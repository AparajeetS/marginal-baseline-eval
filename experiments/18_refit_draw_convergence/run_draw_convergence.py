from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import json
import math
from pathlib import Path
import sys

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from mbe_eval import make_calibration_ledger, refit_bootstrap_audit  # noqa: E402


SCENARIOS = {
    "null_metric": False,
    "nonlinear_proxy": False,
    "heteroskedastic_null": False,
    "clustered_null": False,
    "genuine_increment": True,
}
NUISANCE_MODELS = ("polynomial_ridge", "polynomial_ridge_interactions")


def wilson_interval(successes: int, total: int) -> tuple[float, float]:
    if total <= 0:
        return math.nan, math.nan
    z = 1.96
    rate = successes / total
    denominator = 1.0 + z**2 / total
    center = (rate + z**2 / (2.0 * total)) / denominator
    half = (
        z
        * math.sqrt(rate * (1.0 - rate) / total + z**2 / (4.0 * total**2))
        / denominator
    )
    return center - half, center + half


def run_repetition(payload: dict[str, object]) -> list[dict[str, object]]:
    repetition = int(payload["repetition"])
    simulation_seed = int(payload["seed"]) + repetition * 100_003
    ledger = make_calibration_ledger(n=int(payload["n"]), seed=simulation_seed)
    rows: list[dict[str, object]] = []

    for scenario_index, (scenario, expected) in enumerate(SCENARIOS.items()):
        frame = ledger.loc[ledger["scenario"].eq(scenario)].copy()
        for nuisance_index, nuisance_model in enumerate(NUISANCE_MODELS):
            analysis_seed = (
                int(payload["seed"])
                + repetition * 1_000_003
                + scenario_index * 10_007
                + nuisance_index * 1_009
            )
            for draws in payload["draws"]:
                base = {
                    "repetition": repetition,
                    "scenario": scenario,
                    "expected_increment": expected,
                    "nuisance_model": nuisance_model,
                    "refit_draws": int(draws),
                    "simulation_seed": simulation_seed,
                    "analysis_seed": analysis_seed,
                }
                try:
                    result = refit_bootstrap_audit(
                        frame,
                        "metric",
                        "target",
                        ["baseline"],
                        group_col="config_id",
                        degree=6,
                        nuisance_model=nuisance_model,
                        refit_bootstrap=int(draws),
                        permutations=int(payload["permutations"]),
                        seed=analysis_seed,
                    )
                    rows.append(
                        base
                        | {
                            "status": "estimated",
                            "delta_mse": result["delta_mse"],
                            "refit_delta_mse_ci_low": result[
                                "refit_delta_mse_ci_low"
                            ],
                            "refit_delta_mse_ci_high": result[
                                "refit_delta_mse_ci_high"
                            ],
                            "residual_p": result["residual_p"],
                            "predictive_supported": result[
                                "refit_delta_mse_ci_low"
                            ]
                            > 0.0,
                            "joint_supported": result[
                                "refit_increment_classification"
                            ]
                            == "increment-supported",
                        }
                    )
                except (RuntimeError, ValueError, np.linalg.LinAlgError) as error:
                    rows.append(base | {"status": f"not_estimable: {error}"})
    return rows


def summarize(ledger: pd.DataFrame) -> pd.DataFrame:
    rows = []
    keys = [
        "scenario",
        "expected_increment",
        "nuisance_model",
        "refit_draws",
    ]
    for key, frame in ledger.groupby(keys, sort=True, dropna=False):
        estimated = frame.loc[frame["status"].eq("estimated")]
        predictive = int(estimated["predictive_supported"].sum())
        joint = int(estimated["joint_supported"].sum())
        predictive_low, predictive_high = wilson_interval(
            predictive, len(estimated)
        )
        joint_low, joint_high = wilson_interval(joint, len(estimated))
        rows.append(
            dict(zip(keys, key, strict=True))
            | {
                "repetitions": len(frame),
                "estimable": len(estimated),
                "predictive_support_rate": predictive / len(estimated)
                if len(estimated)
                else math.nan,
                "predictive_wilson_95_low": predictive_low,
                "predictive_wilson_95_high": predictive_high,
                "joint_support_rate": joint / len(estimated)
                if len(estimated)
                else math.nan,
                "joint_wilson_95_low": joint_low,
                "joint_wilson_95_high": joint_high,
                "median_ci_low": estimated["refit_delta_mse_ci_low"].median(),
            }
        )
    return pd.DataFrame(rows)


