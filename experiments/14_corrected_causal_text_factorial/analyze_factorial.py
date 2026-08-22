"""Generate a scope-disciplined report for the corrected causal-text factorial."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from mbe_eval.crossfit import cross_fitted_audit


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


def _markdown(summary: dict[str, object], raw: pd.DataFrame, stability: pd.DataFrame) -> str:
    lines = [
        "# Corrected Causal-Text Factorial: Initial Report",
        "",
        "## Scope",
        "",
        "This is one corrected WikiText-2 causal-LM environment. It supports "
        "pipeline validation, measurement-reliability reporting, and descriptive "
        "within-environment associations. It does not establish transport, a "
        "universal metric ranking, or an inferential MBE survivor/washout label.",
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
        "The active MBE 2.0 protocol abstains below 30 independent "
        "configuration/environment units. This experiment has 20 configuration "
        "interventions (two sizes times ten training settings), so seed-level rows "
        "must not be treated as 100 independent observations. No metric receives an "
        "inferential increment-supported or washout label from this run.",
        "",
        "## Negative-Control Finding",
        "",
        "`random_metric` was generated from the repeated seed ID only. Its values "
        "therefore average to the same constant in every configuration and cannot "
        "serve as a configuration-level negative control. This is an implementation "
        "failure in the control metric, not evidence about the trained models or the "
        "other metric values. A new factorial will derive the random control from the "
        "full run ID and retain this failure in its ledger.",
        "",
        "## Raw Association With Test NLL",
        "",
        "The rows are first averaged within configuration, so this table has 20 "
        "independent intervention units rather than 100 seed-level rows. Negative "
        "Spearman values correspond to lower test NLL for larger metric values; "
        "direction is descriptive only and metric-specific.",
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
            "## Next Evidence Gate",
            "",
            "Run a preregistered extension with at least six additional configurations "
            "per model size (32 independent configurations total), then apply the frozen "
            "full-refit, configuration-blocked MBE analysis. The extension is a new "
            "sequential replication and must not be pooled as though its settings were "
            "chosen before observing this report.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv", type=Path)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--out-dir", type=Path, default=Path("out"))
    args = parser.parse_args()

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
        "inference_status": "abstain_below_30_configuration_units"
        if config_counts.size < 30
        else "eligible_for_frozen_refit_inference",
        "random_negative_control_status": "invalid_constant_at_configuration_level"
        if valid.groupby("config_id")["random_metric"].mean().nunique() < 2
        else "valid",
    }

    configuration_means = valid.groupby("config_id", as_index=False)[
        ["test_loss", *METRICS]
    ].mean(numeric_only=True)
    raw_rows = []
    for index, metric in enumerate(METRICS):
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
    for baseline, controls in BASELINES.items():
        for metric in METRICS:
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

    raw.to_csv(args.out_dir / "raw_associations.csv", index=False)
    stability.to_csv(args.out_dir / "metric_batch_stability.csv", index=False)
    descriptive.to_csv(args.out_dir / "descriptive_crossfit.csv", index=False)
    (args.out_dir / "factorial_integrity.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    (args.out_dir / "INITIAL_REPORT.md").write_text(
        _markdown(summary, raw, stability), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
