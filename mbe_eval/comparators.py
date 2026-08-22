from __future__ import annotations

import math
from itertools import combinations
from typing import Sequence

import numpy as np
import pandas as pd
from scipy.stats import kendalltau, norm

from .crossfit import _fold_ids, _rank_train_test
from .orthogonal import _nuisance_design, _predict_nuisance


def kendall_rank_correlation(values: Sequence[float], target: Sequence[float]) -> float:
    """Return Kendall's tau-b, including tie correction."""
    result = kendalltau(np.asarray(values, dtype=float), np.asarray(target, dtype=float))
    return float(result.statistic)


def _configuration_frame(
    df: pd.DataFrame,
    metric: str,
    target: str,
    hyperparameters: Sequence[str],
    group_col: str | None,
) -> pd.DataFrame:
    required = [metric, target, *hyperparameters]
    if group_col:
        required.append(group_col)
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError(f"missing required columns: {', '.join(missing)}")
    clean = df[required].replace([np.inf, -np.inf], np.nan).dropna().copy()
    if group_col:
        inconsistent = clean.groupby(group_col, sort=False)[list(hyperparameters)].nunique()
        if (inconsistent > 1).any(axis=None):
            raise ValueError("each configuration group must have fixed hyperparameters")
        aggregations = {metric: "mean", target: "mean"}
        aggregations.update({column: "first" for column in hyperparameters})
        clean = clean.groupby(group_col, sort=True, as_index=False).agg(aggregations)
    return clean.reset_index(drop=True)


def granulated_kendall(
    df: pd.DataFrame,
    metric: str,
    target: str,
    hyperparameters: Sequence[str],
    *,
    group_col: str | None = None,
    minimum_axis_levels: int = 2,
) -> tuple[float, pd.DataFrame]:
    """Compute Jiang et al.'s granulated Kendall coefficient."""
    hyperparameters = list(dict.fromkeys(hyperparameters))
    if not hyperparameters:
        raise ValueError("at least one hyperparameter is required")
    frame = _configuration_frame(df, metric, target, hyperparameters, group_col)
    rows: list[dict[str, float | int | str]] = []
    for axis in hyperparameters:
        held_fixed = [column for column in hyperparameters if column != axis]
        grouped = [("all", frame)] if not held_fixed else frame.groupby(held_fixed, dropna=False)
        cell_values: list[float] = []
        eligible = 0
        for _, cell in grouped:
            if cell[axis].nunique() < minimum_axis_levels:
                continue
            eligible += 1
            value = kendall_rank_correlation(cell[metric], cell[target])
            if np.isfinite(value):
                cell_values.append(value)
        axis_value = float(np.mean(cell_values)) if cell_values else math.nan
        rows.append(
            {
                "hyperparameter": axis,
                "granulated_kendall": axis_value,
                "eligible_cells": eligible,
                "finite_cells": len(cell_values),
            }
        )
    detail = pd.DataFrame(rows)
    finite = detail["granulated_kendall"].dropna().to_numpy(dtype=float)
    overall = float(np.mean(finite)) if len(finite) else math.nan
    return overall, detail


def _conditional_information(
    metric_order: np.ndarray,
    target_order: np.ndarray,
    condition_codes: np.ndarray,
) -> tuple[float, float, int]:
    condition_codes = np.asarray(condition_codes, dtype=int)
    condition_count = int(condition_codes.max()) + 1
    categories = metric_order.astype(int) * 2 + target_order.astype(int)
    counts = np.bincount(
        condition_codes * 4 + categories,
        minlength=condition_count * 4,
    ).reshape(condition_count, 2, 2).astype(float)
    condition_totals = counts.sum(axis=(1, 2))
    metric_totals = counts.sum(axis=2)
    target_totals = counts.sum(axis=1)
    total = float(condition_totals.sum())

    mutual_information = 0.0
    for metric_value in range(2):
        for target_value in range(2):
            joint = counts[:, metric_value, target_value]
            denominator = metric_totals[:, metric_value] * target_totals[:, target_value]
            valid = (joint > 0) & (denominator > 0)
            mutual_information += float(
                np.sum(
                    joint[valid]
                    / total
                    * np.log(joint[valid] * condition_totals[valid] / denominator[valid])
                )
            )

    conditional_entropy = 0.0
    for target_value in range(2):
        count = target_totals[:, target_value]
        valid = count > 0
        conditional_entropy -= float(
            np.sum(count[valid] / total * np.log(count[valid] / condition_totals[valid]))
        )
    return mutual_information, conditional_entropy, condition_count


