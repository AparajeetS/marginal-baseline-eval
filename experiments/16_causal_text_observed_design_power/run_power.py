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

from mbe_eval import refit_bootstrap_audit  # noqa: E402


METRICS = [
    "prediction_confidence",
    "prediction_entropy",
    "prediction_margin",
    "gradient_norm",
    "empirical_fisher_trace",
    "fim_erank",
    "fim_norm",
    "feature_erank",
    "parameter_l2",
    "distance_from_initialization_l2",
    "relative_distance_from_initialization",
    "update_to_weight_ratio",
    "sharpness_random_perturbation",
]
BASELINES = {
    "B1_design": ["model_size", "learning_rate", "weight_decay", "dropout"],
    "B2_training_state": [
        "model_size",
        "learning_rate",
        "weight_decay",
        "dropout",
        "final_train_batch_loss",
    ],
    "B3_validation": [
        "model_size",
        "learning_rate",
        "weight_decay",
        "dropout",
        "final_train_batch_loss",
        "val_loss",
    ],
}
NUISANCE_MODELS = ("polynomial_ridge", "polynomial_ridge_interactions")


def one_way_icc(frame: pd.DataFrame, value: str, group: str = "config_id") -> float:
    grouped = frame.groupby(group, sort=True)[value]
    sizes = grouped.size().to_numpy()
    if len(np.unique(sizes)) != 1:
        raise ValueError("ICC calibration requires a balanced group design")
    k = int(sizes[0])
    means = grouped.mean().to_numpy(dtype=float)
    grand = float(frame[value].mean())
    ms_between = k * float(np.sum(np.square(means - grand))) / (len(means) - 1)
    within_ss = float(
        frame.groupby(group, sort=True)[value]
        .apply(lambda values: np.sum(np.square(values - values.mean())))
        .sum()
    )
    ms_within = within_ss / (len(frame) - len(means))
    denominator = ms_between + (k - 1) * ms_within
    estimate = (ms_between - ms_within) / denominator if denominator > 0 else 0.0
    return float(np.clip(estimate, 0.01, 0.99))


def select_reliability_tiers(frame: pd.DataFrame) -> pd.DataFrame:
    estimates = pd.DataFrame(
        [{"source_metric": metric, "icc": one_way_icc(frame, metric)} for metric in METRICS]
    ).sort_values(["icc", "source_metric"], ignore_index=True)
    rows = []
    for tier, quantile in (("low", 0.1), ("median", 0.5), ("high", 0.9)):
        target = float(estimates["icc"].quantile(quantile))
        selected = estimates.iloc[(estimates["icc"] - target).abs().argmin()]
        rows.append(
            {
                "reliability_tier": tier,
                "quantile": quantile,
                "source_metric": selected["source_metric"],
                "icc": float(selected["icc"]),
            }
        )
    return pd.DataFrame(rows)


def wilson_interval(successes: int, total: int) -> tuple[float, float]:
    if total <= 0:
        return math.nan, math.nan
    z = 1.96
    rate = successes / total
    denominator = 1.0 + z**2 / total
    center = (rate + z**2 / (2.0 * total)) / denominator
    half = (
        z
        * math.sqrt(rate * (1 - rate) / total + z**2 / (4 * total**2))
        / denominator
    )
    return center - half, center + half


