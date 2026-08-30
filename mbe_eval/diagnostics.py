from __future__ import annotations

import math
from typing import Iterable

import numpy as np
import pandas as pd
from scipy.stats import norm


def minimum_detectable_correlation(
    independence_units: int,
    *,
    alpha: float = 0.05,
    power: float = 0.80,
) -> float:
    """Approximate two-sided detectable correlation using Fisher's z transform."""
    if independence_units <= 3:
        return math.nan
    if not 0 < alpha < 1 or not 0 < power < 1:
        raise ValueError("alpha and power must lie strictly between zero and one")
    z_required = norm.ppf(1 - alpha / 2) + norm.ppf(power)
    return float(np.tanh(z_required / np.sqrt(independence_units - 3)))


def audit_power_diagnostic(
    independence_units: int,
    *,
    alpha: float = 0.05,
    power_levels: Iterable[float] = (0.8, 0.9),
) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "independence_units": independence_units,
                "alpha": alpha,
                "power": power,
                "minimum_detectable_abs_correlation": minimum_detectable_correlation(
                    independence_units, alpha=alpha, power=power
                ),
            }
            for power in power_levels
        ]
    )


def abstention_reasons(
    audit_rows: pd.DataFrame,
    *,
    minimum_units: int = 30,
    require_refit_interval: bool = False,
) -> list[str]:
    """Return auditable reasons not to issue a metric recommendation."""
    reasons: list[str] = []
    if audit_rows.empty:
        return ["no-audit-results"]
    if audit_rows["independence_units"].min() < minimum_units:
        reasons.append("insufficient-independent-units")
    grouping_columns = [
        column
        for column in ("scope", "baseline_level", "metric", "target")
        if column in audit_rows
    ]
    groups = (
        [group for _, group in audit_rows.groupby(grouping_columns, dropna=False)]
        if grouping_columns
        else [audit_rows]
    )
    if any(group["nuisance_model"].nunique() < 2 for group in groups):
        reasons.append("nuisance-sensitivity-not-run")
    if any(
        group["increment_classification"].dropna().astype(str).nunique() > 1
        for group in groups
    ):
        reasons.append("nuisance-model-disagreement")
    if require_refit_interval and (
        "refit_delta_mse_ci_low" not in audit_rows
        or audit_rows["refit_delta_mse_ci_low"].isna().any()
    ):
        reasons.append("refit-aware-uncertainty-not-run")
    if "delta_mse_ci_low" in audit_rows and audit_rows["delta_mse_ci_low"].isna().any():
        reasons.append("predictive-interval-missing")
    return reasons


__all__ = [
    "abstention_reasons",
    "audit_power_diagnostic",
    "minimum_detectable_correlation",
]