def jiang_normalized_cmi(
    df: pd.DataFrame,
    metric: str,
    target: str,
    hyperparameters: Sequence[str],
    *,
    group_col: str | None = None,
    max_conditioning: int = 2,
) -> tuple[float, pd.DataFrame]:
    """Compute the pairwise normalized CMI criterion of Jiang et al. (2020)."""
    hyperparameters = list(dict.fromkeys(hyperparameters))
    if not hyperparameters:
        raise ValueError("at least one hyperparameter is required")
    if max_conditioning < 0:
        raise ValueError("max_conditioning must be nonnegative")
    frame = _configuration_frame(df, metric, target, hyperparameters, group_col)
    if len(frame) < 3:
        raise ValueError("Jiang CMI requires at least three configurations")

    left, right = np.where(~np.eye(len(frame), dtype=bool))
    metric_values = frame[metric].to_numpy(dtype=float)
    target_values = frame[target].to_numpy(dtype=float)
    metric_order = metric_values[left] > metric_values[right]
    target_order = target_values[left] > target_values[right]

    rows: list[dict[str, float | int | str]] = []
    maximum = min(max_conditioning, len(hyperparameters))
    for size in range(maximum + 1):
        for subset in combinations(hyperparameters, size):
            if not subset:
                codes = np.zeros(len(left), dtype=int)
            else:
                condition = pd.DataFrame(
                    {f"a:{column}": frame[column].to_numpy()[left] for column in subset}
                    | {f"b:{column}": frame[column].to_numpy()[right] for column in subset}
                )
                codes = pd.MultiIndex.from_frame(condition).factorize()[0]
            information, entropy, conditions = _conditional_information(
                metric_order, target_order, codes
            )
            normalized = information / entropy if entropy > 1e-15 else math.nan
            rows.append(
                {
                    "conditioning": ",".join(subset) if subset else "none",
                    "conditioning_size": size,
                    "normalized_cmi": normalized,
                    "conditional_mutual_information": information,
                    "target_conditional_entropy": entropy,
                    "conditions": conditions,
                    "ordered_pairs": len(left),
                }
            )
    detail = pd.DataFrame(rows)
    finite = detail["normalized_cmi"].dropna().to_numpy(dtype=float)
    score = float(np.min(finite)) if len(finite) else math.nan
    return score, detail


def _normal_score_test(values: np.ndarray) -> tuple[float, float, float]:
    values = np.asarray(values, dtype=float)
    mean = float(np.mean(values))
    standard_deviation = float(np.std(values, ddof=1))
    standard_error = standard_deviation / math.sqrt(len(values))
    if standard_error <= 0 or not np.isfinite(standard_error):
        return mean, math.nan, math.nan
    statistic = mean / standard_error
    p_value = float(2.0 * norm.sf(abs(statistic)))
    return mean, float(statistic), p_value


def cross_fitted_rank_residuals(
    df: pd.DataFrame,
    metric: str,
    target: str,
    controls: Sequence[str],
    *,
    group_col: str,
    n_splits: int = 5,
    degree: int = 2,
    ridge: float = 0.1,
    nuisance_model: str = "polynomial_ridge_interactions",
    seed: int = 0,
) -> pd.DataFrame:
    """Return fold-local rank residuals for two responses.

    The function is a comparator building block. It does not perform inference
    and it preserves the independent-unit identifier for downstream tests.
    """
    controls = list(dict.fromkeys(c for c in controls if c not in {metric, target}))
    required = list(dict.fromkeys([metric, target, *controls, group_col]))
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError(f"missing required columns: {', '.join(missing)}")
    clean = (
        df[required]
        .replace([np.inf, -np.inf], np.nan)
        .dropna()
        .reset_index(drop=True)
    )
    if len(clean) < 8 or clean[group_col].nunique() < 8:
        raise ValueError("cross-fitted residuals require at least eight independent groups")
    fold_ids = _fold_ids(clean, n_splits, seed, group_col)
    metric_values = clean[metric].to_numpy(dtype=float)
    target_values = clean[target].to_numpy(dtype=float)
    metric_residual = np.full(len(clean), np.nan, dtype=float)
    target_residual = np.full(len(clean), np.nan, dtype=float)

    for fold in np.unique(fold_ids):
        test_idx = np.flatnonzero(fold_ids == fold)
        train_idx = np.flatnonzero(fold_ids != fold)
        train = clean.iloc[train_idx]
        test = clean.iloc[test_idx]
        x_train, x_test = _nuisance_design(
            train, test, controls, nuisance_model, degree
        )
        metric_train, metric_test = _rank_train_test(
            metric_values[train_idx], metric_values[test_idx]
        )
        target_train, target_test = _rank_train_test(
            target_values[train_idx], target_values[test_idx]
        )
        model_seed = int(seed) + int(fold) * 10_007
        metric_prediction = _predict_nuisance(
            x_train, metric_train, x_test, nuisance_model, ridge, model_seed
        )
        target_prediction = _predict_nuisance(
            x_train, target_train, x_test, nuisance_model, ridge, model_seed + 1
        )
        metric_residual[test_idx] = metric_test - metric_prediction
        target_residual[test_idx] = target_test - target_prediction

    return pd.DataFrame(
        {
            "group": clean[group_col].astype(str),
            "metric_residual": metric_residual,
            "target_residual": target_residual,
        }
    )