def simulate_frame(
    source: pd.DataFrame, *, icc: float, beta: float, seed: int
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    result = source.copy()
    groups = result["config_id"].astype(str)
    unique_groups = sorted(groups.unique())
    group_latent = dict(zip(unique_groups, rng.normal(size=len(unique_groups)), strict=True))
    latent = groups.map(group_latent).to_numpy(dtype=float)
    metric = math.sqrt(icc) * latent + math.sqrt(1.0 - icc) * rng.normal(size=len(result))
    target = result["test_loss"].to_numpy(dtype=float)
    target = (target - target.mean()) / target.std(ddof=1)
    result["synthetic_metric"] = metric
    result["synthetic_target"] = target + beta * latent
    return result


def run_cell(payload: dict[str, object]) -> list[dict[str, object]]:
    source = pd.read_csv(str(payload["csv"]))
    frame = simulate_frame(
        source,
        icc=float(payload["icc"]),
        beta=float(payload["beta"]),
        seed=int(payload["simulation_seed"]),
    )
    rows = []
    for nuisance_index, nuisance in enumerate(NUISANCE_MODELS):
        try:
            result = refit_bootstrap_audit(
                frame,
                "synthetic_metric",
                "synthetic_target",
                BASELINES[str(payload["baseline"])],
                refit_bootstrap=int(payload["refit_bootstrap"]),
                permutations=int(payload["permutations"]),
                group_col="config_id",
                permutation_block_col="model_size",
                n_splits=5,
                degree=int(payload["degree"]),
                nuisance_model=nuisance,
                seed=int(payload["analysis_seed"]) + nuisance_index * 1_009,
            )
            rows.append(
                {
                    **payload,
                    "nuisance_model": nuisance,
                    "status": "estimated",
                    "delta_mse": result["delta_mse"],
                    "residual_p": result["residual_p"],
                    "refit_delta_mse_ci_low": result["refit_delta_mse_ci_low"],
                    "refit_delta_mse_ci_high": result["refit_delta_mse_ci_high"],
                    "predictive_supported": result["refit_delta_mse_ci_low"] > 0,
                    "joint_supported": result["refit_increment_classification"]
                    == "increment-supported",
                }
            )
        except (RuntimeError, ValueError, np.linalg.LinAlgError) as error:
            rows.append(
                {
                    **payload,
                    "nuisance_model": nuisance,
                    "status": f"not_estimable: {error}",
                }
            )
    return rows


def summarize(ledger: pd.DataFrame) -> pd.DataFrame:
    cell_keys = [
        "reliability_tier",
        "source_metric",
        "icc",
        "baseline",
        "beta",
        "repetition",
    ]
    consensus_rows = []
    for key, cell in ledger.groupby(cell_keys, sort=True, dropna=False):
        estimated = cell.loc[cell["status"].eq("estimated")]
        strict = len(estimated) == 2 and bool(estimated["predictive_supported"].all())
        joint = len(estimated) == 2 and bool(estimated["joint_supported"].all())
        consensus_rows.append(
            dict(zip(cell_keys, key, strict=True))
            | {
                "nuisance_models_estimated": len(estimated),
                "strict_supported": strict,
                "joint_supported": joint,
            }
        )
    consensus = pd.DataFrame(consensus_rows)
    rows = []
    summary_keys = ["reliability_tier", "source_metric", "icc", "baseline", "beta"]
    for key, cell in consensus.groupby(summary_keys, sort=True, dropna=False):
        total = len(cell)
        strict_n = int(cell["strict_supported"].sum())
        joint_n = int(cell["joint_supported"].sum())
        low, high = wilson_interval(strict_n, total)
        rows.append(
            dict(zip(summary_keys, key, strict=True))
            | {
                "repetitions": total,
                "estimable_both": int((cell["nuisance_models_estimated"] == 2).sum()),
                "strict_support_count": strict_n,
                "strict_support_rate": strict_n / total,
                "strict_wilson_95_low": low,
                "strict_wilson_95_high": high,
                "joint_support_count": joint_n,
                "joint_support_rate": joint_n / total,
            }
        )
    return pd.DataFrame(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--repetitions", type=int, default=100)
    parser.add_argument("--effects", type=float, nargs="+", default=[0.0, 0.1, 0.2, 0.3, 0.5])
    parser.add_argument("--refit-bootstrap", type=int, default=199)
    parser.add_argument("--permutations", type=int, default=99)
    parser.add_argument("--degree", type=int, default=6)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--seed", type=int, default=20260729)
    parser.add_argument("--tiers", nargs="+", default=["low", "median", "high"])
    parser.add_argument("--baselines", nargs="+", default=list(BASELINES))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source = pd.read_csv(args.csv)
    source = source.loc[source["error"].fillna("").eq("")].reset_index(drop=True)
    if source["config_id"].nunique() != 36 or len(source) != 180:
        raise ValueError("frozen power study requires exactly 180 rows and 36 configurations")
    unknown_baselines = sorted(set(args.baselines) - set(BASELINES))
    if unknown_baselines:
        raise ValueError(f"unknown baselines: {unknown_baselines}")

    tiers = select_reliability_tiers(source)
    tiers = tiers.loc[tiers["reliability_tier"].isin(args.tiers)].reset_index(drop=True)
    if set(args.tiers) != set(tiers["reliability_tier"]):
        raise ValueError("tiers must be selected from low, median, high")

    tasks = []
    task_index = 0
    for tier in tiers.to_dict(orient="records"):
        for baseline in args.baselines:
            for beta in args.effects:
                for repetition in range(args.repetitions):
                    tasks.append(
                        {
                            **tier,
                            "baseline": baseline,
                            "beta": float(beta),
                            "repetition": repetition,
                            "csv": str(args.csv.resolve()),
                            "refit_bootstrap": args.refit_bootstrap,
                            "permutations": args.permutations,
                            "degree": args.degree,
                            "simulation_seed": args.seed + task_index * 100_003,
                            "analysis_seed": args.seed + task_index * 1_000_003,
                        }
                    )
                    task_index += 1

    args.output_dir.mkdir(parents=True, exist_ok=True)
    tiers.to_csv(args.output_dir / "reliability_tiers.csv", index=False)
    partial_path = args.output_dir / "power_ledger.partial.csv"
    all_rows: list[dict[str, object]] = []
    completed_keys: set[tuple[str, str, float, int]] = set()
    if partial_path.is_file():
        partial = pd.read_csv(partial_path)
        key_columns = ["reliability_tier", "baseline", "beta", "repetition"]
        counts = partial.groupby(key_columns, dropna=False).size()
        completed_keys = {
            (str(tier), str(baseline), float(beta), int(repetition))
            for (tier, baseline, beta, repetition), count in counts.items()
            if count == len(NUISANCE_MODELS)
        }
        partial_keys = list(
            zip(
                partial["reliability_tier"].astype(str),
                partial["baseline"].astype(str),
                partial["beta"].astype(float),
                partial["repetition"].astype(int),
                strict=True,
            )
        )
        partial = partial.loc[
            [key in completed_keys for key in partial_keys]
        ].drop_duplicates(
            [*key_columns, "nuisance_model"], keep="last"
        )
        all_rows = partial.to_dict(orient="records")
        tasks = [
            task
            for task in tasks
            if (
                str(task["reliability_tier"]),
                str(task["baseline"]),
                float(task["beta"]),
                int(task["repetition"]),
            )
            not in completed_keys
        ]
        print(
            f"resuming_completed={len(completed_keys)} remaining={len(tasks)}",
            flush=True,
        )

    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        futures = [executor.submit(run_cell, task) for task in tasks]
        for completed, future in enumerate(as_completed(futures), start=1):
            all_rows.extend(future.result())
            if completed % 25 == 0 or completed == len(futures):
                pd.DataFrame(all_rows).to_csv(partial_path, index=False)
                print(f"completed={completed}/{len(futures)}", flush=True)

    ledger = pd.DataFrame(all_rows).sort_values(
        ["reliability_tier", "baseline", "beta", "repetition", "nuisance_model"]
    )
    summary = summarize(ledger)
    ledger.to_csv(args.output_dir / "power_ledger.csv", index=False)
    summary.to_csv(args.output_dir / "power_summary.csv", index=False)
    manifest = {
        "source_csv": str(args.csv),
        "rows": len(source),
        "configurations": int(source["config_id"].nunique()),
        "repetitions": args.repetitions,
        "effects": args.effects,
        "refit_bootstrap": args.refit_bootstrap,
        "permutations": args.permutations,
        "degree": args.degree,
        "workers": args.workers,
        "seed": args.seed,
        "tiers": args.tiers,
        "baselines": args.baselines,
        "primary_decision": "both nuisance-family refit Delta-MSE lower bounds above zero",
    }
    (args.output_dir / "run_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    print(summary.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