def convergence_table(ledger: pd.DataFrame) -> pd.DataFrame:
    estimated = ledger.loc[ledger["status"].eq("estimated")].copy()
    reference_draws = int(estimated["refit_draws"].max())
    key = ["repetition", "scenario", "nuisance_model"]
    reference = estimated.loc[
        estimated["refit_draws"].eq(reference_draws),
        [*key, "predictive_supported", "refit_delta_mse_ci_low"],
    ].rename(
        columns={
            "predictive_supported": "reference_supported",
            "refit_delta_mse_ci_low": "reference_ci_low",
        }
    )
    compared = estimated.loc[estimated["refit_draws"].lt(reference_draws)].merge(
        reference,
        on=key,
        validate="many_to_one",
    )
    compared["agrees"] = compared["predictive_supported"].eq(
        compared["reference_supported"]
    )
    compared["positive_to_negative"] = (
        compared["predictive_supported"]
        & ~compared["reference_supported"]
    )
    compared["negative_to_positive"] = (
        ~compared["predictive_supported"]
        & compared["reference_supported"]
    )
    compared["absolute_ci_low_difference"] = (
        compared["refit_delta_mse_ci_low"] - compared["reference_ci_low"]
    ).abs()

    rows = []
    group_keys = ["scenario", "nuisance_model", "refit_draws"]
    for group, frame in compared.groupby(group_keys, sort=True):
        rows.append(
            dict(zip(group_keys, group, strict=True))
            | {
                "paired_repetitions": len(frame),
                "reference_draws": reference_draws,
                "decision_agreement_rate": frame["agrees"].mean(),
                "positive_to_negative_rate": frame[
                    "positive_to_negative"
                ].mean(),
                "negative_to_positive_rate": frame[
                    "negative_to_positive"
                ].mean(),
                "median_absolute_ci_low_difference": frame[
                    "absolute_ci_low_difference"
                ].median(),
                "max_absolute_ci_low_difference": frame[
                    "absolute_ci_low_difference"
                ].max(),
            }
        )
    return pd.DataFrame(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run paired MBE refit-draw convergence calibration."
    )
    parser.add_argument("--repetitions", type=int, default=100)
    parser.add_argument("--n", type=int, default=150)
    parser.add_argument(
        "--draws", type=int, nargs="+", default=[99, 199, 499, 999]
    )
    parser.add_argument("--permutations", type=int, default=199)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--seed", type=int, default=20260731)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if sorted(set(args.draws)) != sorted(args.draws):
        raise ValueError("draw counts must be unique and sorted")
    if min(args.draws) < 20:
        raise ValueError("every refit draw count must be at least 20")
    if args.repetitions <= 0 or args.workers <= 0:
        raise ValueError("repetitions and workers must be positive")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    partial_path = args.output_dir / "draw_convergence.partial.csv"
    expected_per_repetition = (
        len(SCENARIOS) * len(NUISANCE_MODELS) * len(args.draws)
    )
    all_rows: list[dict[str, object]] = []
    completed_repetitions: set[int] = set()
    if partial_path.is_file():
        partial = pd.read_csv(partial_path)
        counts = partial.groupby("repetition").size()
        completed_repetitions = {
            int(repetition)
            for repetition, count in counts.items()
            if count == expected_per_repetition
        }
        partial = partial.loc[
            partial["repetition"].astype(int).isin(completed_repetitions)
        ]
        partial = partial.drop_duplicates(
            ["repetition", "scenario", "nuisance_model", "refit_draws"],
            keep="last",
        )
        all_rows = partial.to_dict(orient="records")

    payloads = [
        {
            "repetition": repetition,
            "n": args.n,
            "draws": args.draws,
            "permutations": args.permutations,
            "seed": args.seed,
        }
        for repetition in range(args.repetitions)
        if repetition not in completed_repetitions
    ]
    print(
        f"resuming_repetitions={len(completed_repetitions)} "
        f"remaining={len(payloads)}",
        flush=True,
    )

    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        futures = [executor.submit(run_repetition, payload) for payload in payloads]
        for completed, future in enumerate(as_completed(futures), start=1):
            all_rows.extend(future.result())
            if completed % 2 == 0 or completed == len(futures):
                pd.DataFrame(all_rows).to_csv(partial_path, index=False)
                print(f"completed={completed}/{len(futures)}", flush=True)

    ledger = pd.DataFrame(all_rows).sort_values(
        ["repetition", "scenario", "nuisance_model", "refit_draws"]
    )
    duplicate_key = [
        "repetition",
        "scenario",
        "nuisance_model",
        "refit_draws",
    ]
    if ledger.duplicated(duplicate_key).any():
        raise ValueError("duplicate paired convergence cells")
    expected_rows = args.repetitions * expected_per_repetition
    if len(ledger) != expected_rows:
        raise ValueError(f"expected {expected_rows} rows, found {len(ledger)}")

    summary = summarize(ledger)
    convergence = convergence_table(ledger)
    ledger.to_csv(args.output_dir / "draw_convergence_ledger.csv", index=False)
    summary.to_csv(args.output_dir / "draw_convergence_summary.csv", index=False)
    convergence.to_csv(
        args.output_dir / "draw_convergence_comparison.csv", index=False
    )
    manifest = {
        "repetitions": args.repetitions,
        "n": args.n,
        "scenarios": list(SCENARIOS),
        "nuisance_models": list(NUISANCE_MODELS),
        "draws": args.draws,
        "permutations": args.permutations,
        "degree": 6,
        "seed": args.seed,
        "rows": len(ledger),
        "paired_reference_draws": max(args.draws),
    }
    (args.output_dir / "run_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    print(summary.to_string(index=False))
    print(convergence.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
