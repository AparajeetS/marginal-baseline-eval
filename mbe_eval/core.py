from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence

import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype
from scipy.stats import spearmanr, t as student_t


DEFAULT_EFFECT_THRESHOLD = 0.20
DEFAULT_WASHOUT_THRESHOLD = 0.10


class MBEInputError(ValueError):
    """Raised when an audit request does not match its training-run ledger."""


def validate_audit_inputs(
    df: pd.DataFrame,
    metrics: Sequence[str],
    target: str,
    controls: Sequence[str],
    groupby: Sequence[str] | str | None = None,
    inference_unit_col: str | None = None,
) -> None:
    """Validate audit columns before fitting any residualization model."""

    if not isinstance(df, pd.DataFrame):
        raise MBEInputError("df must be a pandas DataFrame")
    if df.empty:
        raise MBEInputError("the training-run ledger is empty")
    if not metrics:
        raise MBEInputError("at least one candidate metric is required")

    group_cols = [groupby] if isinstance(groupby, str) else list(groupby or [])
    requested = list(
        dict.fromkeys(
            [
                *metrics,
                target,
                *controls,
                *group_cols,
                *([inference_unit_col] if inference_unit_col else []),
            ]
        )
    )
    missing = [column for column in requested if column not in df.columns]
    if missing:
        available = ", ".join(map(str, df.columns[:12]))
        suffix = " ..." if len(df.columns) > 12 else ""
        raise MBEInputError(
            f"unknown ledger column(s): {', '.join(missing)}. "
            f"Available columns: {available}{suffix}"
        )
    if target in metrics:
        raise MBEInputError("the held-out target cannot also be a candidate metric")


@dataclass(frozen=True)
class MBEReport:
    """Backward-compatible report for a single metric audit."""

    metric_name: str
    baseline_name: str | list[str]
    absolute_r: float
    absolute_p: float
    partial_r: float
    partial_p: float
    is_confounded: bool
    classification: str = "weak-or-mixed"

    @property
    def is_loss_proxy(self) -> bool:
        """Backward-compatible alias for older notebooks."""

        return self.is_confounded


def rank_values(series: pd.Series | Sequence[float]) -> np.ndarray:
    """Return average ranks as a float array."""

    return pd.Series(series).rank(method="average").to_numpy(dtype=float)


def pearson_corr(a: np.ndarray, b: np.ndarray) -> float:
    """Pearson correlation on already-transformed vectors."""

    if len(a) < 3 or np.nanstd(a) <= 0 or np.nanstd(b) <= 0:
        return math.nan
    return float(np.corrcoef(a, b)[0, 1])


def _design_matrix(df: pd.DataFrame, controls: Sequence[str]) -> np.ndarray:
    blocks: list[np.ndarray] = [np.ones(len(df), dtype=float)]
    for control in controls:
        if control not in df.columns:
            continue
        series = df[control]
        if is_numeric_dtype(series):
            blocks.append(rank_values(series.astype(float)))
        else:
            dummies = pd.get_dummies(series.astype(str), drop_first=True)
            for col in dummies.columns:
                blocks.append(dummies[col].to_numpy(dtype=float))
    return np.column_stack(blocks)


def _residualize(y: np.ndarray, design: np.ndarray) -> np.ndarray:
    beta = np.linalg.lstsq(design, y, rcond=None)[0]
    return y - design @ beta


def _p_value_from_r(r: float, n: int, dof_adjustment: int = 0) -> float:
    if np.isnan(r):
        return math.nan
    dof = n - 2 - dof_adjustment
    if dof <= 0 or abs(r) >= 1:
        return math.nan
    statistic = r * math.sqrt(dof / max(1e-12, 1 - r * r))
    return float(2 * student_t.sf(abs(statistic), dof))


def spearman_corr(df: pd.DataFrame, metric: str, target: str) -> tuple[float, float, int]:
    """Spearman rank correlation and p-value."""

    clean = df[[metric, target]].replace([np.inf, -np.inf], np.nan).dropna()
    if len(clean) < 3:
        return math.nan, math.nan, len(clean)
    result = spearmanr(clean[metric], clean[target])
    return float(result.statistic), float(result.pvalue), len(clean)


def partial_rank_corr(
    df: pd.DataFrame,
    metric: str,
    target: str,
    controls: Sequence[str],
) -> tuple[float, float, int]:
    """Partial Spearman correlation by residualizing ranks on ranked controls.

    Numeric controls are rank transformed. Categorical controls are one-hot
    encoded. The returned p-value uses the standard partial-correlation
    t approximation, adjusted by the design matrix rank.
    """

    validate_audit_inputs(df, [metric], target, controls)
    controls = [c for c in controls if c not in {metric, target}]
    cols = list(dict.fromkeys([metric, target, *[c for c in controls if c in df.columns]]))
    clean = df[cols].replace([np.inf, -np.inf], np.nan).dropna()
    if len(clean) < 5:
        return math.nan, math.nan, len(clean)

    x = rank_values(clean[metric])
    y = rank_values(clean[target])
    design = _design_matrix(clean, controls)
    try:
        x_resid = _residualize(x, design)
        y_resid = _residualize(y, design)
    except np.linalg.LinAlgError:
        return math.nan, math.nan, len(clean)

    r = pearson_corr(x_resid, y_resid)
    rank = int(np.linalg.matrix_rank(design)) - 1
    return r, _p_value_from_r(r, len(clean), rank), len(clean)


