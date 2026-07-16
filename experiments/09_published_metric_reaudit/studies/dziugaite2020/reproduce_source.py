from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from mbe_eval.robust_sign_error import (
    robust_sign_error_environments,
    robust_sign_error_summary,
    source_metric_columns,
)


HYPERPARAMETERS = [
    "hp.dataset",
    "hp.lr",
    "hp.model_depth",
    "hp.model_width",
    "hp.train_size",
]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Reproduce Dziugaite et al. (2020) coupled-network sign error."
    )
    parser.add_argument("data", type=Path, help="Prepared Dziugaite et al. run ledger.")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--minimum-ess", type=float, default=12.0)
    parser.add_argument("--test-size", type=int, default=10_000)
    args = parser.parse_args()

    data = pd.read_csv(args.data)
    data["hp.train_size"] = data["hp.train_dataset_size"]
    metrics = source_metric_columns(data.columns.tolist())
    environments = robust_sign_error_environments(
        data,
        metrics,
        HYPERPARAMETERS,
        minimum_effective_sample_size=args.minimum_ess,
        test_size=args.test_size,
    )
    summary = robust_sign_error_summary(environments, metrics)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    environments.to_csv(args.output_dir / "source_environments.csv", index=False)
    summary.to_csv(args.output_dir / "source_sign_error_summary.csv", index=False)
    headline = summary.loc[summary["hyperparameter"] == "all"].sort_values(
        "mean_sign_error"
    )
    headline.to_csv(args.output_dir / "source_headline_ranking.csv", index=False)

    print(
        f"runs={len(data)} configurations={data['config_id'].nunique()} "
        f"metrics={len(metrics)} directed_environments={len(environments)}"
    )
    print(headline.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
