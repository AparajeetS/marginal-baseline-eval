from __future__ import annotations

import math
from typing import Sequence

import numpy as np
import pandas as pd
from scipy.stats import t as student_t

from .crossfit import (
    _design_train_test,
    _extra_trees_predict,
    _fold_ids,
    _pairwise_interactions,
    _rank_train_test,
    _ridge_fit,
)


_NUISANCE_MODELS = {
    "polynomial_ridge",
    "polynomial_ridge_interactions",
    "extra_trees",
}


def _nuisance_design(
    train: pd.DataFrame,
    test: pd.DataFrame,
    controls: Sequence[str],
    nuisance_model: str,
    degree: int,
) -> tuple[np.ndarray, np.ndarray]:
    design_degree = degree if nuisance_model != "extra_trees" else 1
    x_train, x_test = _design_train_test(
        train, test, controls, design_degree
    )
    if nuisance_model != "polynomial_ridge_interactions":
        return x_train, x_test

    interaction_train, interaction_test = _design_train_test(
        train, test, controls, 1
    )
    train_blocks, test_blocks = _pairwise_interactions(
        interaction_train, interaction_test
    )
    if train_blocks:
        x_train = np.column_stack([x_train, *train_blocks])
        x_test = np.column_stack([x_test, *test_blocks])
    return x_train, x_test


def _predict_nuisance(
    x_train: np.ndarray,
    response_train: np.ndarray,
    x_test: np.ndarray,
    nuisance_model: str,
    ridge: float,
    seed: int,
) -> np.ndarray:
    if nuisance_model == "extra_trees":
        return _extra_trees_predict(x_train, response_train, x_test, seed)
    coefficients = _ridge_fit(x_train, response_train, ridge)
    return x_test @ coefficients


def _studentized_mean(values: np.ndarray) -> tuple[float, float, float]:
    count = len(values)
    mean = float(np.mean(values))
    standard_deviation = float(np.std(values, ddof=1))
    standard_error = standard_deviation / math.sqrt(count)
    if standard_error <= 0 or not np.isfinite(standard_error):
        return mean, math.nan, math.nan
    statistic = mean / standard_error
    p_value = float(2.0 * student_t.sf(abs(statistic), df=count - 1))
    return mean, float(statistic), p_value


def _clustered_standard_error(values: np.ndarray, blocks: np.ndarray) -> float:
    """Return a finite-sample-corrected cluster-robust SE for a mean."""

    values = np.asarray(values, dtype=float)
    blocks = np.asarray(blocks)
    unique_blocks, inverse = np.unique(blocks, return_inverse=True)
    if len(unique_blocks) < 2:
        return math.nan
    centered = values - np.mean(values)
    cluster_sums = np.bincount(inverse, weights=centered)
    variance = (
        len(unique_blocks)
        / (len(unique_blocks) - 1)
        * float(np.sum(np.square(cluster_sums)))
        / (len(values) ** 2)
    )
    return float(math.sqrt(max(0.0, variance)))


def _clustered_studentized_mean(
    values: np.ndarray, blocks: np.ndarray
) -> tuple[float, float, float]:
    mean = float(np.mean(values))
    standard_error = _clustered_standard_error(values, blocks)
    block_count = len(np.unique(blocks))
    if standard_error <= 0 or not np.isfinite(standard_error):
        return mean, math.nan, math.nan
    statistic = mean / standard_error
    p_value = float(2.0 * student_t.sf(abs(statistic), df=block_count - 1))
    return mean, float(statistic), p_value


