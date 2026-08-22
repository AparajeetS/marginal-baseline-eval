from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict, dataclass
import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Iterable

import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from mbe_eval import cross_fitted_audit, refit_bootstrap_audit  # noqa: E402


PROTOCOL_ID = "mbe3-design-matched-calibration-v1"
ALPHA = 0.05
REPETITIONS = 100
PERMUTATIONS = 199
REFIT_BOOTSTRAP = 199
ICC_LEVELS = (0.30, 0.80)
SIGNAL_EFFECTS = (0.20, 0.35, 0.50)
NULL_SCENARIOS = (
    "independent_null",
    "additive_proxy_null",
    "nonlinear_proxy_null",
    "interaction_proxy_null",
    "heteroskedastic_proxy_null",
)
SIGNAL_SCENARIOS = ("interaction_increment",)


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    nuisance_model: str
    degree: int
    complexity_rank: int


CANDIDATES = (
    Candidate("additive_d4", "polynomial_ridge", 4, 1),
    Candidate("additive_d6", "polynomial_ridge", 6, 2),
    Candidate("interactions_d4", "polynomial_ridge_interactions", 4, 3),
    Candidate("interactions_d6", "polynomial_ridge_interactions", 6, 4),
    Candidate("extra_trees", "extra_trees", 1, 5),
)
CANDIDATE_BY_ID = {candidate.candidate_id: candidate for candidate in CANDIDATES}


BASELINES = {
    "B1_design": {
        "image": [
            "arch",
            "optimizer",
            "lr_level",
            "learning_rate",
            "weight_decay",
            "dropout",
            "seed_id",
        ],
        "text": [
            "model_size",
            "learning_rate",
            "weight_decay",
            "dropout",
            "seed_id",
        ],
    },
    "B2_training_state": {
        "image": [
            "arch",
            "optimizer",
            "lr_level",
            "learning_rate",
            "weight_decay",
            "dropout",
            "seed_id",
            "final_train_batch_loss",
        ],
        "text": [
            "model_size",
            "learning_rate",
            "weight_decay",
            "dropout",
            "seed_id",
            "final_train_batch_loss",
        ],
    },
    "B3_validation": {
        "image": [
            "arch",
            "optimizer",
            "lr_level",
            "learning_rate",
            "weight_decay",
            "dropout",
            "seed_id",
            "final_train_batch_loss",
            "val_loss",
        ],
        "text": [
            "model_size",
            "learning_rate",
            "weight_decay",
            "dropout",
            "seed_id",
            "final_train_batch_loss",
            "val_loss",
        ],
    },
}


@dataclass(frozen=True)
class Design:
    scope: str
    frame: pd.DataFrame
    group_col: str
    block_col: str


def _stable_id(prefix: str, values: Iterable[object]) -> str:
    payload = json.dumps(list(values), separators=(",", ":"), sort_keys=False)
    return f"{prefix}-{hashlib.sha256(payload.encode()).hexdigest()[:12]}"


def make_image_design() -> Design:
    rows: list[dict[str, object]] = []
    learning_rates = {
        "adamw": {"low": 3e-4, "high": 1e-3},
        "sgd": {"low": 1e-2, "high": 3e-2},
    }
    for optimizer in ("adamw", "sgd"):
        for lr_level in ("low", "high"):
            for weight_decay in (0.0, 1e-3):
                for dropout in (0.0, 0.2):
                    for arch in ("cnn", "resnet", "wide_resnet"):
                        config_values = (
                            arch,
                            optimizer,
                            lr_level,
                            learning_rates[optimizer][lr_level],
                            weight_decay,
                            dropout,
                        )
                        config_id = _stable_id("image", config_values)
                        for seed_id in ("8111", "8112"):
                            rows.append(
                                {
                                    "scope": "image",
                                    "config_id": config_id,
                                    "seed_id": seed_id,
                                    "arch": arch,
                                    "optimizer": optimizer,
                                    "lr_level": lr_level,
                                    "learning_rate": learning_rates[optimizer][lr_level],
                                    "weight_decay": weight_decay,
                                    "dropout": dropout,
                                }
                            )
    frame = pd.DataFrame(rows)
    if len(frame) != 96 or frame["config_id"].nunique() != 48:
        raise RuntimeError("image design construction violated the frozen grid")
    return Design("image", frame, "config_id", "arch")


