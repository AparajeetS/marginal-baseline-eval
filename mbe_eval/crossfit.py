from __future__ import annotations

import math
from typing import Sequence

import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype


def _ridge_fit(x: np.ndarray, y: np.ndarray, alpha: float) -> np.ndarray:
    penalty = np.eye(x.shape[1], dtype=float) * alpha
    penalty[0, 0] = 0.0
    return np.linalg.pinv(x.T @ x + penalty) @ x.T @ y


def _extra_trees_predict(
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_test: np.ndarray,
    seed: int,
) -> np.ndarray:
    try:
        from sklearn.ensemble import ExtraTreesRegressor
    except ImportError as exc:  # pragma: no cover - depends on optional extra
        raise ImportError(
            "extra_trees nuisance adjustment requires scikit-learn; "
            "install mbe-eval[flexible]"
        ) from exc
    model = ExtraTreesRegressor(
        n_estimators=128,
        min_samples_leaf=5,
        max_features=1.0,
        random_state=seed,
        n_jobs=1,
    )
    model.fit(x_train, y_train)
    return model.predict(x_test)


def _numeric_block(
    train: pd.Series,
    test: pd.Series,
    degree: int,
) -> tuple[list[np.ndarray], list[np.ndarray]]:
    train_values = train.to_numpy(dtype=float)
    test_values = test.to_numpy(dtype=float)
    train_rank, test_rank = _rank_train_test(train_values, test_values)
    train_z = 2.0 * train_rank - 1.0
    test_z = 2.0 * test_rank - 1.0
    return (
        [np.power(train_z, power) for power in range(1, degree + 1)],
        [np.power(test_z, power) for power in range(1, degree + 1)],
    )


def _design_train_test(
    train: pd.DataFrame,
    test: pd.DataFrame,
    controls: Sequence[str],
    degree: int,
) -> tuple[np.ndarray, np.ndarray]:
    train_blocks: list[np.ndarray] = [np.ones(len(train), dtype=float)]
    test_blocks: list[np.ndarray] = [np.ones(len(test), dtype=float)]

    for control in controls:
        if is_numeric_dtype(train[control]):
            train_numeric, test_numeric = _numeric_block(
                train[control].astype(float),
                test[control].astype(float),
                degree,
            )
            train_blocks.extend(train_numeric)
            test_blocks.extend(test_numeric)
            continue

        train_values = train[control].astype(str)
        test_values = test[control].astype(str)
        levels = sorted(train_values.unique().tolist())
        for level in levels[1:]:
            train_blocks.append((train_values == level).to_numpy(dtype=float))
            test_blocks.append((test_values == level).to_numpy(dtype=float))

    return np.column_stack(train_blocks), np.column_stack(test_blocks)


def _pairwise_interactions(
    train: np.ndarray,
    test: np.ndarray,
) -> tuple[list[np.ndarray], list[np.ndarray]]:
    train_blocks: list[np.ndarray] = []
    test_blocks: list[np.ndarray] = []
    for left in range(1, train.shape[1]):
        for right in range(left + 1, train.shape[1]):
            train_blocks.append(train[:, left] * train[:, right])
            test_blocks.append(test[:, left] * test[:, right])
    return train_blocks, test_blocks


def _fold_ids(
    df: pd.DataFrame,
    n_splits: int,
    seed: int,
    group_col: str | None,
) -> np.ndarray:
    rng = np.random.default_rng(seed)
    folds = np.empty(len(df), dtype=int)

    if group_col:
        groups = df[group_col].astype(str).to_numpy()
        unique_groups = np.unique(groups)
        if len(unique_groups) < 2:
            raise ValueError(f"group column {group_col!r} must contain at least two groups")
        rng.shuffle(unique_groups)
        split_count = min(n_splits, len(unique_groups))
        mapping = {group: i % split_count for i, group in enumerate(unique_groups)}
        return np.asarray([mapping[group] for group in groups], dtype=int)

    order = rng.permutation(len(df))
    split_count = min(n_splits, len(df))
    folds[order] = np.arange(len(df)) % split_count
    return folds


def _rank_correlation(a: np.ndarray, b: np.ndarray) -> float:
    a_rank = pd.Series(a).rank(method="average").to_numpy(dtype=float)
    b_rank = pd.Series(b).rank(method="average").to_numpy(dtype=float)
    if np.std(a_rank) <= 0 or np.std(b_rank) <= 0:
        return math.nan
    return float(np.corrcoef(a_rank, b_rank)[0, 1])


