from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


METRICS = [
    "parameter_count",
    "parameter_l2",
    "initial_parameter_l2",
    "distance_from_initialization_l2",
    "relative_distance_from_initialization",
    "update_to_weight_ratio",
    "frobenius_sum_sq",
    "log_frobenius_product_sq",
    "spectral_sum_sq",
    "log_spectral_product_sq",
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the PGDL checkpoint pilot.")
    parser.add_argument("metrics", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    args = parser.parse_args()

    data = pd.read_csv(args.metrics)
    required = {"run_id", "task", "generalization_gap_accuracy", *METRICS}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"missing pilot columns: {sorted(missing)}")
    counts = data.groupby("task").size().to_dict()
    if len(data) != 48 or counts != {"task1": 24, "task2": 24}:
        raise ValueError(f"unexpected frozen-pilot counts: {counts}")
    if data["run_id"].duplicated().any():
        raise ValueError("pilot run IDs are not unique")
    metric_values = data[METRICS].to_numpy(dtype=float)
    if not np.isfinite(metric_values).all():
        raise ValueError("checkpoint metrics contain non-finite values")
    if (data[[metric for metric in METRICS if not metric.startswith("log_")]] <= 0).any().any():
        raise ValueError("a positive checkpoint metric is non-positive")

    rows: list[dict[str, object]] = []
    for task, frame in data.groupby("task"):
        for metric in METRICS:
            rows.append(
                {
                    "task": task,
                    "metric": metric,
                    "n": len(frame),
                    "unique_values": frame[metric].nunique(),
                    "minimum": frame[metric].min(),
                    "median": frame[metric].median(),
                    "maximum": frame[metric].max(),
                    "descriptive_spearman_to_accuracy_gap": frame[metric].corr(
                        frame["generalization_gap_accuracy"], method="spearman"
                    ),
                }
            )
    summary = pd.DataFrame(rows)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(args.summary, index=False)

    lines = [
        "# PGDL Checkpoint Pilot QA",
        "",
        "The frozen, outcome-blind pilot contains 24 models from Task 1 and 24 from Task 2. All 48 initialization/final checkpoint pairs aligned by tensor role and shape, and every extracted metric is finite.",
        "",
        "Spectral norms use exact singular-value decomposition. Product-style measures are sums of log squared layer norms; biases enter whole-model norms but not layer products or sums.",
        "",
        "| Task | Metric | Unique | Min | Median | Max | Descriptive rho |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for _, row in summary.iterrows():
        lines.append(
            f"| {row['task']} | `{row['metric']}` | {row['unique_values']} | "
            f"{row['minimum']:.4g} | {row['median']:.4g} | {row['maximum']:.4g} | "
            f"{row['descriptive_spearman_to_accuracy_gap']:.3f} |"
        )
    lines.extend(
        [
            "",
            "The correlations are implementation smoke checks, not effect estimates: the pilot has only 24 observations per task and intentionally performs no p-value, confidence-interval, survival, or washout classification. Development inference must use all Tasks 1-2 models after every primary metric implementation is frozen.",
            "",
        ]
    )
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text("\n".join(lines), encoding="utf-8")
    print(summary.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