def make_text_design() -> Design:
    rows: list[dict[str, object]] = []
    for learning_rate in (2e-4, 6e-4, 1.5e-3):
        for weight_decay in (0.0, 1e-2):
            for dropout in (0.0, 0.2):
                for model_size in ("small", "medium"):
                    config_values = (
                        model_size,
                        learning_rate,
                        weight_decay,
                        dropout,
                    )
                    config_id = _stable_id("text", config_values)
                    for seed_id in ("8201", "8202"):
                        rows.append(
                            {
                                "scope": "text",
                                "config_id": config_id,
                                "seed_id": seed_id,
                                "model_size": model_size,
                                "learning_rate": learning_rate,
                                "weight_decay": weight_decay,
                                "dropout": dropout,
                            }
                        )
    frame = pd.DataFrame(rows)
    if len(frame) != 48 or frame["config_id"].nunique() != 24:
        raise RuntimeError("text design construction violated the frozen grid")
    return Design("text", frame, "config_id", "model_size")


def get_design(scope: str) -> Design:
    if scope == "image":
        return make_image_design()
    if scope == "text":
        return make_text_design()
    raise ValueError(f"unknown scope: {scope}")


def _standardize(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    scale = float(values.std(ddof=1))
    if not np.isfinite(scale) or scale <= 0:
        return values - float(values.mean())
    return (values - float(values.mean())) / scale


def _factor_codes(design: Design) -> np.ndarray:
    frame = design.frame
    if design.scope == "image":
        columns = [
            frame["arch"].map({"cnn": -1.0, "resnet": 0.0, "wide_resnet": 1.0}),
            frame["optimizer"].map({"adamw": -1.0, "sgd": 1.0}),
            frame["lr_level"].map({"low": -1.0, "high": 1.0}),
            frame["weight_decay"].map({0.0: -1.0, 1e-3: 1.0}),
            frame["dropout"].map({0.0: -1.0, 0.2: 1.0}),
        ]
    else:
        columns = [
            frame["model_size"].map({"small": -1.0, "medium": 1.0}),
            frame["learning_rate"].map({2e-4: -1.0, 6e-4: 0.0, 1.5e-3: 1.0}),
            frame["weight_decay"].map({0.0: -1.0, 1e-2: 1.0}),
            frame["dropout"].map({0.0: -1.0, 0.2: 1.0}),
        ]
    return np.column_stack([column.to_numpy(dtype=float) for column in columns])


def _surfaces(design: Design) -> dict[str, np.ndarray]:
    x = _factor_codes(design)
    additive = 0.55 * x[:, 0] - 0.40 * x[:, 1] + 0.30 * x[:, 2]
    if x.shape[1] > 3:
        additive += 0.20 * x[:, 3]
    if x.shape[1] > 4:
        additive -= 0.15 * x[:, 4]
    nonlinear = additive + 0.65 * np.square(x[:, 1]) - 0.45 * np.cos(np.pi * x[:, 2])
    interaction = nonlinear + 0.70 * x[:, 0] * x[:, 1] - 0.55 * x[:, 2] * x[:, 3]
    if x.shape[1] > 4:
        interaction += 0.45 * x[:, 0] * x[:, 4]
    threshold = interaction + 0.60 * (x[:, 1] > 0).astype(float) * x[:, 2]
    return {
        "additive": _standardize(additive),
        "nonlinear": _standardize(nonlinear),
        "interaction": _standardize(interaction),
        "threshold": _standardize(threshold),
    }


def _group_latent(
    frame: pd.DataFrame, rng: np.random.Generator, scale: float = 1.0
) -> np.ndarray:
    groups = sorted(frame["config_id"].astype(str).unique())
    draws = rng.normal(scale=scale, size=len(groups))
    mapping = dict(zip(groups, draws, strict=True))
    return frame["config_id"].astype(str).map(mapping).to_numpy(dtype=float)


def simulate_frame(
    scope: str,
    scenario: str,
    icc: float,
    beta: float,
    seed: int,
) -> pd.DataFrame:
    design = get_design(scope)
    frame = design.frame.copy()
    rng = np.random.default_rng(seed)
    surfaces = _surfaces(design)
    signal = _group_latent(frame, rng)
    train_state = _group_latent(frame, rng)
    validation_state = _group_latent(frame, rng)
    row_noise = rng.normal(size=(len(frame), 5))

    frame["final_train_batch_loss"] = _standardize(
        0.55 * surfaces["additive"] + 0.65 * train_state + 0.45 * row_noise[:, 0]
    )
    frame["val_loss"] = _standardize(
        0.45 * surfaces["nonlinear"]
        + 0.35 * train_state
        + 0.60 * validation_state
        + 0.40 * row_noise[:, 1]
    )

    if scenario == "independent_null":
        metric_surface = np.zeros(len(frame), dtype=float)
        target_surface = surfaces["interaction"]
        heteroskedastic = np.ones(len(frame), dtype=float)
    elif scenario == "additive_proxy_null":
        metric_surface = surfaces["additive"]
        target_surface = 0.75 * surfaces["additive"] + 0.25 * surfaces["nonlinear"]
        heteroskedastic = np.ones(len(frame), dtype=float)
    elif scenario == "nonlinear_proxy_null":
        metric_surface = surfaces["nonlinear"]
        target_surface = 0.65 * surfaces["nonlinear"] + 0.35 * surfaces["threshold"]
        heteroskedastic = np.ones(len(frame), dtype=float)
    elif scenario == "interaction_proxy_null":
        metric_surface = surfaces["interaction"]
        target_surface = surfaces["threshold"]
        heteroskedastic = np.ones(len(frame), dtype=float)
    elif scenario == "heteroskedastic_proxy_null":
        metric_surface = surfaces["threshold"]
        target_surface = surfaces["interaction"]
        heteroskedastic = 0.45 + 0.75 * (surfaces["additive"] > 0).astype(float)
    elif scenario == "interaction_increment":
        metric_surface = surfaces["interaction"]
        target_surface = surfaces["threshold"]
        heteroskedastic = np.ones(len(frame), dtype=float)
    else:
        raise ValueError(f"unknown scenario: {scenario}")

    if scenario in NULL_SCENARIOS and beta != 0.0:
        raise ValueError("null scenarios require beta=0")
    if scenario in SIGNAL_SCENARIOS and beta <= 0.0:
        raise ValueError("signal scenarios require beta>0")

    metric = (
        0.65 * metric_surface
        + math.sqrt(icc) * signal
        + math.sqrt(1.0 - icc) * row_noise[:, 2]
    )
    target = (
        0.80 * target_surface
        + 0.35 * train_state
        + 0.45 * validation_state
        + beta * signal
        + heteroskedastic * row_noise[:, 3]
    )
    frame["synthetic_metric"] = _standardize(metric)
    frame["synthetic_target"] = _standardize(target)
    frame["negative_control"] = _standardize(row_noise[:, 4])
    return frame


def wilson_interval(successes: int, total: int) -> tuple[float, float]:
    if total <= 0:
        return math.nan, math.nan
    z = 1.959963984540054
    rate = successes / total
    denominator = 1.0 + z**2 / total
    center = (rate + z**2 / (2.0 * total)) / denominator
    half = z * math.sqrt(rate * (1.0 - rate) / total + z**2 / (4.0 * total**2)) / denominator
    return center - half, center + half


def _run_cell(payload: dict[str, object]) -> dict[str, object]:
    design = get_design(str(payload["scope"]))
    candidate = CANDIDATE_BY_ID[str(payload["candidate_id"])]
    frame = simulate_frame(
        design.scope,
        str(payload["scenario"]),
        float(payload["icc"]),
        float(payload["beta"]),
        int(payload["simulation_seed"]),
    )
    controls = BASELINES[str(payload["baseline"])][design.scope]
    kwargs = {
        "group_col": design.group_col,
        "permutation_block_col": design.block_col,
        "n_splits": 5,
        "degree": candidate.degree,
        "nuisance_model": candidate.nuisance_model,
        "permutations": int(payload["permutations"]),
        "seed": int(payload["analysis_seed"]),
    }
    try:
        if payload["stage"] == "confirm":
            result = refit_bootstrap_audit(
                frame,
                "synthetic_metric",
                "synthetic_target",
                controls,
                refit_bootstrap=int(payload["refit_bootstrap"]),
                **kwargs,
            )
            predictive_supported = bool(result["refit_delta_mse_ci_low"] > 0.0)
            joint_supported = result["refit_increment_classification"] == "increment-supported"
        else:
            result = cross_fitted_audit(
                frame,
                "synthetic_metric",
                "synthetic_target",
                controls,
                bootstrap=0,
                **kwargs,
            )
            predictive_supported = bool(result["delta_mse"] > 0.0)
            joint_supported = bool(
                predictive_supported
                and np.isfinite(result["residual_p"])
                and result["residual_p"] <= ALPHA
            )
        return {
            **payload,
            "status": "estimated",
            "delta_mse": result["delta_mse"],
            "residual_p": result["residual_p"],
            "predictive_supported": predictive_supported,
            "joint_supported": joint_supported,
            "refit_delta_mse_ci_low": result.get("refit_delta_mse_ci_low", math.nan),
            "refit_delta_mse_ci_high": result.get("refit_delta_mse_ci_high", math.nan),
        }
    except (ImportError, RuntimeError, ValueError, np.linalg.LinAlgError) as error:
        return {**payload, "status": f"not_estimable: {error}"}


GROUP_KEYS = ["scope", "baseline", "candidate_id", "scenario", "icc", "beta"]


def summarize(ledger: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for key, cell in ledger.groupby(GROUP_KEYS, sort=True, dropna=False):
        estimated = cell.loc[cell["status"].eq("estimated")]
        total = len(cell)
        predictive_count = int(estimated["predictive_supported"].fillna(False).sum())
        joint_count = int(estimated["joint_supported"].fillna(False).sum())
        predictive_low, predictive_high = wilson_interval(predictive_count, total)
        joint_low, joint_high = wilson_interval(joint_count, total)
        rows.append(
            dict(zip(GROUP_KEYS, key, strict=True))
            | {
                "planned_repetitions": total,
                "estimated_repetitions": len(estimated),
                "estimability_rate": len(estimated) / total,
                "predictive_support_count": predictive_count,
                "predictive_support_rate": predictive_count / total,
                "predictive_wilson_95_low": predictive_low,
                "predictive_wilson_95_high": predictive_high,
                "joint_support_count": joint_count,
                "joint_support_rate": joint_count / total,
                "joint_wilson_95_low": joint_low,
                "joint_wilson_95_high": joint_high,
            }
        )
    return pd.DataFrame(rows)


def select_screen_finalists(summary: pd.DataFrame) -> dict[str, object]:
    selections: dict[str, list[str]] = {}
    diagnostics: list[dict[str, object]] = []
    for (scope, baseline, candidate_id), cell in summary.groupby(
        ["scope", "baseline", "candidate_id"], sort=True
    ):
        null = cell.loc[cell["scenario"].isin(NULL_SCENARIOS)]
        signal_large = cell.loc[
            cell["scenario"].isin(SIGNAL_SCENARIOS) & cell["beta"].eq(0.50)
        ]
        estimability = float(cell["estimability_rate"].min())
        max_null_joint_upper = float(null["joint_wilson_95_high"].max())
        min_large_signal_joint = float(signal_large["joint_support_rate"].min())
        screen_pass = (
            estimability >= 0.98
            and max_null_joint_upper <= 0.10
            and min_large_signal_joint >= 0.20
        )
        diagnostics.append(
            {
                "scope": scope,
                "baseline": baseline,
                "candidate_id": candidate_id,
                "minimum_estimability": estimability,
                "maximum_null_joint_wilson_upper": max_null_joint_upper,
                "minimum_beta_0_50_joint_power": min_large_signal_joint,
                "screen_pass": screen_pass,
                "complexity_rank": CANDIDATE_BY_ID[candidate_id].complexity_rank,
            }
        )
    diagnostic_frame = pd.DataFrame(diagnostics)
    for (scope, baseline), cell in diagnostic_frame.groupby(["scope", "baseline"], sort=True):
        passed = cell.loc[cell["screen_pass"]].sort_values(
            ["minimum_beta_0_50_joint_power", "complexity_rank", "candidate_id"],
            ascending=[False, True, True],
        )
        selections[f"{scope}:{baseline}"] = passed["candidate_id"].head(2).tolist()
    return {
        "protocol_id": PROTOCOL_ID,
        "stage": "screen",
        "selection_rule": {
            "minimum_estimability": 0.98,
            "maximum_null_joint_wilson_upper": 0.10,
            "minimum_beta_0_50_joint_power": 0.20,
            "finalists_per_scope_baseline": 2,
            "ranking": "minimum beta=0.50 joint power descending, then frozen complexity rank",
        },
        "selections": selections,
        "diagnostics": diagnostics,
    }


def confirm_eligibility(summary: pd.DataFrame) -> dict[str, object]:
    decisions: list[dict[str, object]] = []
    for (scope, baseline, candidate_id), cell in summary.groupby(
        ["scope", "baseline", "candidate_id"], sort=True
    ):
        null = cell.loc[cell["scenario"].isin(NULL_SCENARIOS)]
        signal_large = cell.loc[
            cell["scenario"].isin(SIGNAL_SCENARIOS) & cell["beta"].eq(0.50)
        ]
        signal_mid = cell.loc[
            cell["scenario"].isin(SIGNAL_SCENARIOS) & cell["beta"].eq(0.35)
        ]
        estimability = float(cell["estimability_rate"].min())
        max_null_predictive_upper = float(null["predictive_wilson_95_high"].max())
        max_null_joint_upper = float(null["joint_wilson_95_high"].max())
        min_large_predictive_low = float(signal_large["predictive_wilson_95_low"].min())
        min_mid_predictive = (
            float(signal_mid["predictive_support_rate"].min())
            if len(signal_mid)
            else 0.0
        )
        eligible = (
            estimability >= 0.95
            and max_null_predictive_upper <= 0.10
            and max_null_joint_upper <= 0.10
            and min_large_predictive_low >= 0.50
        )
        decisions.append(
            {
                "scope": scope,
                "baseline": baseline,
                "candidate_id": candidate_id,
                "minimum_estimability": estimability,
                "maximum_null_predictive_wilson_upper": max_null_predictive_upper,
                "maximum_null_joint_wilson_upper": max_null_joint_upper,
                "minimum_beta_0_50_predictive_wilson_lower": min_large_predictive_low,
                "minimum_beta_0_35_predictive_power": min_mid_predictive,
                "eligible": eligible,
                "complexity_rank": CANDIDATE_BY_ID[candidate_id].complexity_rank,
            }
        )
    decision_frame = pd.DataFrame(decisions)
    opening: dict[str, dict[str, object]] = {}
    for (scope, baseline), cell in decision_frame.groupby(["scope", "baseline"], sort=True):
        eligible = cell.loc[cell["eligible"]].sort_values(
            ["minimum_beta_0_35_predictive_power", "complexity_rank", "candidate_id"],
            ascending=[False, True, True],
        )
        selected = eligible["candidate_id"].iloc[0] if len(eligible) else None
        opening[f"{scope}:{baseline}"] = {
            "open_protected_analysis": selected is not None,
            "selected_primary_candidate": selected,
            "eligible_candidates": eligible["candidate_id"].tolist(),
            "decision": "open" if selected is not None else "abstain",
        }
    return {
        "protocol_id": PROTOCOL_ID,
        "stage": "confirm",
        "eligibility_rule": {
            "minimum_estimability": 0.95,
            "maximum_null_predictive_wilson_upper": 0.10,
            "maximum_null_joint_wilson_upper": 0.10,
            "minimum_beta_0_50_predictive_wilson_lower": 0.50,
            "primary_ranking": "minimum beta=0.35 predictive power descending, then frozen complexity rank",
        },
        "opening_decisions": opening,
        "candidate_diagnostics": decisions,
    }


def _task_grid(
    stage: str,
    repetitions: int,
    permutations: int,
    refit_bootstrap: int,
    selected: dict[str, list[str]] | None,
    smoke: bool,
) -> list[dict[str, object]]:
    scopes = ("image",) if smoke else ("image", "text")
    baselines = ("B1_design",) if smoke else tuple(BASELINES)
    iccs = (0.30,) if smoke else ICC_LEVELS
    effects = (0.50,) if smoke else SIGNAL_EFFECTS
    null_scenarios = ("independent_null",) if smoke else NULL_SCENARIOS
    signal_scenarios = SIGNAL_SCENARIOS
    tasks: list[dict[str, object]] = []
    task_index = 0
    for scope in scopes:
        for baseline in baselines:
            if selected is None:
                candidates = (CANDIDATES[0],) if smoke else CANDIDATES
            else:
                candidates = tuple(
                    CANDIDATE_BY_ID[candidate_id]
                    for candidate_id in selected.get(f"{scope}:{baseline}", [])
                )
            for candidate in candidates:
                conditions = [
                    (scenario, icc, 0.0)
                    for scenario in null_scenarios
                    for icc in iccs
                ] + [
                    (scenario, icc, effect)
                    for scenario in signal_scenarios
                    for icc in iccs
                    for effect in effects
                ]
                for scenario, icc, beta in conditions:
                    for repetition in range(repetitions):
                        tasks.append(
                            {
                                "protocol_id": PROTOCOL_ID,
                                "stage": stage,
                                "scope": scope,
                                "baseline": baseline,
                                "candidate_id": candidate.candidate_id,
                                "scenario": scenario,
                                "icc": icc,
                                "beta": beta,
                                "repetition": repetition,
                                "permutations": permutations,
                                "refit_bootstrap": refit_bootstrap,
                                "simulation_seed": 20260811 + task_index * 100_003,
                                "analysis_seed": 20260811 + task_index * 1_000_003,
                            }
                        )
                        task_index += 1
    return tasks


def _task_key(row: dict[str, object]) -> tuple[object, ...]:
    return tuple(row[column] for column in [*GROUP_KEYS, "repetition"])


def run_tasks(tasks: list[dict[str, object]], output_dir: Path, workers: int) -> pd.DataFrame:
    output_dir.mkdir(parents=True, exist_ok=True)
    partial_path = output_dir / "calibration_ledger.partial.csv"
    rows: list[dict[str, object]] = []
    completed_keys: set[tuple[object, ...]] = set()
    if partial_path.is_file():
        partial = pd.read_csv(partial_path)
        rows = partial.to_dict(orient="records")
        completed_keys = {_task_key(row) for row in rows}
        tasks = [task for task in tasks if _task_key(task) not in completed_keys]
        print(f"resuming={len(completed_keys)} remaining={len(tasks)}", flush=True)

    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(_run_cell, task) for task in tasks]
        for completed, future in enumerate(as_completed(futures), start=1):
            rows.append(future.result())
            if completed % 25 == 0 or completed == len(futures):
                pd.DataFrame(rows).to_csv(partial_path, index=False)
                print(f"completed={completed}/{len(futures)}", flush=True)
    return pd.DataFrame(rows).sort_values([*GROUP_KEYS, "repetition"], ignore_index=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Outcome-blind design-matched calibration for MBE-3 GPU follow-ups"
    )
    parser.add_argument("--stage", choices=("screen", "confirm"), required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--screen-selection", type=Path)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--smoke", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.workers < 1:
        raise ValueError("workers must be positive")
    repetitions = 2 if args.smoke else REPETITIONS
    permutations = 19 if args.smoke else PERMUTATIONS
    refit_bootstrap = 20 if args.smoke else REFIT_BOOTSTRAP

    selected = None
    if args.stage == "confirm":
        if args.screen_selection is None:
            raise ValueError("confirm stage requires --screen-selection")
        selection = json.loads(args.screen_selection.read_text(encoding="utf-8"))
        if selection.get("protocol_id") != PROTOCOL_ID or selection.get("stage") != "screen":
            raise ValueError("screen selection does not match the frozen protocol")
        if bool(selection.get("smoke", False)) != bool(args.smoke):
            raise ValueError("screen selection smoke status does not match this run")
        selected = selection["selections"]
        if not any(selected.values()):
            raise RuntimeError("screen selected no finalists; protected analysis must abstain")

    tasks = _task_grid(
        args.stage,
        repetitions,
        permutations,
        refit_bootstrap,
        selected,
        args.smoke,
    )
    if not tasks:
        raise RuntimeError("no calibration tasks were selected")
    ledger = run_tasks(tasks, args.output_dir, args.workers)
    expected = len(tasks)
    if len(ledger) != expected or ledger.duplicated([*GROUP_KEYS, "repetition"]).any():
        raise RuntimeError("calibration ledger failed row-count or duplicate-key gate")
    summary = summarize(ledger)
    ledger.to_csv(args.output_dir / "calibration_ledger.csv", index=False)
    summary.to_csv(args.output_dir / "calibration_summary.csv", index=False)

    manifest = {
        "protocol_id": PROTOCOL_ID,
        "stage": args.stage,
        "smoke": args.smoke,
        "planned_rows": expected,
        "observed_rows": len(ledger),
        "repetitions": repetitions,
        "permutations": permutations,
        "refit_bootstrap": refit_bootstrap,
        "icc_levels": [0.30] if args.smoke else list(ICC_LEVELS),
        "signal_effects": [0.50] if args.smoke else list(SIGNAL_EFFECTS),
        "null_scenarios": ["independent_null"] if args.smoke else list(NULL_SCENARIOS),
        "signal_scenarios": list(SIGNAL_SCENARIOS),
        "designs": {scope: len(get_design(scope).frame) for scope in ("image", "text")},
        "protected_result_csv_read": False,
    }
    (args.output_dir / "run_manifest.json").write_text(
        json.dumps(manifest, indent=2, allow_nan=False), encoding="utf-8"
    )
    if args.stage == "screen":
        decision = select_screen_finalists(summary)
        decision["smoke"] = args.smoke
        if args.smoke:
            decision["selections"] = {"image:B1_design": ["additive_d4"]}
            decision["smoke_forced_selection"] = True
            decision["smoke_warning"] = (
                "Forced solely to exercise confirmation; never eligible to unlock analysis."
            )
        decision_name = "screen_selection.json"
    else:
        decision = confirm_eligibility(summary)
        decision["smoke"] = args.smoke
        for key, finalists in selected.items():
            if key not in decision["opening_decisions"]:
                decision["opening_decisions"][key] = {
                    "open_protected_analysis": False,
                    "selected_primary_candidate": None,
                    "eligible_candidates": [],
                    "decision": "abstain",
                    "reason": (
                        "screen-selected-no-finalist"
                        if not finalists
                        else "confirmation-result-missing"
                    ),
                }
        if args.smoke:
            for opening in decision["opening_decisions"].values():
                opening.update(
                    {
                        "open_protected_analysis": False,
                        "selected_primary_candidate": None,
                        "eligible_candidates": [],
                        "decision": "smoke-only",
                    }
                )
        decision_name = "FINAL_ELIGIBILITY.json"
    (args.output_dir / decision_name).write_text(
        json.dumps(decision, indent=2, allow_nan=False), encoding="utf-8"
    )
    print(json.dumps({"manifest": manifest, "decision": decision}, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