def gcm_rank_test(
    df: pd.DataFrame,
    metric: str,
    target: str,
    controls: Sequence[str],
    *,
    group_col: str,
    n_splits: int = 5,
    degree: int = 2,
    ridge: float = 0.1,
    nuisance_model: str = "polynomial_ridge_interactions",
    seed: int = 0,
) -> dict[str, float | int | str]:
    residuals = cross_fitted_rank_residuals(
        df,
        metric,
        target,
        controls,
        group_col=group_col,
        n_splits=n_splits,
        degree=degree,
        ridge=ridge,
        nuisance_model=nuisance_model,
        seed=seed,
    )
    grouped = residuals.groupby("group", sort=True).mean(numeric_only=True)
    scores = (
        grouped["metric_residual"] * grouped["target_residual"]
    ).to_numpy(dtype=float)
    mean, statistic, p_value = _normal_score_test(scores)
    return {
        "method": "gcm_rank_crossfit",
        "estimand": "cross-fitted conditional rank covariance",
        "n_groups": int(len(grouped)),
        "score_mean": mean,
        "statistic": statistic,
        "p_value": p_value,
    }


def wgcm_est_rank_test(
    df: pd.DataFrame,
    metric: str,
    target: str,
    controls: Sequence[str],
    *,
    group_col: str,
    weight_fraction: float = 0.30,
    n_splits: int = 5,
    degree: int = 2,
    ridge: float = 0.1,
    nuisance_model: str = "polynomial_ridge_interactions",
    seed: int = 0,
) -> dict[str, float | int | str]:
    """Single-split estimated-weight GCM on fold-local rank residuals.

    Following WGCM.est, an independent auxiliary split estimates
    ``sign(E[residual_metric * residual_target | controls])``. The weighted
    covariance statistic is evaluated only on the held-out main split.
    """
    if not 0.15 <= weight_fraction <= 0.50:
        raise ValueError("weight_fraction must lie between 0.15 and 0.50")
    groups = np.asarray(sorted(df[group_col].astype(str).unique()))
    if len(groups) < 20:
        raise ValueError("WGCM.est requires at least 20 independent groups")
    rng = np.random.default_rng(seed)
    rng.shuffle(groups)
    auxiliary_count = max(8, int(round(weight_fraction * len(groups))))
    auxiliary_groups = set(groups[:auxiliary_count])
    group_values = df[group_col].astype(str)
    auxiliary = df.loc[group_values.isin(auxiliary_groups)].copy()
    main = df.loc[~group_values.isin(auxiliary_groups)].copy()

    auxiliary_residuals = cross_fitted_rank_residuals(
        auxiliary,
        metric,
        target,
        controls,
        group_col=group_col,
        n_splits=min(3, auxiliary_count),
        degree=degree,
        ridge=ridge,
        nuisance_model=nuisance_model,
        seed=seed + 101,
    )
    auxiliary_scores = auxiliary_residuals.assign(
        score=lambda frame: frame["metric_residual"] * frame["target_residual"]
    )
    score_by_group = auxiliary_scores.groupby("group", sort=True)["score"].mean()
    auxiliary = auxiliary.copy()
    auxiliary["weight_response"] = auxiliary[group_col].astype(str).map(score_by_group)
    auxiliary_grouped = auxiliary.groupby(group_col, sort=True, as_index=False).first()
    main_grouped = main.groupby(group_col, sort=True, as_index=False).first()
    x_auxiliary, x_main = _nuisance_design(
        auxiliary_grouped,
        main_grouped,
        list(controls),
        nuisance_model,
        degree,
    )
    weight_prediction = _predict_nuisance(
        x_auxiliary,
        auxiliary_grouped["weight_response"].to_numpy(dtype=float),
        x_main,
        nuisance_model,
        ridge,
        seed + 307,
    )
    weights = np.sign(weight_prediction)

    main_residuals = cross_fitted_rank_residuals(
        main,
        metric,
        target,
        controls,
        group_col=group_col,
        n_splits=min(n_splits, len(main_grouped)),
        degree=degree,
        ridge=ridge,
        nuisance_model=nuisance_model,
        seed=seed + 503,
    )
    grouped = main_residuals.groupby("group", sort=True).mean(numeric_only=True)
    weight_map = dict(zip(main_grouped[group_col].astype(str), weights, strict=True))
    ordered_weights = grouped.index.to_series().map(weight_map).to_numpy(dtype=float)
    scores = (
        grouped["metric_residual"].to_numpy(dtype=float)
        * grouped["target_residual"].to_numpy(dtype=float)
        * ordered_weights
    )
    mean, statistic, p_value = _normal_score_test(scores)
    return {
        "method": "wgcm_est_rank_crossfit",
        "estimand": "weighted cross-fitted conditional rank covariance",
        "n_groups": int(len(grouped)),
        "weight_groups": int(auxiliary_count),
        "weight_fraction": float(weight_fraction),
        "score_mean": mean,
        "statistic": statistic,
        "p_value": p_value,
    }


__all__ = [
    "cross_fitted_rank_residuals",
    "gcm_rank_test",
    "granulated_kendall",
    "jiang_normalized_cmi",
    "kendall_rank_correlation",
    "wgcm_est_rank_test",
]