def classify_effect(
    raw_r: float,
    partial_r: float,
    effect_threshold: float = DEFAULT_EFFECT_THRESHOLD,
    washout_threshold: float = DEFAULT_WASHOUT_THRESHOLD,
) -> str:
    """Classify how a metric behaves after MBE controls."""

    if np.isnan(raw_r) or np.isnan(partial_r):
        return "insufficient-data"
    if abs(raw_r) >= effect_threshold and abs(partial_r) < washout_threshold:
        return "washout"
    if raw_r <= -effect_threshold and partial_r >= effect_threshold:
        return "sign-inversion"
    if raw_r >= effect_threshold and partial_r <= -effect_threshold:
        return "reverse-inversion"
    if abs(raw_r) < effect_threshold and abs(partial_r) >= effect_threshold:
        return "hidden-after-control"
    if np.sign(raw_r) == np.sign(partial_r) and abs(partial_r) >= effect_threshold:
        return "survives"
    return "weak-or-mixed"


def _bootstrap_ci(
    df: pd.DataFrame,
    metric: str,
    target: str,
    controls: Sequence[str],
    n_boot: int,
    seed: int,
    inference_unit_col: str | None = None,
) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    raw_vals: list[float] = []
    partial_vals: list[float] = []
    delta_vals: list[float] = []
    idx = np.arange(len(df))
    units = (
        df[inference_unit_col].drop_duplicates().to_numpy()
        if inference_unit_col
        else None
    )
    for _ in range(n_boot):
        if units is None:
            sample = df.iloc[rng.choice(idx, size=len(idx), replace=True)]
        else:
            sampled_units = rng.choice(units, size=len(units), replace=True)
            pieces = [df.loc[df[inference_unit_col].eq(unit)] for unit in sampled_units]
            sample = pd.concat(pieces, ignore_index=True)
        raw, _, _ = spearman_corr(sample, metric, target)
        partial, _, _ = partial_rank_corr(sample, metric, target, controls)
        raw_vals.append(raw)
        partial_vals.append(partial)
        delta_vals.append(partial - raw if not np.isnan(raw) and not np.isnan(partial) else math.nan)

    def quantile(vals: list[float], q: float) -> float:
        arr = np.asarray([v for v in vals if not np.isnan(v)], dtype=float)
        return float(np.quantile(arr, q)) if len(arr) else math.nan

    return {
        "raw_ci_low": quantile(raw_vals, 0.025),
        "raw_ci_high": quantile(raw_vals, 0.975),
        "partial_ci_low": quantile(partial_vals, 0.025),
        "partial_ci_high": quantile(partial_vals, 0.975),
        "delta_ci_low": quantile(delta_vals, 0.025),
        "delta_ci_high": quantile(delta_vals, 0.975),
    }


def audit_metric(
    df: pd.DataFrame,
    metric: str,
    target: str,
    controls: Sequence[str],
    *,
    group: str = "pooled",
    bootstrap: int = 0,
    seed: int = 0,
    effect_threshold: float = DEFAULT_EFFECT_THRESHOLD,
    washout_threshold: float = DEFAULT_WASHOUT_THRESHOLD,
    inference_unit_col: str | None = None,
) -> dict[str, float | int | str]:
    """Audit one metric against one target under MBE controls."""

    validate_audit_inputs(
        df, [metric], target, controls, inference_unit_col=inference_unit_col
    )
    if bootstrap < 0:
        raise MBEInputError("bootstrap must be zero or a positive integer")
    controls = [c for c in controls if c not in {metric, target}]
    cols = list(
        dict.fromkeys(
            [
                metric,
                target,
                *[c for c in controls if c in df.columns],
                *([inference_unit_col] if inference_unit_col else []),
            ]
        )
    )
    clean = df[cols].replace([np.inf, -np.inf], np.nan).dropna()
    independence_units = (
        int(clean[inference_unit_col].nunique()) if inference_unit_col else len(clean)
    )
    if inference_unit_col and independence_units < 2:
        raise MBEInputError(
            f"inference unit column {inference_unit_col!r} must contain at least two units"
        )
    raw_r, raw_p, n_raw = spearman_corr(clean, metric, target)
    partial_r, partial_p, n_partial = partial_rank_corr(clean, metric, target, controls)
    if inference_unit_col:
        # The analytic correlation p-values assume exchangeable rows. Clustered
        # uncertainty is reported through the declared-unit bootstrap instead.
        raw_p = math.nan
        partial_p = math.nan
    row: dict[str, float | int | str] = {
        "group": group,
        "metric": metric,
        "target": target,
        "controls": ",".join(controls),
        "n": min(n_raw, n_partial),
        "independence_units": independence_units,
        "inference_unit": inference_unit_col or "row",
        "bootstrap_unit": inference_unit_col or "row",
        "raw_r": raw_r,
        "raw_p": raw_p,
        "partial_r": partial_r,
        "partial_p": partial_p,
        "delta_partial_minus_raw": partial_r - raw_r
        if not np.isnan(raw_r) and not np.isnan(partial_r)
        else math.nan,
        "classification": classify_effect(raw_r, partial_r, effect_threshold, washout_threshold),
    }
    if bootstrap > 0 and len(clean) >= 8:
        row.update(
            _bootstrap_ci(
                clean,
                metric,
                target,
                controls,
                bootstrap,
                seed,
                inference_unit_col,
            )
        )
    return row


