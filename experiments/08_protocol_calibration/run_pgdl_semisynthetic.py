from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from mbe_eval import audit_metric, cross_fitted_audit


def _standardize(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    scale = float(np.std(values))
    if not np.isfinite(scale) or scale < 1e-12:
        return np.zeros_like(values)
    return (values - np.mean(values)) / scale


def _baseline_score(frame: pd.DataFrame, controls: list[str]) -> np.ndarray:
    score = np.zeros(len(frame), dtype=float)
    for index, control in enumerate(controls):
        series = frame[control]
        if is_numeric_dtype(series):
            component = series.rank(method="average", pct=True).to_numpy(dtype=float)
        else:
            levels = {value: i for i, value in enumerate(sorted(series.astype(str).unique()))}
            component = series.astype(str).map(levels).to_numpy(dtype=float)
            if len(levels) > 1:
                component /= len(levels) - 1
        component = 2.0 * component - 1.0
        weight = 1.0 / np.sqrt(index + 1.0)
        score += weight * (component + 0.35 * np.square(component))
    return _standardize(score)


def _audit_case(
    frame: pd.DataFrame,
    controls: list[str],
    *,
    seed: int,
    permutations: int,
    bootstrap: int,
    nuisance_model: str,
    degree: int,
) -> dict[str, object]:
    legacy = audit_metric(frame, "synthetic_metric", "synthetic_target", controls)
    crossfit = cross_fitted_audit(
        frame,
        "synthetic_metric",
        "synthetic_target",
        controls,
        degree=degree,
        permutations=permutations,
        bootstrap=bootstrap,
        nuisance_model=nuisance_model,
        seed=seed,
    )
    return {
        "raw_r": legacy["raw_r"],
        "raw_p": legacy["raw_p"],
        "partial_r": legacy["partial_r"],
        "partial_p": legacy["partial_p"],
        "crossfit_residual_r": crossfit["residual_r"],
        "crossfit_residual_p": crossfit["residual_p"],
        "delta_mse": crossfit["delta_mse"],
        "delta_mse_ci_low": crossfit["delta_mse_ci_low"],
        "delta_mse_ci_high": crossfit["delta_mse_ci_high"],
        "relative_mse_improvement": crossfit["relative_mse_improvement"],
    }


def _wilson(successes: int, total: int) -> tuple[float, float]:
    z = 1.959963984540054
    proportion = successes / total
    denominator = 1.0 + z * z / total
    center = (proportion + z * z / (2.0 * total)) / denominator
    half = z * np.sqrt(
        proportion * (1.0 - proportion) / total
        + z * z / (4.0 * total * total)
    ) / denominator
    return float(center - half), float(center + half)


def run_semisynthetic(
    ledger: pd.DataFrame,
    plan: dict[str, object],
    *,
    repetitions: int,
    permutations: int,
    bootstrap: int,
    nuisance_model: str,
    degree: int,
    alpha: float,
    seed: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    development = ledger.loc[ledger["task"].isin(["task1", "task2"])].copy()
    rows: list[dict[str, object]] = []
    sign_by_task = {"task1": 1.0, "task2": -1.0}

    for repetition in range(repetitions):
        task_specialist_frames: list[pd.DataFrame] = []
        for task_index, task in enumerate(("task1", "task2")):
            frame = development.loc[development["task"] == task].reset_index(drop=True)
            controls = list(plan["task_controls"][task])
            score = _baseline_score(frame, controls)
            actual_target = _standardize(
                frame["generalization_gap_accuracy"].to_numpy(dtype=float)
            )
            run_seed = seed + repetition * 10_007 + task_index * 1_000_003
            rng = np.random.default_rng(run_seed)
            latent = rng.normal(size=len(frame))

            cases = {
                "real_structure_null": (
                    actual_target,
                    rng.normal(size=len(frame)),
                    False,
                    0,
                ),
                "real_design_proxy": (
                    score + rng.normal(0, 0.45, len(frame)),
                    score + rng.normal(0, 0.20, len(frame)),
                    False,
                    0,
                ),
                "injected_increment": (
                    actual_target + 0.80 * latent + rng.normal(0, 0.35, len(frame)),
                    latent + rng.normal(0, 0.15, len(frame)),
                    True,
                    1,
                ),
                "task_specialist": (
                    0.50 * score
                    + sign_by_task[task] * latent
                    + rng.normal(0, 0.35, len(frame)),
                    latent + rng.normal(0, 0.15, len(frame)),
                    True,
                    int(sign_by_task[task]),
                ),
            }
            for case_index, (
                case_name,
                (target, metric, expected_signal, direction),
            ) in enumerate(cases.items()):
                synthetic = frame.copy()
                synthetic["synthetic_target"] = target
                synthetic["synthetic_metric"] = metric
                result = _audit_case(
                    synthetic,
                    controls,
                    seed=run_seed + case_index * 101,
                    permutations=permutations,
                    bootstrap=bootstrap,
                    nuisance_model=nuisance_model,
                    degree=degree,
                )
                residual_reject = bool(result["crossfit_residual_p"] <= alpha)
                positive_delta = bool(result["delta_mse"] > 0.0)
                delta_ci_positive = bool(result["delta_mse_ci_low"] > 0.0)
                sign_correct = bool(
                    direction == 0
                    or np.sign(result["crossfit_residual_r"]) == direction
                )
                rows.append(
                    {
                        "scope": task,
                        "case": case_index,
                        "case_name": case_name,
                        "expected_signal": expected_signal,
                        "expected_direction": direction,
                        "n": len(synthetic),
                        "polynomial_degree": degree,
                        "nuisance_model": nuisance_model,
                        "repetition": repetition,
                        "seed": run_seed,
                        **result,
                        "crossfit_residual_reject": residual_reject,
                        "positive_delta_mse": positive_delta,
                        "delta_ci_positive": delta_ci_positive,
                        "joint_increment_decision": residual_reject
                        and delta_ci_positive,
                        "sign_correct": sign_correct,
                    }
                )
                if case_name == "task_specialist":
                    task_specialist_frames.append(
                        synthetic[["task", "synthetic_target", "synthetic_metric"]]
                    )

        minimum = min(len(frame) for frame in task_specialist_frames)
        balanced = pd.concat(
            [
                frame.sample(n=minimum, random_state=seed + repetition + index)
                for index, frame in enumerate(task_specialist_frames)
            ],
            ignore_index=True,
        )
        pooled_result = _audit_case(
            balanced,
            ["task"],
            seed=seed + repetition * 10_007 + 9_000_019,
            permutations=permutations,
            bootstrap=bootstrap,
            nuisance_model=nuisance_model,
            degree=degree,
        )
        pooled_reject = bool(pooled_result["crossfit_residual_p"] <= alpha)
        pooled_delta_ci_positive = bool(pooled_result["delta_mse_ci_low"] > 0.0)
        rows.append(
            {
                "scope": "balanced_pool",
                "case": 4,
                "case_name": "opposite_sign_task_specialists",
                "expected_signal": "heterogeneous",
                "expected_direction": 0,
                "n": len(balanced),
                "polynomial_degree": degree,
                "nuisance_model": nuisance_model,
                "repetition": repetition,
                "seed": seed + repetition * 10_007 + 9_000_019,
                **pooled_result,
                "crossfit_residual_reject": pooled_reject,
                "positive_delta_mse": bool(pooled_result["delta_mse"] > 0.0),
                "delta_ci_positive": pooled_delta_ci_positive,
                "joint_increment_decision": pooled_reject
                and pooled_delta_ci_positive,
                "sign_correct": True,
            }
        )

    results = pd.DataFrame(rows)
    summary_rows: list[dict[str, object]] = []
    for (
        scope,
        case_name,
        expected_signal,
        polynomial_degree,
        nuisance_model,
    ), group in results.groupby(
        [
            "scope",
            "case_name",
            "expected_signal",
            "polynomial_degree",
            "nuisance_model",
        ],
        sort=True,
    ):
        total = len(group)
        decisions = int(group["joint_increment_decision"].sum())
        low, high = _wilson(decisions, total)
        summary_rows.append(
            {
                "scope": scope,
                "case_name": case_name,
                "expected_signal": expected_signal,
                "polynomial_degree": polynomial_degree,
                "nuisance_model": nuisance_model,
                "n": int(group["n"].iloc[0]),
                "repetitions": total,
                "joint_decision_rate": decisions / total,
                "joint_decision_ci_low": low,
                "joint_decision_ci_high": high,
                "sign_correct_rate": group["sign_correct"].mean(),
                "median_residual_r": group["crossfit_residual_r"].median(),
                "median_delta_mse": group["delta_mse"].median(),
            }
        )
    return results, pd.DataFrame(summary_rows)


def write_report(summary: pd.DataFrame, path: Path, alpha: float) -> None:
    lines = [
        "# PGDL Semi-Synthetic Calibration",
        "",
        "This experiment preserves the real Tasks 1-2 sample sizes and hyperparameter geometry while injecting metrics whose role is known by construction. It uses no protected PGDL metric outputs.",
        "",
        "| Scope | Case | Expected signal | Nuisance | Degree | n | Repetitions | Joint decision [95% CI] | Sign correct | Median residual rho | Median Delta MSE |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in summary.iterrows():
        lines.append(
            f"| {row['scope']} | `{row['case_name']}` | {row['expected_signal']} | "
            f"{row['nuisance_model']} | {int(row['polynomial_degree'])} | {int(row['n'])} | {int(row['repetitions'])} | "
            f"{row['joint_decision_rate']:.3f} [{row['joint_decision_ci_low']:.3f}, {row['joint_decision_ci_high']:.3f}] | "
            f"{row['sign_correct_rate']:.3f} | {row['median_residual_r']:.3f} | "
            f"{row['median_delta_mse']:.4f} |"
        )
    lines.extend(
        [
            "",
            "The joint decision requires a residual permutation p-value at or below "
            f"{alpha:.3f} and a 95% out-of-fold Delta-MSE interval entirely above zero. The balanced pooled specialist case deliberately combines opposite task-specific directions; it is a heterogeneity diagnostic, not a conditional-null false-positive test.",
            "",
            "These results validate behavior on the observed design distribution, not on unseen checkpoint metrics. They cannot substitute for Tasks 4-5 validation or Tasks 6-9 protected transfer.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run PGDL semi-synthetic calibration.")
    parser.add_argument("ledger", type=Path)
    parser.add_argument("plan", type=Path)
    parser.add_argument("--repetitions", type=int, default=100)
    parser.add_argument("--permutations", type=int, default=199)
    parser.add_argument("--bootstrap", type=int, default=499)
    parser.add_argument(
        "--nuisance-model",
        choices=(
            "polynomial_ridge",
            "polynomial_ridge_interactions",
            "extra_trees",
        ),
        default="polynomial_ridge",
    )
    parser.add_argument("--degrees", default="2,6")
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--seed", type=int, default=20260716)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    if args.repetitions < 20:
        raise ValueError("semi-synthetic calibration requires at least 20 repetitions")
    ledger = pd.read_csv(args.ledger)
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    degrees = tuple(int(value.strip()) for value in args.degrees.split(",") if value.strip())
    if not degrees or any(degree < 1 for degree in degrees):
        raise ValueError("--degrees must contain positive comma-separated integers")
    result_frames = []
    summary_frames = []
    for degree in degrees:
        results, summary = run_semisynthetic(
            ledger,
            plan,
            repetitions=args.repetitions,
            permutations=args.permutations,
            bootstrap=args.bootstrap,
            nuisance_model=args.nuisance_model,
            degree=degree,
            alpha=args.alpha,
            seed=args.seed + degree * 1_000_003,
        )
        result_frames.append(results)
        summary_frames.append(summary)
    results = pd.concat(result_frames, ignore_index=True)
    summary = pd.concat(summary_frames, ignore_index=True)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    results.to_csv(args.output_dir / "pgdl_semisynthetic_ledger.csv", index=False)
    summary.to_csv(args.output_dir / "pgdl_semisynthetic_summary.csv", index=False)
    write_report(summary, args.output_dir / "PGDL_SEMISYNTHETIC_CALIBRATION.md", args.alpha)
    print(summary.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