def _wild_studentized_p_value(
    values: np.ndarray,
    observed_t: float,
    draws: int,
    seed: int,
    blocks: np.ndarray | None = None,
) -> float:
    if draws < 1 or not np.isfinite(observed_t):
        return math.nan
    centered = values - np.mean(values)
    rng = np.random.default_rng(seed)
    if blocks is None:
        signs = rng.choice(np.array([-1.0, 1.0]), size=(draws, len(values)))
    else:
        unique_blocks, inverse = np.unique(blocks, return_inverse=True)
        if len(unique_blocks) < 2:
            return math.nan
        block_signs = rng.choice(
            np.array([-1.0, 1.0]), size=(draws, len(unique_blocks))
        )
        signs = block_signs[:, inverse]
    bootstrap = signs * centered
    means = np.mean(bootstrap, axis=1)
    if blocks is None:
        standard_errors = np.std(bootstrap, axis=1, ddof=1) / math.sqrt(len(values))
    else:
        bootstrap_centered = bootstrap - means[:, None]
        cluster_sums = np.column_stack(
            [
                bootstrap_centered[:, inverse == index].sum(axis=1)
                for index in range(len(unique_blocks))
            ]
        )
        standard_errors = np.sqrt(
            len(unique_blocks)
            / (len(unique_blocks) - 1)
            * np.sum(np.square(cluster_sums), axis=1)
            / (len(values) ** 2)
        )
    valid = np.isfinite(standard_errors) & (standard_errors > 0)
    if not valid.any():
        return math.nan
    bootstrap_t = np.abs(means[valid] / standard_errors[valid])
    exceedances = int(np.count_nonzero(bootstrap_t >= abs(observed_t)))
    return float((exceedances + 1) / (len(bootstrap_t) + 1))


