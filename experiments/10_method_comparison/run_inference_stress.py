from __future__ import annotations

import argparse
from pathlib import Path
import sys

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from mbe_eval import cross_fitted_audit, make_calibration_ledger, refit_bootstrap_audit  # noqa: E402


SCENARIOS = {
    "null_metric": False,
    "nonlinear_proxy": False,
    "heteroskedastic_null": False,
    "clustered_null": False,
    "genuine_increment": True,
}
NUISANCE_MODELS = ("polynomial_ridge", "polynomial_ridge_interactions")


def wilson_interval(successes: int, total: int, z: float = 1.96) -> tuple[float, float]:
    if total <= 0:
        raise ValueError("total must be positive")
    rate = successes / total
    denominator = 1.0 + z**2 / total
    center = (rate + z**2 / (2.0 * total)) / denominator
    half_width = z * np.sqrt(rate * (1.0 - rate) / total + z**2 / (4.0 * total**2)) / denominator
    return float(center - half_width), float(center + half_width)


def run_refit_stress(
    *, repetitions: int, sample_sizes: list[int], refit_draws: int, permutations: int, seed: int
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for n_index, n in enumerate(sample_sizes):
        for repetition in range(repetitions):
            repetition_seed = seed + n_index * 1_000_003 + repetition * 10_007
            ledger = make_calibration_ledger(n=n, seed=repetition_seed)
            for scenario_index, (scenario, expected) in enumerate(SCENARIOS.items()):
                frame = ledger.loc[ledger["scenario"] == scenario].copy()
                for nuisance_index, nuisance_model in enumerate(NUISANCE_MODELS):
                    result = refit_bootstrap_audit(
                        frame,
                        "metric",
                        "target",
                        ["baseline"],
                        group_col="config_id",
                        degree=6,
                        nuisance_model=nuisance_model,
                        refit_bootstrap=refit_draws,
                        permutations=permutations,
                        seed=(
                            repetition_seed
                            + scenario_index * 1_009
                            + nuisance_index * 101
                        ),
                    )
                    rows.append(
                        {
                            "sample_size": n,
                            "repetition": repetition,
                            "scenario": scenario,
                            "expected_increment": expected,
                            "nuisance_model": nuisance_model,
                            "residual_p": result["residual_p"],
                            "delta_mse": result["delta_mse"],
                            "refit_delta_mse_ci_low": result["refit_delta_mse_ci_low"],
                            "joint_supported": result["refit_increment_classification"]
                            == "increment-supported",
                            "predictive_supported": result["refit_delta_mse_ci_low"] > 0.0,
                        }
                    )
    return pd.DataFrame(rows)


def make_block_null(kind: str, seed: int) -> tuple[pd.DataFrame, str | None]:
    rng = np.random.default_rng(seed)
    block_sizes = [50, 50, 50, 50] if kind != "unequal_blocks" else [20, 35, 60, 85]
    block = np.concatenate([np.repeat(index, size) for index, size in enumerate(block_sizes)])
    n = len(block)
    baseline = rng.normal(size=n)
    metric_scale = np.ones(n)
    target_scale = np.ones(n)
    if kind == "heteroskedastic":
        metric_scale = np.exp(np.clip(0.45 * baseline, -1.0, 1.0))
        target_scale = np.exp(np.clip(-0.35 * baseline, -1.0, 1.0))
    block_metric = np.array([-2.0, -0.5, 0.7, 2.2])[block]
    block_target = np.array([-1.7, -0.3, 0.9, 2.0])[block]
    frame = pd.DataFrame(
        {
            "block": block.astype(str),
            "baseline": baseline,
            "metric": block_metric + metric_scale * rng.normal(size=n),
            "target": block_target + baseline + target_scale * rng.normal(size=n),
        }
    )
    if kind != "clustered":
        return frame, None

    frame["config_id"] = np.repeat(np.arange(n // 2), 2).astype(str)
    shared_metric = rng.normal(size=n // 2)
    shared_target = rng.normal(size=n // 2)
    frame["metric"] += np.repeat(shared_metric, 2)
    frame["target"] += np.repeat(shared_target, 2)
    return frame, "config_id"


def run_block_stress(*, repetitions: int, permutations: int, seed: int) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for kind_index, kind in enumerate(
        ("homoskedastic", "heteroskedastic", "unequal_blocks", "clustered")
    ):
        for repetition in range(repetitions):
            run_seed = seed + kind_index * 1_000_003 + repetition * 10_007
            frame, group_col = make_block_null(kind, run_seed)
            result = cross_fitted_audit(
                frame,
                "metric",
                "target",
                ["baseline", "block"],
                group_col=group_col,
                permutation_block_col="block",
                degree=6,
                nuisance_model="polynomial_ridge_interactions",
                permutations=permutations,
                bootstrap=0,
                seed=run_seed,
            )
            rows.append(
                {
                    "structure": kind,
                    "repetition": repetition,
                    "independence_units": result["independence_units"],
                    "residual_r": result["residual_r"],
                    "residual_p": result["residual_p"],
                    "rejected_05": result["residual_p"] <= 0.05,
                }
            )
    return pd.DataFrame(rows)


def summarize_refit(ledger: pd.DataFrame) -> pd.DataFrame:
    return (
        ledger.groupby(
            ["sample_size", "scenario", "expected_increment", "nuisance_model"],
            as_index=False,
        )
        .agg(
            repetitions=("repetition", "size"),
            joint_support_rate=("joint_supported", "mean"),
            predictive_support_rate=("predictive_supported", "mean"),
            median_delta_mse=("delta_mse", "median"),
            median_refit_ci_low=("refit_delta_mse_ci_low", "median"),
        )
    )


def summarize_blocks(ledger: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for structure, frame in ledger.groupby("structure", sort=True):
        rejected = int(frame["rejected_05"].sum())
        total = len(frame)
        low, high = wilson_interval(rejected, total)
        rows.append(
            {
                "structure": structure,
                "repetitions": total,
                "rejections": rejected,
                "rejection_rate": rejected / total,
                "wilson_95_low": low,
                "wilson_95_high": high,
            }
        )
    return pd.DataFrame(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Stress-test MBE inference on known nulls.")
    parser.add_argument("--refit-repetitions", type=int, default=20)
    parser.add_argument("--sample-sizes", type=int, nargs="+", default=[100, 200])
    parser.add_argument("--refit-draws", type=int, default=39)
    parser.add_argument("--refit-permutations", type=int, default=99)
    parser.add_argument("--block-repetitions", type=int, default=500)
    parser.add_argument("--block-permutations", type=int, default=199)
    parser.add_argument("--seed", type=int, default=20260717)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    refit = run_refit_stress(
        repetitions=args.refit_repetitions,
        sample_sizes=args.sample_sizes,
        refit_draws=args.refit_draws,
        permutations=args.refit_permutations,
        seed=args.seed,
    )
    blocks = run_block_stress(
        repetitions=args.block_repetitions,
        permutations=args.block_permutations,
        seed=args.seed + 9_000_001,
    )
    refit_summary = summarize_refit(refit)
    block_summary = summarize_blocks(blocks)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    refit.to_csv(args.output_dir / "inference_stress_refit_ledger.csv", index=False)
    refit_summary.to_csv(args.output_dir / "inference_stress_refit_summary.csv", index=False)
    blocks.to_csv(args.output_dir / "inference_stress_block_ledger.csv", index=False)
    block_summary.to_csv(args.output_dir / "inference_stress_block_summary.csv", index=False)

    lines = [
        "# Inference Stress Test",
        "",
        "This known-truth matrix separates the refit predictive-improvement interval from the residual-permutation diagnostic.",
        "",
        "## Refit Decisions",
        "",
        "| n | Scenario | Nuisance | Joint support | Predictive support |",
        "|---:|---|---|---:|---:|",
    ]
    for _, row in refit_summary.iterrows():
        lines.append(
            f"| {int(row['sample_size'])} | {row['scenario']} | {row['nuisance_model']} | "
            f"{row['joint_support_rate']:.3f} | {row['predictive_support_rate']:.3f} |"
        )
    lines.extend(
        [
            "",
            "## Residual-Permutation Nulls",
            "",
            "| Structure | Rejections | Rate | Wilson 95% interval |",
            "|---|---:|---:|---:|",
        ]
    )
    for _, row in block_summary.iterrows():
        lines.append(
            f"| {row['structure']} | {int(row['rejections'])}/{int(row['repetitions'])} | "
            f"{row['rejection_rate']:.3f} | [{row['wilson_95_low']:.3f}, {row['wilson_95_high']:.3f}] |"
        )
    lines.extend(
        [
            "",
            "Residual permutation is retained as a diagnostic unless all relevant known-null structures are compatible with nominal error. The primary MBE decision is learner-relative predictive improvement under full refitting and preregistered nuisance-family agreement.",
            "",
        ]
    )
    (args.output_dir / "INFERENCE_STRESS_TEST.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )
    print(refit_summary.to_string(index=False))
    print(block_summary.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
