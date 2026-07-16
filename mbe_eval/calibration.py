from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Sequence
from typing import Callable

import numpy as np
import pandas as pd

from .core import audit_metric
from .crossfit import cross_fitted_audit


@dataclass(frozen=True)
class CalibrationScenario:
    name: str
    expected_profile: str
    controls: tuple[str, ...]
    explanation: str
    generator: Callable[[np.random.Generator, int], pd.DataFrame]


def _base_frame(rng: np.random.Generator, n: int) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "environment": rng.choice(["A", "B"], size=n),
            "config_id": [f"cfg_{i // 5:04d}" for i in range(n)],
        }
    )


def _null_metric(rng: np.random.Generator, n: int) -> pd.DataFrame:
    frame = _base_frame(rng, n)
    baseline = rng.normal(size=n)
    frame["baseline"] = baseline
    frame["metric"] = rng.normal(size=n)
    frame["target"] = baseline + rng.normal(0, 0.55, n)
    return frame


def _linear_proxy(rng: np.random.Generator, n: int) -> pd.DataFrame:
    frame = _base_frame(rng, n)
    baseline = rng.normal(size=n)
    frame["baseline"] = baseline
    frame["metric"] = baseline + rng.normal(0, 0.18, n)
    frame["target"] = baseline + rng.normal(0, 0.45, n)
    return frame


def _nonlinear_proxy(rng: np.random.Generator, n: int) -> pd.DataFrame:
    frame = _base_frame(rng, n)
    baseline = rng.uniform(-2.5, 2.5, n)
    nonlinear = np.square(baseline)
    frame["baseline"] = baseline
    frame["metric"] = nonlinear + rng.normal(0, 0.20, n)
    frame["target"] = nonlinear + rng.normal(0, 0.40, n)
    return frame


def _genuine_increment(rng: np.random.Generator, n: int) -> pd.DataFrame:
    frame = _base_frame(rng, n)
    baseline = rng.normal(size=n)
    latent = rng.normal(size=n)
    frame["baseline"] = baseline
    frame["metric"] = latent + rng.normal(0, 0.18, n)
    frame["target"] = 0.75 * baseline + 0.90 * latent + rng.normal(0, 0.40, n)
    return frame


def _heteroskedastic_null(rng: np.random.Generator, n: int) -> pd.DataFrame:
    frame = _base_frame(rng, n)
    baseline = rng.uniform(-2.5, 2.5, n)
    scale = 0.15 + 0.65 / (1.0 + np.exp(-baseline))
    frame["baseline"] = baseline
    frame["metric"] = np.sin(baseline) + scale * rng.normal(size=n)
    frame["target"] = np.square(baseline) + scale * rng.normal(size=n)
    return frame


def _clustered_null(rng: np.random.Generator, n: int) -> pd.DataFrame:
    frame = _base_frame(rng, n)
    groups = frame["config_id"].astype("category").cat.codes.to_numpy()
    group_count = int(groups.max()) + 1
    group_baseline = rng.normal(size=group_count)
    metric_shock = rng.normal(0, 0.45, group_count)
    target_shock = rng.normal(0, 0.45, group_count)
    baseline = group_baseline[groups]
    frame["baseline"] = baseline
    frame["metric"] = baseline + metric_shock[groups] + rng.normal(0, 0.20, n)
    frame["target"] = baseline + target_shock[groups] + rng.normal(0, 0.20, n)
    return frame


def _simpson_increment(rng: np.random.Generator, n: int) -> pd.DataFrame:
    frame = _base_frame(rng, n)
    environment = (frame["environment"] == "B").to_numpy(dtype=float)
    latent = rng.normal(size=n)
    frame["baseline"] = rng.normal(size=n)
    frame["metric"] = latent - 2.4 * environment + rng.normal(0, 0.15, n)
    frame["target"] = 0.65 * latent + 2.4 * environment + rng.normal(0, 0.40, n)
    return frame


def _post_treatment(rng: np.random.Generator, n: int) -> pd.DataFrame:
    frame = _base_frame(rng, n)
    metric = rng.normal(size=n)
    mediator = 0.95 * metric + rng.normal(0, 0.22, n)
    frame["baseline"] = rng.normal(size=n)
    frame["metric"] = metric
    frame["mediator"] = mediator
    frame["target"] = mediator + rng.normal(0, 0.35, n)
    return frame


