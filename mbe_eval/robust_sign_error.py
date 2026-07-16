from __future__ import annotations

from itertools import combinations
from typing import Sequence

import numpy as np
import pandas as pd


def hoeffding_weight(delta: np.ndarray, n: int = 10_000) -> np.ndarray:
    """Return the squared Hoeffding confidence weight used by Dziugaite et al."""

    delta = np.asarray(delta, dtype=float)
    phi = 2.0 * np.exp(-2.0 * n * np.square(delta / 2.0))
    return np.square(np.maximum(0.0, 1.0 - phi))


def weighted_environment_loss(
    first_gap: np.ndarray,
    second_gap: np.ndarray,
    first_metrics: np.ndarray,
    second_metrics: np.ndarray,
    *,
    test_size: int = 10_000,
    minimum_weight: float = 0.5,
) -> tuple[np.ndarray, float, float]:
    """Compute source-compatible weighted sign errors for one environment."""

    first_gap = np.asarray(first_gap, dtype=float)
    second_gap = np.asarray(second_gap, dtype=float)
    first_metrics = np.asarray(first_metrics, dtype=float)
    second_metrics = np.asarray(second_metrics, dtype=float)
    if first_metrics.ndim == 1:
        first_metrics = first_metrics[:, None]
    if second_metrics.ndim == 1:
        second_metrics = second_metrics[:, None]

    gap_difference = first_gap[:, None] - second_gap[None, :]
    weight = hoeffding_weight(np.abs(gap_difference), n=test_size)
    weight = np.maximum(weight - minimum_weight, 0.0)
    weight_sum = float(np.sum(weight))
    squared_weight_sum = float(np.sum(np.square(weight)))
    effective_sample_size = (
        weight_sum * weight_sum / squared_weight_sum if squared_weight_sum > 0 else 0.0
    )

    metric_difference = first_metrics[:, None, :] - second_metrics[None, :, :]
    agreement = np.sign(metric_difference) * np.sign(gap_difference)[:, :, None]
    sign_error = (1.0 - agreement) / 2.0
    if weight_sum <= 0:
        losses = np.full(first_metrics.shape[1], np.nan, dtype=float)
    else:
        losses = np.sum(sign_error * weight[:, :, None], axis=(0, 1)) / weight_sum
    return losses, weight_sum, effective_sample_size


def source_metric_columns(columns: Sequence[str]) -> list[str]:
    """Apply the paper figure's rule of preferring FFT spectral variants."""

    available = {column for column in columns if column.startswith("complexity.")}
    return [
        column
        for column in columns
        if column in available and not ("_fft" not in column and f"{column}_fft" in available)
    ]


def robust_sign_error_environments(
    df: pd.DataFrame,
    metrics: Sequence[str],
    hyperparameters: Sequence[str],
    *,
    target: str = "gen.gap",
    config_column: str = "config_id",
    test_size: int = 10_000,
    minimum_weight: float = 0.5,
    minimum_effective_sample_size: float = 12.0,
) -> pd.DataFrame:
    """Reconstruct directed coupled-network environments.

    Each returned row corresponds to one direction of a configuration pair
    that differs in exactly one declared hyperparameter. The source statistic
    is symmetric, so both directions have equal losses and are retained to
    match the authors' environment counts.
    """

    metrics = list(metrics)
    hyperparameters = list(hyperparameters)
    required = [config_column, target, *metrics, *hyperparameters]
    missing = sorted(set(required) - set(df.columns))
    if missing:
        raise ValueError(f"dataset is missing columns: {', '.join(missing)}")
    clean = df[required].replace([np.inf, -np.inf], np.nan).dropna().copy()
    config_hyperparameters = clean.groupby(config_column)[hyperparameters].nunique()
    if (config_hyperparameters > 1).any().any():
        raise ValueError("a configuration maps to multiple hyperparameter values")

    configurations: dict[str, dict[str, object]] = {}
    for config, group in clean.groupby(config_column, sort=True):
        configurations[str(config)] = {
            "hps": tuple(group.iloc[0][hyperparameters].tolist()),
            "gap": group[target].to_numpy(dtype=float),
            "metrics": group[metrics].to_numpy(dtype=float),
        }

    rows: list[dict[str, object]] = []
    for hp_index, hyperparameter in enumerate(hyperparameters):
        coupled: dict[tuple[object, ...], list[str]] = {}
        for config, values in configurations.items():
            hp_values = values["hps"]
            key = tuple(hp_values[:hp_index] + hp_values[hp_index + 1 :])
            coupled.setdefault(key, []).append(config)

        for configs in coupled.values():
            for first, second in combinations(sorted(configs), 2):
                first_values = configurations[first]
                second_values = configurations[second]
                first_hp = first_values["hps"][hp_index]
                second_hp = second_values["hps"][hp_index]
                if first_hp == second_hp or (
                    isinstance(first_hp, float)
                    and isinstance(second_hp, float)
                    and np.isclose(first_hp, second_hp)
                ):
                    continue
                losses, weight_sum, effective_sample_size = weighted_environment_loss(
                    first_values["gap"],
                    second_values["gap"],
                    first_values["metrics"],
                    second_values["metrics"],
                    test_size=test_size,
                    minimum_weight=minimum_weight,
                )
                if not (
                    np.isclose(effective_sample_size, minimum_effective_sample_size)
                    or effective_sample_size > minimum_effective_sample_size
                ):
                    continue
                for source, destination in ((first, second), (second, first)):
                    row: dict[str, object] = {
                        "hyperparameter": hyperparameter,
                        "source_config": source,
                        "destination_config": destination,
                        "weight_sum": weight_sum,
                        "effective_sample_size": effective_sample_size,
                    }
                    row.update(dict(zip(metrics, losses)))
                    rows.append(row)
    return pd.DataFrame(rows)


def robust_sign_error_summary(
    environments: pd.DataFrame,
    metrics: Sequence[str],
) -> pd.DataFrame:
    """Summarize the source figure's mean, 90th percentile, and maximum."""

    rows: list[dict[str, object]] = []
    scopes = ["all", *environments["hyperparameter"].drop_duplicates().tolist()]
    for scope in scopes:
        frame = environments if scope == "all" else environments.loc[
            environments["hyperparameter"] == scope
        ]
        for metric in metrics:
            values = frame[metric].dropna().to_numpy(dtype=float)
            rows.append(
                {
                    "hyperparameter": scope,
                    "metric": metric,
                    "environments": len(values),
                    "mean_sign_error": float(np.mean(values)) if len(values) else np.nan,
                    "p90_sign_error": float(np.percentile(values, 90)) if len(values) else np.nan,
                    "max_sign_error": float(np.max(values)) if len(values) else np.nan,
                }
            )
    return pd.DataFrame(rows)


__all__ = [
    "hoeffding_weight",
    "robust_sign_error_environments",
    "robust_sign_error_summary",
    "source_metric_columns",
    "weighted_environment_loss",
]