def _rank_train_test(
    train_values: np.ndarray,
    test_values: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Map train and test values to midranks using only the training fold."""
    train_values = np.asarray(train_values, dtype=float)
    test_values = np.asarray(test_values, dtype=float)
    if train_values.size == 0:
        raise ValueError("rank transform requires a non-empty training fold")
    ordered = np.sort(train_values)
    n = len(ordered)

    def transform(values: np.ndarray) -> np.ndarray:
        left = np.searchsorted(ordered, values, side="left")
        right = np.searchsorted(ordered, values, side="right")
        midrank = (left + right + 1.0) / (2.0 * n)
        return np.clip(midrank, 1.0 / n, 1.0)

    return transform(train_values), transform(test_values)


def _permutation_p_value(
    values: np.ndarray,
    target: np.ndarray,
    observed: float,
    permutations: int,
    rng: np.random.Generator,
    groups: np.ndarray | None,
) -> float:
    """Vectorized two-sided rank-permutation test.

    Permuting values does not change their global ranks, so ranking once is
    exactly equivalent to calling Spearman correlation after every shuffle.
    Group permutations are generated as one matrix to avoid a Python loop over
    groups for every replicate.
    """

    value_rank = pd.Series(values).rank(method="average").to_numpy(dtype=float)
    target_rank = pd.Series(target).rank(method="average").to_numpy(dtype=float)
    value_centered = value_rank - np.mean(value_rank)
    target_centered = target_rank - np.mean(target_rank)
    denominator = float(
        np.sqrt(np.sum(np.square(value_centered)) * np.sum(np.square(target_centered)))
    )
    if denominator <= 0 or not np.isfinite(observed):
        return math.nan

    permuted = np.empty((permutations, len(values)), dtype=float)
    if groups is None:
        order = np.argsort(rng.random((permutations, len(values))), axis=1)
        permuted[:] = value_rank[order]
    else:
        for group in np.unique(groups):
            idx = np.flatnonzero(groups == group)
            order = np.argsort(rng.random((permutations, len(idx))), axis=1)
            permuted[:, idx] = value_rank[idx][order]

    permuted_r = (permuted @ target_centered) / denominator
    exceedances = int(np.count_nonzero(np.abs(permuted_r) >= abs(observed)))
    return float((exceedances + 1) / (permutations + 1))


def classify_increment_evidence(
    residual_p: float,
    delta_mse_ci_low: float,
    *,
    alpha: float = 0.05,
    minimum_delta_mse: float = 0.0,
) -> str:
    """Keep residual dependence and predictive improvement logically separate."""
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must lie strictly between zero and one")
    residual_supported = np.isfinite(residual_p) and residual_p <= alpha
    predictive_supported = (
        np.isfinite(delta_mse_ci_low) and delta_mse_ci_low > minimum_delta_mse
    )
    if residual_supported and predictive_supported:
        return "increment-supported"
    if residual_supported:
        return "residual-dependence-only"
    if predictive_supported:
        return "predictive-improvement-only"
    return "no-supported-increment"


def classify_predictive_increment(
    delta_mse_ci_low: float,
    *,
    minimum_delta_mse: float = 0.0,
) -> str:
    """Classify learner-relative increment from a full-refit lower interval."""
    if not np.isfinite(delta_mse_ci_low):
        return "insufficient-inference"
    if delta_mse_ci_low > minimum_delta_mse:
        return "increment-supported"
    return "no-supported-increment"


def cross_fitted_audit(
    df: pd.DataFrame,
    metric: str,
    target: str,
    controls: Sequence[str],
    *,
    group_col: str | None = None,
    permutation_block_col: str | None = None,
    n_splits: int = 5,
    degree: int = 2,
    ridge: float = 1e-3,
    nuisance_model: str = "polynomial_ridge",
    permutations: int = 0,
    bootstrap: int = 0,
    seed: int = 0,
) -> dict[str, float | int | str]:
    """Estimate incremental metric signal with grouped cross-fitting.

    Numeric controls are mapped through a training-fold empirical CDF and
    expanded into a bounded polynomial basis. Categorical controls are one-hot
    encoded from training-fold levels. The function reports out-of-fold
    residual dependence and the change
    in target mean-squared error from adding the metric to the baseline model.

    This is a compact reference implementation for protocol calibration. It is
    not a causal estimator and does not select the control set for the user.
    """

    if n_splits < 2:
        raise ValueError("n_splits must be at least 2")
    if degree < 1:
        raise ValueError("degree must be at least 1")
    if nuisance_model not in {
        "polynomial_ridge",
        "polynomial_ridge_interactions",
        "extra_trees",
    }:
        raise ValueError(
            "nuisance_model must be 'polynomial_ridge', "
            "'polynomial_ridge_interactions', or 'extra_trees'"
        )

    controls = list(dict.fromkeys(c for c in controls if c not in {metric, target}))
    required = [metric, target, *controls]
    if group_col:
        required.append(group_col)
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
        raise ValueError("cross-fitted audit requires at least 20 complete rows")

    fold_ids = _fold_ids(clean, n_splits, seed, group_col)
    target_values = clean[target].to_numpy(dtype=float)
    metric_values = clean[metric].to_numpy(dtype=float)
    target_rank = np.full(len(clean), np.nan, dtype=float)
    metric_rank = np.full(len(clean), np.nan, dtype=float)
    target_pred = np.full(len(clean), np.nan, dtype=float)
    metric_pred = np.full(len(clean), np.nan, dtype=float)
    augmented_pred = np.full(len(clean), np.nan, dtype=float)

    for fold in np.unique(fold_ids):
        test_idx = np.flatnonzero(fold_ids == fold)
        train_idx = np.flatnonzero(fold_ids != fold)
        train = clean.iloc[train_idx]
        test = clean.iloc[test_idx]
        design_degree = (
            degree
            if nuisance_model
            in {"polynomial_ridge", "polynomial_ridge_interactions"}
            else 1
        )
        x_train, x_test = _design_train_test(
            train, test, controls, design_degree
        )
        interaction_base_train = None
        interaction_base_test = None
        if nuisance_model == "polynomial_ridge_interactions":
            interaction_base_train, interaction_base_test = _design_train_test(
                train, test, controls, 1
            )
            train_interactions, test_interactions = _pairwise_interactions(
                interaction_base_train, interaction_base_test
            )
            if train_interactions:
                x_train = np.column_stack([x_train, *train_interactions])
                x_test = np.column_stack([x_test, *test_interactions])
        target_train_rank, target_test_rank = _rank_train_test(
            target_values[train_idx], target_values[test_idx]
        )
        metric_train_rank, metric_test_rank = _rank_train_test(
            metric_values[train_idx], metric_values[test_idx]
        )
        if nuisance_model == "polynomial_ridge":
            metric_train_blocks, metric_test_blocks = _numeric_block(
                pd.Series(metric_train_rank),
                pd.Series(metric_test_rank),
                degree,
            )
        else:
            metric_train_blocks = [metric_train_rank]
            metric_test_blocks = [metric_test_rank]
        x_aug_train = np.column_stack([x_train, *metric_train_blocks])
        x_aug_test = np.column_stack([x_test, *metric_test_blocks])
        if nuisance_model == "polynomial_ridge_interactions":
            metric_control_train = [
                metric_train_rank * interaction_base_train[:, column]
                for column in range(1, interaction_base_train.shape[1])
            ]
            metric_control_test = [
                metric_test_rank * interaction_base_test[:, column]
                for column in range(1, interaction_base_test.shape[1])
            ]
            if metric_control_train:
                x_aug_train = np.column_stack(
                    [x_aug_train, *metric_control_train]
                )
                x_aug_test = np.column_stack([x_aug_test, *metric_control_test])

        target_rank[test_idx] = target_test_rank
        metric_rank[test_idx] = metric_test_rank
        if nuisance_model in {
            "polynomial_ridge",
            "polynomial_ridge_interactions",
        }:
            target_beta = _ridge_fit(x_train, target_train_rank, ridge)
            metric_beta = _ridge_fit(x_train, metric_train_rank, ridge)
            augmented_beta = _ridge_fit(x_aug_train, target_train_rank, ridge)
            target_pred[test_idx] = x_test @ target_beta
            metric_pred[test_idx] = x_test @ metric_beta
            augmented_pred[test_idx] = x_aug_test @ augmented_beta
        else:
            model_seed = seed + int(fold) * 10_007
            target_pred[test_idx] = _extra_trees_predict(
                x_train, target_train_rank, x_test, model_seed
            )
            metric_pred[test_idx] = _extra_trees_predict(
                x_train, metric_train_rank, x_test, model_seed + 1
            )
            augmented_pred[test_idx] = _extra_trees_predict(
                x_aug_train, target_train_rank, x_aug_test, model_seed + 2
            )

    target_residual = target_rank - target_pred
    metric_residual = metric_rank - metric_pred
    run_residual_r = _rank_correlation(metric_residual, target_residual)
    baseline_squared_error = np.square(target_rank - target_pred)
    augmented_squared_error = np.square(target_rank - augmented_pred)

    inference_metric = metric_residual
    inference_target = target_residual
    inference_blocks = (
        clean[permutation_block_col].astype(str).to_numpy()
        if permutation_block_col
        else None
    )
    if group_col:
        cluster_frame = pd.DataFrame(
            {
                "group": clean[group_col].astype(str).to_numpy(),
                "metric_residual": metric_residual,
                "target_residual": target_residual,
                "baseline_squared_error": baseline_squared_error,
                "augmented_squared_error": augmented_squared_error,
            }
        )
        if permutation_block_col:
            cluster_frame["block"] = clean[permutation_block_col].astype(str).to_numpy()
            block_counts = cluster_frame.groupby("group", sort=True)["block"].nunique()
            if (block_counts > 1).any():
                raise ValueError(
                    "each inference group must belong to one permutation block"
                )
            inference_blocks = (
                cluster_frame.groupby("group", sort=True)["block"].first().to_numpy()
            )
        cluster = cluster_frame.groupby("group", sort=True).mean(numeric_only=True)
        inference_metric = cluster["metric_residual"].to_numpy(dtype=float)
        inference_target = cluster["target_residual"].to_numpy(dtype=float)
        inference_baseline_error = cluster["baseline_squared_error"].to_numpy(dtype=float)
        inference_augmented_error = cluster["augmented_squared_error"].to_numpy(dtype=float)
    else:
        inference_baseline_error = baseline_squared_error
        inference_augmented_error = augmented_squared_error

    residual_r = _rank_correlation(inference_metric, inference_target)
    baseline_mse = float(np.mean(inference_baseline_error))
    augmented_mse = float(np.mean(inference_augmented_error))

    permutation_p = math.nan
    if permutations > 0:
        rng = np.random.default_rng(seed + 1_000_003)
        permutation_p = _permutation_p_value(
            inference_metric,
            inference_target,
            residual_r,
            permutations,
            rng,
            inference_blocks,
        )

    residual_ci_low = math.nan
    residual_ci_high = math.nan
    delta_mse_ci_low = math.nan
    delta_mse_ci_high = math.nan
    if bootstrap > 0:
        rng = np.random.default_rng(seed + 2_000_003)
        unit_count = len(inference_metric)
        draws = rng.integers(0, unit_count, size=(bootstrap, unit_count))
        metric_rank = pd.Series(inference_metric).rank(method="average").to_numpy(dtype=float)
        target_rank = pd.Series(inference_target).rank(method="average").to_numpy(dtype=float)
        sampled_metric = metric_rank[draws]
        sampled_target = target_rank[draws]
        sampled_metric -= sampled_metric.mean(axis=1, keepdims=True)
        sampled_target -= sampled_target.mean(axis=1, keepdims=True)
        numerators = np.sum(sampled_metric * sampled_target, axis=1)
        denominators = np.sqrt(
            np.sum(np.square(sampled_metric), axis=1)
            * np.sum(np.square(sampled_target), axis=1)
        )
        bootstrap_r = np.divide(
            numerators,
            denominators,
            out=np.full(bootstrap, np.nan, dtype=float),
            where=denominators > 0,
        )
        bootstrap_delta = np.mean(
            inference_baseline_error[draws] - inference_augmented_error[draws],
            axis=1,
        )
        residual_ci_low, residual_ci_high = np.nanquantile(bootstrap_r, [0.025, 0.975])
        delta_mse_ci_low, delta_mse_ci_high = np.nanquantile(
            bootstrap_delta, [0.025, 0.975]
        )

    increment_classification = classify_increment_evidence(
        permutation_p,
        float(delta_mse_ci_low),
    )
    return {
        "metric": metric,
        "target": target,
        "controls": ",".join(controls),
        "group_col": group_col or "",
        "permutation_block_col": permutation_block_col or "",
        "n": len(clean),
        "independence_units": len(inference_metric),
        "n_splits": int(len(np.unique(fold_ids))),
        "polynomial_degree": degree,
        "nuisance_model": nuisance_model,
        "run_residual_r": run_residual_r,
        "residual_r": residual_r,
        "residual_p": permutation_p,
        "residual_ci_low": float(residual_ci_low),
        "residual_ci_high": float(residual_ci_high),
        "baseline_mse": baseline_mse,
        "augmented_mse": augmented_mse,
        "delta_mse": baseline_mse - augmented_mse,
        "delta_mse_ci_low": float(delta_mse_ci_low),
        "delta_mse_ci_high": float(delta_mse_ci_high),
        "relative_mse_improvement": (baseline_mse - augmented_mse) / baseline_mse
        if baseline_mse > 0
        else math.nan,
        "increment_classification": increment_classification,
    }


def repeated_cross_fitted_audit(
    df: pd.DataFrame,
    metric: str,
    target: str,
    controls: Sequence[str],
    *,
    repeats: int = 10,
    seed: int = 0,
    seed_stride: int = 100_003,
    **audit_kwargs: object,
) -> pd.DataFrame:
    """Repeat the full audit across fold assignments without combining p-values."""
    if repeats < 2:
        raise ValueError("repeated cross-fitting requires at least two repeats")
    if "seed" in audit_kwargs:
        raise ValueError("pass the initial seed through the seed argument")
    rows = []
    for repeat in range(repeats):
        split_seed = seed + repeat * seed_stride
        result = cross_fitted_audit(
            df,
            metric,
            target,
            controls,
            seed=split_seed,
            **audit_kwargs,
        )
        rows.append({"repeat": repeat, "split_seed": split_seed, **result})
    return pd.DataFrame(rows)


def refit_bootstrap_audit(
    df: pd.DataFrame,
    metric: str,
    target: str,
    controls: Sequence[str],
    *,
    refit_bootstrap: int = 199,
    permutations: int = 199,
    group_col: str | None = None,
    seed: int = 0,
    **audit_kwargs: object,
) -> dict[str, float | int | str]:
    """Bootstrap independent units and refit the complete audit in every draw."""
    if refit_bootstrap < 20:
        raise ValueError("refit_bootstrap must be at least 20")
    forbidden = {"seed", "bootstrap", "permutations", "group_col"} & audit_kwargs.keys()
    if forbidden:
        raise ValueError(f"pass {', '.join(sorted(forbidden))} as named arguments")

    base = cross_fitted_audit(
        df,
        metric,
        target,
        controls,
        group_col=group_col,
        permutations=permutations,
        bootstrap=0,
        seed=seed,
        **audit_kwargs,
    )
    rng = np.random.default_rng(seed + 3_000_003)
    residual_draws: list[float] = []
    delta_draws: list[float] = []

    if group_col:
        source_groups = df[group_col].dropna().astype(str).unique()
        if len(source_groups) < 2:
            raise ValueError("refit bootstrap requires at least two independent groups")
    else:
        source_groups = np.arange(len(df))

    for draw in range(refit_bootstrap):
        sampled = rng.choice(source_groups, size=len(source_groups), replace=True)
        if group_col:
            pieces = []
            group_values = df[group_col].astype(str)
            for occurrence, sampled_group in enumerate(sampled):
                piece = df.loc[group_values == sampled_group].copy()
                piece[group_col] = f"{sampled_group}__bootstrap_{occurrence}"
                pieces.append(piece)
            bootstrap_frame = pd.concat(pieces, ignore_index=True)
        else:
            bootstrap_frame = df.iloc[np.asarray(sampled, dtype=int)].reset_index(drop=True)
        try:
            result = cross_fitted_audit(
                bootstrap_frame,
                metric,
                target,
                controls,
                group_col=group_col,
                permutations=0,
                bootstrap=0,
                seed=seed + (draw + 1) * 100_003,
                **audit_kwargs,
            )
        except (ValueError, np.linalg.LinAlgError):
            continue
        residual_draws.append(float(result["residual_r"]))
        delta_draws.append(float(result["delta_mse"]))

    minimum_success = max(20, math.ceil(refit_bootstrap * 0.8))
    if len(delta_draws) < minimum_success:
        raise RuntimeError(
            f"only {len(delta_draws)} of {refit_bootstrap} refit bootstrap draws succeeded"
        )
    residual_ci = np.nanquantile(residual_draws, [0.025, 0.975])
    delta_ci = np.nanquantile(delta_draws, [0.025, 0.975])
    base.update(
        {
            "refit_bootstrap_draws": refit_bootstrap,
            "refit_bootstrap_successful": len(delta_draws),
            "refit_residual_ci_low": float(residual_ci[0]),
            "refit_residual_ci_high": float(residual_ci[1]),
            "refit_delta_mse_ci_low": float(delta_ci[0]),
            "refit_delta_mse_ci_high": float(delta_ci[1]),
            "refit_predictive_classification": classify_predictive_increment(
                float(delta_ci[0])
            ),
            "refit_increment_classification": classify_increment_evidence(
                float(base["residual_p"]), float(delta_ci[0])
            ),
        }
    )
    return base


__all__ = [
    "classify_increment_evidence",
    "classify_predictive_increment",
    "cross_fitted_audit",
    "refit_bootstrap_audit",
    "repeated_cross_fitted_audit",
]