SCENARIOS: tuple[CalibrationScenario, ...] = (
    CalibrationScenario(
        "null_metric",
        "no-increment",
        ("baseline",),
        "Independent noise should remain null before and after adjustment.",
        _null_metric,
    ),
    CalibrationScenario(
        "linear_proxy",
        "proxy-washout",
        ("baseline",),
        "A noisy copy of the baseline should lose its apparent target signal.",
        _linear_proxy,
    ),
    CalibrationScenario(
        "nonlinear_proxy",
        "nonlinear-proxy-washout",
        ("baseline",),
        "A U-shaped proxy exposes the limitation of linear partial ranks.",
        _nonlinear_proxy,
    ),
    CalibrationScenario(
        "genuine_increment",
        "increment-survives",
        ("baseline",),
        "A metric with independent latent signal should improve prediction.",
        _genuine_increment,
    ),
    CalibrationScenario(
        "heteroskedastic_null",
        "conditional-null",
        ("baseline",),
        "Independent errors share baseline-dependent variance but no conditional signal.",
        _heteroskedastic_null,
    ),
    CalibrationScenario(
        "clustered_null",
        "conditional-null",
        ("baseline",),
        "Independent configuration-level shocks test grouped folds and inference.",
        _clustered_null,
    ),
    CalibrationScenario(
        "simpson_increment",
        "increment-after-environment-control",
        ("baseline", "environment"),
        "Environment pooling masks a genuine within-environment relationship.",
        _simpson_increment,
    ),
    CalibrationScenario(
        "post_treatment_control",
        "estimand-warning",
        ("baseline", "mediator"),
        "Controlling a mediator removes the total effect by design.",
        _post_treatment,
    ),
)


def make_calibration_ledger(n: int = 600, seed: int = 2026) -> pd.DataFrame:
    """Generate all preregistered synthetic calibration scenarios."""

    if n < 100:
        raise ValueError("calibration scenarios require at least 100 rows each")
    frames: list[pd.DataFrame] = []
    for index, scenario in enumerate(SCENARIOS):
        rng = np.random.default_rng(seed + 10_007 * index)
        frame = scenario.generator(rng, n)
        frame.insert(0, "scenario", scenario.name)
        frame.insert(1, "expected_profile", scenario.expected_profile)
        frames.append(frame)
    return pd.concat(frames, ignore_index=True, sort=False)


def _scenario_pass(
    scenario: CalibrationScenario,
    raw_r: float,
    partial_r: float,
    residual_r: float,
    delta_mse: float,
) -> bool:
    weak_increment = abs(residual_r) < 0.15 and delta_mse < 0.01
    clear_increment = abs(residual_r) >= 0.15 and delta_mse >= 0.01
    if scenario.expected_profile == "no-increment":
        return abs(raw_r) < 0.15 and weak_increment
    if scenario.expected_profile == "conditional-null":
        return delta_mse < 0.01
    if scenario.expected_profile == "proxy-washout":
        return abs(raw_r) >= 0.40 and weak_increment
    if scenario.expected_profile == "nonlinear-proxy-washout":
        return abs(partial_r) >= 0.20 and weak_increment
    if scenario.expected_profile in {
        "increment-survives",
        "increment-after-environment-control",
    }:
        return clear_increment
    if scenario.expected_profile == "estimand-warning":
        return abs(raw_r) >= 0.40 and weak_increment
    return False