def orthogonal_score_audit(
    df: pd.DataFrame,
    metric: str,
    target: str,
    controls: Sequence[str],
    *,
    group_col: str,
    permutation_block_col: str | None = None,
    n_splits: int = 5,
    degree: int = 4,
    ridge: float = 1e-3,
    nuisance_model: str = "polynomial_ridge",
    wild_draws: int = 999,
    seed: int = 0,
    alpha: float = 0.05,
) -> dict[str, float | int | str]:
    """Test a cross-fitted conditional rank-covariance score.

    Metric and target ranks are separately residualized against the controls
    with grouped cross-fitting. Inference uses the mean residual product at the
    independent-group level. The primary p-value is a studentized Rademacher
    multiplier bootstrap over those groups. When ``permutation_block_col`` is
    supplied, standard errors use block clusters and each block receives one
    multiplier per draw.

    This estimates conditional rank covariance, not causal effect or arbitrary
    conditional dependence. It deliberately remains separate from MBE's
    learner-relative predictive-gain estimand.
    """
    if not group_col:
        raise ValueError("group_col is required for independent-unit inference")
    if n_splits < 2:
        raise ValueError("n_splits must be at least 2")
    if degree < 1:
        raise ValueError("degree must be at least 1")
    if ridge < 0:
        raise ValueError("ridge must be non-negative")
    if wild_draws < 1:
        raise ValueError("wild_draws must be at least 1")
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must lie strictly between zero and one")
    if nuisance_model not in _NUISANCE_MODELS:
        choices = ", ".join(sorted(_NUISANCE_MODELS))
        raise ValueError(f"nuisance_model must be one of: {choices}")

    controls = list(dict.fromkeys(c for c in controls if c not in {metric, target}))
    required = [metric, target, *controls, group_col]
    if permutation_block_col:
        required.append(permutation_block_col)
    required = list(dict.fromkeys(required))
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError(f"missing required columns: {', '.join(missing)}")

    clean = (
        df[required]
        .replace([np.inf, -np.inf], np.nan)
        .dropna()
        .reset_index(drop=True)
    )
    if len(clean) < max(20, n_splits * 3):
        raise ValueError("orthogonal score audit requires at least 20 complete rows")

    group_sizes = clean.groupby(group_col, sort=True).size()
    if len(group_sizes) < max(8, n_splits):
        raise ValueError("orthogonal score audit requires at least eight groups")
    if group_sizes.nunique() != 1:
        raise ValueError("group_col must define balanced independent groups")
    if permutation_block_col:
        block_counts = clean.groupby(group_col, sort=True)[
            permutation_block_col
        ].nunique()
        if (block_counts > 1).any():
            raise ValueError("each inference group must belong to one permutation block")
        if clean[permutation_block_col].nunique() < 2:
            raise ValueError("permutation_block_col must contain at least two blocks")

    fold_ids = _fold_ids(clean, n_splits, seed, group_col)
    target_values = clean[target].to_numpy(dtype=float)
    metric_values = clean[metric].to_numpy(dtype=float)
    target_rank = np.full(len(clean), np.nan, dtype=float)
    metric_rank = np.full(len(clean), np.nan, dtype=float)
    target_prediction = np.full(len(clean), np.nan, dtype=float)
    metric_prediction = np.full(len(clean), np.nan, dtype=float)

    for fold in np.unique(fold_ids):
        test_idx = np.flatnonzero(fold_ids == fold)
        train_idx = np.flatnonzero(fold_ids != fold)
        train = clean.iloc[train_idx]
        test = clean.iloc[test_idx]
        x_train, x_test = _nuisance_design(
            train, test, controls, nuisance_model, degree
        )
        target_train_rank, target_test_rank = _rank_train_test(
            target_values[train_idx], target_values[test_idx]
        )
        metric_train_rank, metric_test_rank = _rank_train_test(
            metric_values[train_idx], metric_values[test_idx]
        )
        model_seed = int(seed) + int(fold) * 10_007
        target_prediction[test_idx] = _predict_nuisance(
            x_train,
            target_train_rank,
            x_test,
            nuisance_model,
            ridge,
            model_seed,
        )
        metric_prediction[test_idx] = _predict_nuisance(
            x_train,
            metric_train_rank,
            x_test,
            nuisance_model,
            ridge,
            model_seed + 1,
        )
        target_rank[test_idx] = target_test_rank
        metric_rank[test_idx] = metric_test_rank

    target_residual = target_rank - target_prediction
    metric_residual = metric_rank - metric_prediction
    residual_frame = pd.DataFrame(
        {
            "group": clean[group_col].astype(str),
            "metric_residual": metric_residual,
            "target_residual": target_residual,
        }
    )
    if permutation_block_col:
        residual_frame["block"] = clean[permutation_block_col].astype(str)
    grouped = residual_frame.groupby("group", sort=True).mean(numeric_only=True)
    grouped["score"] = grouped["metric_residual"] * grouped["target_residual"]
    grouped["metric_energy"] = np.square(grouped["metric_residual"])
    grouped["target_error"] = np.square(grouped["target_residual"])
    group_scores = grouped["score"].to_numpy(dtype=float)
    block_labels = None
    if permutation_block_col:
        block_labels = (
            residual_frame.groupby("group", sort=True)["block"].first().to_numpy()
        )
        score_mean, score_t, student_p = _clustered_studentized_mean(
            group_scores, block_labels
        )
    else:
        score_mean, score_t, student_p = _studentized_mean(group_scores)
    wild_p = _wild_studentized_p_value(
        group_scores,
        score_t,
        wild_draws,
        int(seed) + 4_000_003,
        block_labels,
    )

    mean_metric_energy = float(grouped["metric_energy"].mean())
    slope = score_mean / mean_metric_energy if mean_metric_energy > 0 else math.nan
    influence = group_scores - slope * grouped["metric_energy"].to_numpy(dtype=float)
    if mean_metric_energy > 0:
        influence_se = (
            _clustered_standard_error(influence, block_labels)
            if block_labels is not None
            else float(np.std(influence, ddof=1)) / math.sqrt(len(grouped))
        )
        slope_se = influence_se / mean_metric_energy
    else:
        slope_se = math.nan
    inference_df = (
        len(np.unique(block_labels)) - 1
        if block_labels is not None
        else len(grouped) - 1
    )
    critical = float(student_t.ppf(1.0 - alpha / 2.0, df=inference_df))
    slope_ci_low = slope - critical * slope_se
    slope_ci_high = slope + critical * slope_se

    if np.isfinite(wild_p) and wild_p <= alpha and score_mean > 0:
        classification = "supported-positive-conditional-rank-signal"
    elif np.isfinite(wild_p) and wild_p <= alpha and score_mean < 0:
        classification = "supported-negative-conditional-rank-signal"
    else:
        classification = "no-supported-conditional-rank-signal"

    n_blocks = 0
    if permutation_block_col:
        n_blocks = int(clean[permutation_block_col].nunique())

    return {
        "metric": metric,
        "target": target,
        "n": int(len(clean)),
        "n_groups": int(len(grouped)),
        "rows_per_group": int(group_sizes.iloc[0]),
        "n_blocks": n_blocks,
        "n_splits": int(len(np.unique(fold_ids))),
        "degree": int(degree),
        "ridge": float(ridge),
        "nuisance_model": nuisance_model,
        "wild_draws": int(wild_draws),
        "orthogonal_score_mean": score_mean,
        "orthogonal_score_t": score_t,
        "orthogonal_student_p": student_p,
        "orthogonal_wild_p": wild_p,
        "partial_rank_slope": float(slope),
        "partial_rank_slope_se": float(slope_se),
        "partial_rank_slope_ci_low": float(slope_ci_low),
        "partial_rank_slope_ci_high": float(slope_ci_high),
        "baseline_rank_mse": float(grouped["target_error"].mean()),
        "classification": classification,
        "estimand": "cross-fitted conditional rank covariance",
        "inference_unit": group_col,
        "inference_block": permutation_block_col or "none",
        "score_aggregation": "product-of-group-mean-residuals",
    }