def audit_metrics(
    df: pd.DataFrame,
    metrics: Sequence[str],
    target: str,
    controls: Sequence[str],
    *,
    groupby: Sequence[str] | str | None = None,
    bootstrap: int = 0,
    seed: int = 0,
    include_pooled: bool = True,
    inference_unit_col: str | None = None,
) -> pd.DataFrame:
    """Audit many metrics in a dataframe.

    Parameters
    ----------
    df:
        One row per training run/model.
    metrics:
        Candidate metric columns to audit.
    target:
        Outcome column, such as final accuracy, validation loss, or perplexity.
    controls:
        Marginal baselines/control variables, such as learning rate, weight
        decay, optimizer, architecture, task, or seed.
    groupby:
        Optional stratification columns. For example, `groupby=["suite", "arch"]`
        reports pooled results plus one result per suite and per architecture.
        This does not declare independent sampling units.
    inference_unit_col:
        Optional column defining independent clusters for bootstrap resampling.
        Analytic row-level p-values are suppressed when this is supplied.
    bootstrap:
        Number of bootstrap resamples for confidence intervals. Use 0 to skip.
    """
    validate_audit_inputs(
        df,
        metrics,
        target,
        controls,
        groupby,
        inference_unit_col=inference_unit_col,
    )
    if bootstrap < 0:
        raise MBEInputError("bootstrap must be zero or a positive integer")
    if not include_pooled and not groupby:
        raise MBEInputError("groupby is required when include_pooled is false")

    available_metrics = list(dict.fromkeys(metrics))
    rows: list[dict[str, float | int | str]] = []
    if include_pooled:
        for i, metric in enumerate(available_metrics):
            rows.append(
                audit_metric(
                    df,
                    metric,
                    target,
                    controls,
                    group="pooled",
                    bootstrap=bootstrap,
                    seed=seed + i,
                    inference_unit_col=inference_unit_col,
                )
            )

    if groupby:
        group_cols = [groupby] if isinstance(groupby, str) else list(groupby)
        for group_col in group_cols:
            if group_col not in df.columns:
                continue
            for value, group_df in df.groupby(group_col, dropna=False):
                label = f"{group_col}={value}"
                for i, metric in enumerate(available_metrics):
                    rows.append(
                        audit_metric(
                            group_df,
                            metric,
                            target,
                            controls,
                            group=label,
                            bootstrap=bootstrap,
                            seed=seed + 10_000 + i,
                            inference_unit_col=inference_unit_col,
                        )
                    )
    return pd.DataFrame(rows)


class MBEEvaluator:
    """Backward-compatible single-metric evaluator.

    New projects should prefer `audit_metric` or `audit_metrics`.
    """

    def __init__(
        self,
        metric_name: str = "Proposed Metric",
        baseline_name: str | list[str] = "Baseline",
    ) -> None:
        self.metric_name = metric_name
        self.baseline_name = baseline_name

    def evaluate(
        self,
        metric_vals: np.ndarray,
        baseline_vals: np.ndarray,
        target_vals: np.ndarray,
        alpha: float = 0.05,
        output_dir: str | None = None,
    ) -> MBEReport:
        metric_vals = np.asarray(metric_vals)
        baseline_vals = np.asarray(baseline_vals)
        target_vals = np.asarray(target_vals)
        df = pd.DataFrame({"Metric": metric_vals, "Target": target_vals})
        if isinstance(self.baseline_name, str):
            df[self.baseline_name] = baseline_vals
            controls = [self.baseline_name]
        else:
            controls = list(self.baseline_name)
            if baseline_vals.ndim == 1 and len(controls) == 1:
                df[controls[0]] = baseline_vals
            else:
                for i, name in enumerate(controls):
                    df[name] = baseline_vals[:, i]

        row = audit_metric(df, "Metric", "Target", controls)
        classification = str(row["classification"])
        return MBEReport(
            metric_name=self.metric_name,
            baseline_name=self.baseline_name,
            absolute_r=float(row["raw_r"]),
            absolute_p=float(row["raw_p"]),
            partial_r=float(row["partial_r"]),
            partial_p=float(row["partial_p"]),
            is_confounded=classification
            in {"washout", "sign-inversion", "reverse-inversion"},
            classification=classification,
        )


__all__ = [
    "MBEReport",
    "MBEEvaluator",
    "audit_metric",
    "audit_metrics",
    "classify_effect",
    "MBEInputError",
    "partial_rank_corr",
    "spearman_corr",
    "validate_audit_inputs",
]