def run_calibration(
    *,
    n: int = 600,
    seed: int = 2026,
    permutations: int = 199,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Run legacy and cross-fitted audits on known-ground-truth scenarios."""

    ledger = make_calibration_ledger(n=n, seed=seed)
    rows: list[dict[str, float | int | str | bool]] = []
    for index, scenario in enumerate(SCENARIOS):
        frame = ledger.loc[ledger["scenario"] == scenario.name].copy()
        legacy = audit_metric(frame, "metric", "target", scenario.controls)
        crossfit = cross_fitted_audit(
            frame,
            "metric",
            "target",
            scenario.controls,
            group_col="config_id",
            degree=6,
            permutations=permutations,
            seed=seed + index,
        )
        passed = _scenario_pass(
            scenario,
            float(legacy["raw_r"]),
            float(legacy["partial_r"]),
            float(crossfit["residual_r"]),
            float(crossfit["delta_mse"]),
        )
        rows.append(
            {
                "scenario": scenario.name,
                "expected_profile": scenario.expected_profile,
                "controls": ",".join(scenario.controls),
                "raw_r": legacy["raw_r"],
                "partial_r": legacy["partial_r"],
                "legacy_classification": legacy["classification"],
                "crossfit_residual_r": crossfit["residual_r"],
                "crossfit_permutation_p": crossfit["residual_p"],
                "baseline_mse": crossfit["baseline_mse"],
                "augmented_mse": crossfit["augmented_mse"],
                "delta_mse": crossfit["delta_mse"],
                "relative_mse_improvement": crossfit["relative_mse_improvement"],
                "calibration_pass": passed,
                "explanation": scenario.explanation,
            }
        )
    return ledger, pd.DataFrame(rows)


def _wilson_interval(successes: int, total: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if total <= 0:
        return (float("nan"), float("nan"))
    proportion = successes / total
    denominator = 1.0 + z * z / total
    center = (proportion + z * z / (2.0 * total)) / denominator
    half_width = (
        z
        * np.sqrt(
            proportion * (1.0 - proportion) / total
            + z * z / (4.0 * total * total)
        )
        / denominator
    )
    return float(center - half_width), float(center + half_width)


def run_monte_carlo_calibration(
    *,
    sample_sizes: Sequence[int] = (150, 300, 600),
    degrees: Sequence[int] = (2, 6),
    repetitions: int = 100,
    permutations: int = 199,
    bootstrap: int = 499,
    nuisance_model: str = "polynomial_ridge",
    alpha: float = 0.05,
    seed: int = 20260716,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Estimate repeated-simulation error and detection rates for MBE.

    The residual permutation test is the inferential check. The joint decision
    additionally requires positive out-of-fold Delta MSE. Proxy and null cases
    are treated as conditional-null scenarios; genuine and Simpson increments
    are treated as conditional-signal scenarios. The post-treatment case is a
    null only for the explicitly controlled direct-information estimand.
    """
    if repetitions < 20:
        raise ValueError("Monte Carlo calibration requires at least 20 repetitions")
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must lie strictly between zero and one")
    if any(n < 100 for n in sample_sizes):
        raise ValueError("each calibration sample size must be at least 100")
    if any(degree < 1 for degree in degrees):
        raise ValueError("polynomial degrees must be positive")

    signal_profiles = {
        "increment-survives",
        "increment-after-environment-control",
    }
    rows: list[dict[str, object]] = []
    for scenario_index, scenario in enumerate(SCENARIOS):
        expected_signal = scenario.expected_profile in signal_profiles
        for n in sample_sizes:
            for degree in degrees:
                for repetition in range(repetitions):
                    run_seed = (
                        seed
                        + scenario_index * 10_000_019
                        + n * 10_007
                        + degree * 1_009
                        + repetition
                    )
                    frame = scenario.generator(np.random.default_rng(run_seed), n)
                    legacy = audit_metric(frame, "metric", "target", scenario.controls)
                    crossfit = cross_fitted_audit(
                        frame,
                        "metric",
                        "target",
                        scenario.controls,
                        group_col="config_id",
                        degree=degree,
                        permutations=permutations,
                        bootstrap=bootstrap,
                        nuisance_model=nuisance_model,
                        seed=run_seed,
                    )
                    residual_reject = bool(
                        np.isfinite(crossfit["residual_p"])
                        and float(crossfit["residual_p"]) <= alpha
                    )
                    positive_delta = float(crossfit["delta_mse"]) > 0.0
                    delta_ci_positive = float(crossfit["delta_mse_ci_low"]) > 0.0
                    rows.append(
                        {
                            "scenario": scenario.name,
                            "expected_profile": scenario.expected_profile,
                            "expected_signal": expected_signal,
                            "n": n,
                            "polynomial_degree": degree,
                            "nuisance_model": nuisance_model,
                            "repetition": repetition,
                            "seed": run_seed,
                            "raw_r": legacy["raw_r"],
                            "raw_p": legacy["raw_p"],
                            "partial_r": legacy["partial_r"],
                            "partial_p": legacy["partial_p"],
                            "legacy_partial_reject": bool(
                                np.isfinite(legacy["partial_p"])
                                and float(legacy["partial_p"]) <= alpha
                            ),
                            "crossfit_residual_r": crossfit["residual_r"],
                            "crossfit_residual_p": crossfit["residual_p"],
                            "delta_mse": crossfit["delta_mse"],
                            "delta_mse_ci_low": crossfit["delta_mse_ci_low"],
                            "delta_mse_ci_high": crossfit["delta_mse_ci_high"],
                            "relative_mse_improvement": crossfit[
                                "relative_mse_improvement"
                            ],
                            "crossfit_residual_reject": residual_reject,
                            "positive_delta_mse": positive_delta,
                            "delta_ci_positive": delta_ci_positive,
                            "joint_increment_decision": residual_reject
                            and delta_ci_positive,
                            "profile_pass": _scenario_pass(
                                scenario,
                                float(legacy["raw_r"]),
                                float(legacy["partial_r"]),
                                float(crossfit["residual_r"]),
                                float(crossfit["delta_mse"]),
                            ),
                        }
                    )

    ledger = pd.DataFrame(rows)
    summaries: list[dict[str, object]] = []
    group_columns = [
        "scenario",
        "expected_profile",
        "expected_signal",
        "n",
        "polynomial_degree",
        "nuisance_model",
    ]
    for keys, group in ledger.groupby(group_columns, sort=True, dropna=False):
        summary = dict(zip(group_columns, keys))
        total = len(group)
        for column in (
            "legacy_partial_reject",
            "crossfit_residual_reject",
            "joint_increment_decision",
            "profile_pass",
        ):
            successes = int(group[column].sum())
            low, high = _wilson_interval(successes, total)
            summary[f"{column}_rate"] = successes / total
            summary[f"{column}_ci_low"] = low
            summary[f"{column}_ci_high"] = high
        summary.update(
            {
                "repetitions": total,
                "median_residual_r": group["crossfit_residual_r"].median(),
                "median_delta_mse": group["delta_mse"].median(),
                "median_relative_mse_improvement": group[
                    "relative_mse_improvement"
                ].median(),
            }
        )
        summaries.append(summary)
    return ledger, pd.DataFrame(summaries)


__all__ = [
    "CalibrationScenario",
    "SCENARIOS",
    "make_calibration_ledger",
    "run_calibration",
    "run_monte_carlo_calibration",
]