def repeated_split_orthogonal_audit(
    df: pd.DataFrame,
    metric: str,
    target: str,
    controls: Sequence[str],
    *,
    group_col: str,
    permutation_block_col: str | None = None,
    n_splits: int = 5,
    degree: int = 4,
    ridge: float = 1e-3,
    nuisance_model: str = "polynomial_ridge",
    wild_draws: int = 999,
    repeats: int = 3,
    seed: int = 0,
    seed_stride: int = 10_007,
    alpha: float = 0.05,
) -> dict[str, float | int | str | bool]:
    """Apply an intersection rule across independent grouped cross-fit splits.

    This is a deliberately conservative stability diagnostic. It does not pool
    split-specific p-values or create a new aggregate p-value: a positive
    conclusion requires a positive, significant wild-bootstrap score in every
    repeat. Its calibration and power must therefore be established empirically
    for the intended design.
    """
    if repeats < 2:
        raise ValueError("repeats must be at least two")
    if seed_stride < 1:
        raise ValueError("seed_stride must be positive")

    results = []
    for repeat in range(repeats):
        split_seed = int(seed) + repeat * int(seed_stride)
        result = orthogonal_score_audit(
            df,
            metric,
            target,
            controls,
            group_col=group_col,
            permutation_block_col=permutation_block_col,
            n_splits=n_splits,
            degree=degree,
            ridge=ridge,
            nuisance_model=nuisance_model,
            wild_draws=wild_draws,
            seed=split_seed,
            alpha=alpha,
        )
        results.append(result)

    wild_p = np.asarray([row["orthogonal_wild_p"] for row in results], dtype=float)
    score = np.asarray(
        [row["orthogonal_score_mean"] for row in results], dtype=float
    )
    positive = np.isfinite(wild_p) & (wild_p <= alpha) & (score > 0.0)
    stable_positive = bool(positive.all())
    return {
        "metric": metric,
        "target": target,
        "n": int(results[0]["n"]),
        "n_groups": int(results[0]["n_groups"]),
        "rows_per_group": int(results[0]["rows_per_group"]),
        "n_blocks": int(results[0]["n_blocks"]),
        "n_splits": int(results[0]["n_splits"]),
        "degree": int(degree),
        "ridge": float(ridge),
        "nuisance_model": nuisance_model,
        "wild_draws": int(wild_draws),
        "stability_repeats": int(repeats),
        "stability_seed_stride": int(seed_stride),
        "stability_rule": "positive_wild_support_in_every_split",
        "stability_alpha": float(alpha),
        "stable_positive": stable_positive,
        "positive_split_count": int(positive.sum()),
        "minimum_orthogonal_score_mean": float(np.nanmin(score)),
        "median_orthogonal_score_mean": float(np.nanmedian(score)),
        "maximum_orthogonal_wild_p": float(np.nanmax(wild_p)),
        "minimum_orthogonal_wild_p": float(np.nanmin(wild_p)),
        "classification": (
            "stable-positive-conditional-rank-signal"
            if stable_positive
            else "no-stable-positive-conditional-rank-signal"
        ),
        "estimand": "cross-fitted conditional rank covariance",
        "inference_unit": group_col,
        "score_aggregation": "intersection-across-grouped-crossfit-splits",
    }
