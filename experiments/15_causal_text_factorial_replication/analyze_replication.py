"""Generate a scope-disciplined report for the corrected causal-text factorial."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from mbe_eval.crossfit import cross_fitted_audit, refit_bootstrap_audit


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
    "random_metric",
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


def _spearman_permutation(
    values: pd.Series, target: pd.Series, *, seed: int, permutations: int = 999
) -> tuple[float, float]:
    """Return a raw rank association and a descriptive two-sided permutation p-value."""
    value_rank = values.rank(method="average").to_numpy(dtype=float)
    target_rank = target.rank(method="average").to_numpy(dtype=float)
    value_centered = value_rank - value_rank.mean()
    target_centered = target_rank - target_rank.mean()
    denominator = float(np.linalg.norm(value_centered) * np.linalg.norm(target_centered))
    if denominator == 0.0:
        return np.nan, np.nan
    observed = float(np.dot(value_centered, target_centered) / denominator)
    rng = np.random.default_rng(seed)
    orders = np.argsort(rng.random((permutations, len(value_rank))), axis=1)
    permuted = value_centered[orders]
    null = (permuted @ target_centered) / denominator
    p_value = float((np.count_nonzero(np.abs(null) >= abs(observed)) + 1) / (permutations + 1))
    return observed, p_value


def _markdown(
    summary: dict[str, object],
    raw: pd.DataFrame,
    stability: pd.DataFrame,
    consensus: pd.DataFrame,
) -> str:
    lines = [
        "# Causal-Text Factorial Sequential Replication: Initial Report",
        "",
        "## Scope",
        "",
        "This is one corrected WikiText-2 causal-LM environment. It supports a "
        "configuration-blocked, refit-aware within-environment MBE analysis. It "
        "does not establish transport, a universal metric ranking, or a selector "
        "claim across tasks.",
        "",
        "## Integrity",
        "",
        f"- Planned rows: {summary['planned_rows']}",
        f"- Completed valid rows: {summary['valid_rows']}",
        f"- Error rows: {summary['error_rows']}",
        f"- Distinct configuration interventions: {summary['configuration_count']}",
        f"- Repeated seeds per configuration: {summary['seeds_per_configuration']}",
        f"- Causal behavioral test: {summary['causal_test']}",
        "",
        "## Inference Guard",
        "",
        "The active MBE 2.0 protocol requires at least 30 independent "
        "configuration/environment units for the configuration-blocked inference "
        f"path. This factorial has {summary['configuration_count']} configuration "
        "interventions, so seed-level rows are used only as repeated measurements "
        "within those units.",
        "",
        "## Negative-Control Finding",
        "",
        "`random_metric` is a deterministic Gaussian value derived from the full "
        "run ID. It varies across all configuration means and is used as the "
        "configuration-level negative control. The earlier seed-only control failure "
        "is retained in the previous factorial's artifact record.",
        "",
        "## Raw Association With Test NLL",
        "",
        "The rows are first averaged within configuration, so this table has "
        f"{summary['configuration_count']} independent intervention units rather "
        f"than {summary['valid_rows']} seed-level rows. Negative Spearman values "
        "correspond to lower test NLL for larger metric values; direction is "
        "descriptive only and metric-specific.",
        "",
        "| Metric | Raw Spearman | permutation p (descriptive) |",
        "|---|---:|---:|",
    ]
    for row in raw.itertuples(index=False):
        lines.append(f"| {row.metric} | {row.raw_spearman:.3f} | {row.raw_permutation_p:.4f} |")

    lines.extend(
        [
            "",
            "## Metric-Batch Stability",
            "",
            "Each non-random metric was recomputed on three deterministic diagnostic "
            "batches per model. The table reports the median within-model batch standard "
            "deviation and its ratio to the metric's across-model standard deviation. "
            "Smaller ratios indicate less batch sensitivity in this environment.",
            "",
            "| Metric | Median batch SD | Batch/Across-model SD |",
            "|---|---:|---:|",
        ]
    )
    for row in stability.itertuples(index=False):
        lines.append(
            f"| {row.metric} | {row.median_batch_std:.6g} | {row.batch_to_model_sd:.3f} |"
        )
    lines.extend(
        [
            "",
            "## Configuration-Blocked Refit Analysis",
            "",
            "For every metric and baseline level, the analysis uses 199 full refit "
            "configuration bootstraps and both frozen nuisance families: degree-six "
            "ridge and degree-six ridge with pairwise control interactions. A within-"
            "environment predictive increment requires the lower refit interval to be "
            "above zero for both families. Residual permutation is reported as a "
            "secondary diagnostic only.",
            "",
            "| Baseline | Metrics with both refit lower intervals above zero | Random control |",
            "|---|---|---|",
        ]
    )
    for baseline, group in consensus.groupby("baseline", sort=False):
        supported = group.loc[group["both_refit_lower_positive"], "metric"].tolist()
        random_status = group.loc[group["metric"].eq("random_metric"), "consensus_status"]
        random_text = random_status.iloc[0] if not random_status.empty else "missing"
        lines.append(
            f"| {baseline} | {', '.join(supported) if supported else 'none'} | {random_text} |"
        )
    lines.extend(
        [
            "",
            "The complete per-metric, per-nuisance-family values are in "
            "`refit_analysis.csv` and `refit_consensus.csv`. These are scoped "
            "within-environment results, not universal survivor or washout labels.",
            "",
            "## Next Evidence Gate",
            "",
            "Replicate this exact analysis in a corrected image environment, then test "
            "the frozen metric and baseline policy on an external locked holdout. "
            "Neither one text environment nor this configuration grid establishes "
            "cross-task transport.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv", type=Path)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--out-dir", type=Path, default=Path("out"))
    parser.add_argument("--refit-bootstrap", type=int, default=199)
    parser.add_argument("--permutations", type=int, default=999)
    parser.add_argument(
        "--baselines",
        default="",
        help="Optional comma-separated B1/B2/B3 baseline keys for resumable analysis chunks.",
    )
    parser.add_argument(
        "--metrics",
        default="",
        help="Optional comma-separated metric names for confirmation chunks.",
    )
    args = parser.parse_args()

    selected_baseline_keys = (
        [part.strip() for part in args.baselines.split(",") if part.strip()]
        if args.baselines
        else list(BASELINES)
    )
    missing_baselines = [key for key in selected_baseline_keys if key not in BASELINES]
    if missing_baselines:
        raise ValueError(f"unknown baseline keys: {', '.join(missing_baselines)}")
    selected_baselines = {key: BASELINES[key] for key in selected_baseline_keys}
    selected_metrics = (
        [part.strip() for part in args.metrics.split(",") if part.strip()]
        if args.metrics
        else list(METRICS)
    )
    missing_metrics = [metric for metric in selected_metrics if metric not in METRICS]
    if missing_metrics:
        raise ValueError(f"unknown metrics: {', '.join(missing_metrics)}")

    rows = pd.read_csv(args.csv)
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    valid = rows.loc[rows["error"].fillna("").eq("")].copy()
    if valid["run_id"].duplicated().any() or valid["run_uuid"].duplicated().any():
        raise ValueError("duplicate primary identifiers in factorial ledger")
    if len(valid) != len(manifest["grid"]):
        raise ValueError("completed ledger does not match frozen factorial grid")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    causal = json.loads((args.csv.parent / "causal_mask_leakage_test.json").read_text())
    config_counts = valid.groupby("config_id", sort=False).size()
    summary = {
        "planned_rows": len(manifest["grid"]),
        "valid_rows": int(len(valid)),
        "error_rows": int(len(rows) - len(valid)),
        "configuration_count": int(config_counts.size),
        "seeds_per_configuration": sorted(config_counts.unique().astype(int).tolist()),
        "causal_test": "passed"
        if causal.get("causal_pass") and causal.get("negative_control_pass")
        else "failed",
        "inference_status": "eligible_for_frozen_refit_inference"
        if config_counts.size >= 30
        else "abstain_below_30_configuration_units",
        "random_negative_control_status": "valid"
        if valid.groupby("config_id")["random_metric"].mean().nunique() >= 2
        else "invalid_constant_at_configuration_level",
    }

    configuration_means = valid.groupby("config_id", as_index=False)[
        ["test_loss", *METRICS]
    ].mean(numeric_only=True)
    raw_rows = []
    for index, metric in enumerate(selected_metrics):
        correlation, p_value = _spearman_permutation(
            configuration_means[metric], configuration_means["test_loss"], seed=20260726 + index
        )
        raw_rows.append(
            {
                "metric": metric,
                "configuration_units": len(configuration_means),
                "raw_spearman": correlation,
                "raw_permutation_p": p_value,
            }
        )
    raw = pd.DataFrame(raw_rows).sort_values("raw_spearman").reset_index(drop=True)

    stability_rows = []
    for column in valid.columns:
        if not column.endswith("_metric_batch_std"):
            continue
        metric = column.removesuffix("_metric_batch_std")
        between = float(valid[metric].std(ddof=1))
        within = float(valid[column].median())
        stability_rows.append(
            {
                "metric": metric,
                "median_batch_std": within,
                "across_model_std": between,
                "batch_to_model_sd": within / between if between > 0 else np.nan,
            }
        )
    stability = pd.DataFrame(stability_rows).sort_values("batch_to_model_sd").reset_index(drop=True)

    # These are deliberately non-inferential diagnostics until the extension
    # crosses the frozen 30-configuration minimum.
    descriptive_rows = []
    for baseline, controls in selected_baselines.items():
        for metric in selected_metrics:
            for nuisance in ("polynomial_ridge", "polynomial_ridge_interactions"):
                try:
                    result = cross_fitted_audit(
                        valid,
                        metric,
                        "test_loss",
                        controls,
                        group_col="config_id",
                        n_splits=5,
                        degree=6,
                        nuisance_model=nuisance,
                        permutations=0,
                        bootstrap=0,
                        seed=20260726,
                    )
                    descriptive_rows.append(
                        {
                            "baseline": baseline,
                            "metric": metric,
                            "nuisance_model": nuisance,
                            "status": "descriptive_underpowered",
                            "configuration_units": config_counts.size,
                            "residual_r": result["residual_r"],
                            "delta_mse": result["delta_mse"],
                            "relative_mse_improvement": result["relative_mse_improvement"],
                        }
                    )
                except (ValueError, np.linalg.LinAlgError) as error:
                    descriptive_rows.append(
                        {
                            "baseline": baseline,
                            "metric": metric,
                            "nuisance_model": nuisance,
                            "status": f"not_estimable: {error}",
                            "configuration_units": config_counts.size,
                        }
                    )
    descriptive = pd.DataFrame(descriptive_rows)

    refit_rows = []
    for baseline, controls in selected_baselines.items():
        for metric in selected_metrics:
            for nuisance in ("polynomial_ridge", "polynomial_ridge_interactions"):
                try:
                    result = refit_bootstrap_audit(
                        valid,
                        metric,
                        "test_loss",
                        controls,
                        refit_bootstrap=args.refit_bootstrap,
                        permutations=args.permutations,
                        group_col="config_id",
                        permutation_block_col="model_size",
                        n_splits=5,
                        degree=6,
                        nuisance_model=nuisance,
                        seed=20260728,
                    )
                    refit_rows.append(
                        {
                            "baseline": baseline,
                            "metric": metric,
                            "nuisance_model": nuisance,
                            "status": "estimated",
                            **result,
                        }
                    )
                except (RuntimeError, ValueError, np.linalg.LinAlgError) as error:
                    refit_rows.append(
                        {
                            "baseline": baseline,
                            "metric": metric,
                            "nuisance_model": nuisance,
                            "status": f"not_estimable: {error}",
                        }
                    )
    refit = pd.DataFrame(refit_rows)
    consensus_rows = []
    for (baseline, metric), group in refit.groupby(["baseline", "metric"], sort=False):
        estimated = group.loc[group["status"].eq("estimated")]
        lower = estimated.get("refit_delta_mse_ci_low", pd.Series(dtype=float))
        both_positive = len(estimated) == 2 and bool((lower > 0).all())
        consensus_rows.append(
            {
                "baseline": baseline,
                "metric": metric,
                "nuisance_models_estimated": len(estimated),
                "minimum_refit_delta_mse_ci_low": float(lower.min()) if len(lower) else np.nan,
                "maximum_residual_permutation_p": float(estimated["residual_p"].max())
                if len(estimated)
                else np.nan,
                "both_refit_lower_positive": both_positive,
                "consensus_status": "within_environment_increment_supported"
                if both_positive
                else "no_consensus_increment",
            }
        )
    consensus = pd.DataFrame(consensus_rows)

    raw.to_csv(args.out_dir / "raw_associations.csv", index=False)
    stability.to_csv(args.out_dir / "metric_batch_stability.csv", index=False)
    descriptive.to_csv(args.out_dir / "descriptive_crossfit.csv", index=False)
    refit.to_csv(args.out_dir / "refit_analysis.csv", index=False)
    consensus.to_csv(args.out_dir / "refit_consensus.csv", index=False)
    (args.out_dir / "factorial_integrity.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    (args.out_dir / "INITIAL_REPORT.md").write_text(
        _markdown(summary, raw, stability, consensus), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
