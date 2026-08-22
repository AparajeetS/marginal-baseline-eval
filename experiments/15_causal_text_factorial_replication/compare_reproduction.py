from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


def maximum_difference(
    reference: pd.DataFrame, candidate: pd.DataFrame, column: str
) -> float:
    difference = np.abs(
        reference[column].to_numpy(dtype=float)
        - candidate[column].to_numpy(dtype=float)
    )
    return float(np.nanmax(difference)) if len(difference) else 0.0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("reference", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    raw_reference = pd.read_csv(args.reference / "raw_associations.csv").sort_values(
        "metric"
    )
    raw_candidate = pd.read_csv(args.candidate / "raw_associations.csv").sort_values(
        "metric"
    )
    consensus_reference = pd.read_csv(
        args.reference / "refit_consensus.csv"
    ).sort_values(["baseline", "metric"])
    consensus_candidate = pd.read_csv(
        args.candidate / "refit_consensus.csv"
    ).sort_values(["baseline", "metric"])

    raw_reference = raw_reference.reset_index(drop=True)
    raw_candidate = raw_candidate.reset_index(drop=True)
    consensus_reference = consensus_reference.reset_index(drop=True)
    consensus_candidate = consensus_candidate.reset_index(drop=True)

    report = {
        "raw_metric_order_equal": raw_reference["metric"].equals(
            raw_candidate["metric"]
        ),
        "consensus_keys_equal": consensus_reference[
            ["baseline", "metric"]
        ].equals(consensus_candidate[["baseline", "metric"]]),
        "consensus_status_equal": consensus_reference["consensus_status"].equals(
            consensus_candidate["consensus_status"]
        ),
        "support_decisions_equal": consensus_reference[
            "both_refit_lower_positive"
        ].equals(consensus_candidate["both_refit_lower_positive"]),
        "maximum_absolute_differences": {
            "raw_spearman": maximum_difference(
                raw_reference, raw_candidate, "raw_spearman"
            ),
            "raw_permutation_p": maximum_difference(
                raw_reference, raw_candidate, "raw_permutation_p"
            ),
            "minimum_refit_delta_mse_ci_low": maximum_difference(
                consensus_reference,
                consensus_candidate,
                "minimum_refit_delta_mse_ci_low",
            ),
            "maximum_residual_permutation_p": maximum_difference(
                consensus_reference,
                consensus_candidate,
                "maximum_residual_permutation_p",
            ),
        },
    }
    report["scientific_reproduction_pass"] = bool(
        report["raw_metric_order_equal"]
        and report["consensus_keys_equal"]
        and report["consensus_status_equal"]
        and report["support_decisions_equal"]
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["scientific_reproduction_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

