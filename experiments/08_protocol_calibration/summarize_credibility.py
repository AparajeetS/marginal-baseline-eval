from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def _range(frame: pd.DataFrame, column: str) -> str:
    return f"{frame[column].min():.3f}-{frame[column].max():.3f}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize MBE calibration evidence.")
    parser.add_argument("calibration_dir", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--tree-monte-carlo", type=Path)
    parser.add_argument("--tree-semisynthetic", type=Path)
    parser.add_argument("--interaction-semisynthetic", type=Path)
    parser.add_argument("--pgdl-metadata-floor", type=Path)
    args = parser.parse_args()

    monte_carlo = pd.read_csv(args.calibration_dir / "monte_carlo_summary.csv")
    semisynthetic = pd.read_csv(
        args.calibration_dir / "pgdl_semisynthetic_summary.csv"
    )
    polynomial = monte_carlo.loc[monte_carlo["nuisance_model"] == "polynomial_ridge"]
    degree_two_null = polynomial.loc[
        (~polynomial["expected_signal"]) & (polynomial["polynomial_degree"] == 2)
    ]
    degree_six_null = polynomial.loc[
        (~polynomial["expected_signal"]) & (polynomial["polynomial_degree"] == 6)
    ]
    degree_six_signal = polynomial.loc[
        polynomial["expected_signal"] & (polynomial["polynomial_degree"] == 6)
    ]
    semi_null = semisynthetic.loc[semisynthetic["expected_signal"].astype(str) == "False"]
    semi_signal = semisynthetic.loc[semisynthetic["expected_signal"].astype(str) == "True"]

    lines = [
        "# MBE Calibration Evidence Summary",
        "",
        "Status: known-ground-truth and semi-synthetic evidence only. This does not validate real checkpoint metrics or unseen-task transport.",
        "",
        "## Main Findings",
        "",
        f"- Degree-2 polynomial nuisance adjustment fails the generic proxy stress tests: joint false-decision rates span {_range(degree_two_null, 'joint_increment_decision_rate')} across conditional-null cells.",
        f"- Degree-6 polynomial adjustment reduces the same conditional-null joint-decision range to {_range(degree_six_null, 'joint_increment_decision_rate')} while conditional-signal power spans {_range(degree_six_signal, 'joint_increment_decision_rate')}.",
        f"- On PGDL Tasks 1-2 real design geometry, null/proxy joint decisions span {_range(semi_null, 'joint_decision_rate')} and injected/task-specialist recovery spans {_range(semi_signal, 'joint_decision_rate')}.",
        "- Opposite-sign task specialists are recovered within each task and rejected as one stable metric in the balanced pool, supporting task-specific reliability reporting.",
        "",
        "## Nuisance Sensitivity",
        "",
        "| Source | Nuisance | Conditional-null joint decisions | Signal joint decisions |",
        "|---|---|---:|---:|",
        f"| Generic simulation | polynomial degree 2 | {_range(degree_two_null, 'joint_increment_decision_rate')} | {_range(polynomial.loc[polynomial.expected_signal & (polynomial.polynomial_degree == 2)], 'joint_increment_decision_rate')} |",
        f"| Generic simulation | polynomial degree 6 | {_range(degree_six_null, 'joint_increment_decision_rate')} | {_range(degree_six_signal, 'joint_increment_decision_rate')} |",
        f"| PGDL semi-synthetic | polynomial degrees 2/4/6 | {_range(semi_null, 'joint_decision_rate')} | {_range(semi_signal, 'joint_decision_rate')} |",
    ]

    if args.tree_monte_carlo and args.tree_monte_carlo.is_file():
        tree_mc = pd.read_csv(args.tree_monte_carlo)
        tree_null = tree_mc.loc[~tree_mc["expected_signal"]]
        tree_signal = tree_mc.loc[tree_mc["expected_signal"]]
        lines.append(
            f"| Generic simulation | Extra Trees | {_range(tree_null, 'joint_increment_decision_rate')} | {_range(tree_signal, 'joint_increment_decision_rate')} |"
        )
    if args.tree_semisynthetic and args.tree_semisynthetic.is_file():
        tree_semi = pd.read_csv(args.tree_semisynthetic)
        tree_semi_null = tree_semi.loc[
            tree_semi["expected_signal"].astype(str) == "False"
        ]
        tree_semi_signal = tree_semi.loc[
            tree_semi["expected_signal"].astype(str) == "True"
        ]
        lines.append(
            f"| PGDL semi-synthetic | Extra Trees | {_range(tree_semi_null, 'joint_decision_rate')} | {_range(tree_semi_signal, 'joint_decision_rate')} |"
        )
    if args.interaction_semisynthetic and args.interaction_semisynthetic.is_file():
        interaction = pd.read_csv(args.interaction_semisynthetic)
        interaction_null = interaction.loc[
            interaction["expected_signal"].astype(str) == "False"
        ]
        interaction_signal = interaction.loc[
            interaction["expected_signal"].astype(str) == "True"
        ]
        lines.append(
            f"| PGDL semi-synthetic | polynomial degree 6 + pairwise interactions | {_range(interaction_null, 'joint_decision_rate')} | {_range(interaction_signal, 'joint_decision_rate')} |"
        )

    metadata_lines = []
    if args.pgdl_metadata_floor and args.pgdl_metadata_floor.is_file():
        metadata = pd.read_csv(args.pgdl_metadata_floor)
        supported = int(
            (metadata["increment_classification"] == "increment-supported").sum()
        )
        residual_only = int(
            (metadata["increment_classification"] == "residual-dependence-only").sum()
        )
        metadata_lines = [
            "",
            "## Real-Data Baseline Check",
            "",
            f"The PGDL metadata floor contains {len(metadata)} frozen task-by-nuisance fits. Final training loss is increment-supported in {supported}; {residual_only} fits show residual dependence without interval-supported predictive improvement. This is a baseline diagnostic only and does not evaluate the checkpoint-derived metric battery.",
        ]

    lines.extend(
        [
            *metadata_lines,
            "",
            "## What This Changes",
            "",
            "Degree 2 and the tested Extra Trees configuration are documented failure controls and cannot support primary MBE conclusions. Primary real-metric reporting must show every preregistered eligible nuisance learner, repeated cross-fitting, adjusted residual evidence, and interval-supported predictive improvement. Learner disagreement is a result, not permission to select the favorable model.",
            "",
            "## Remaining Gates",
            "",
            "- calibrate nested or repeated-cross-fit uncertainty that refits nuisance models;",
            "- compare directly with conditional mutual information and granulated statistics;",
            "- complete PGDL Tasks 1-2 real metric extraction;",
            "- freeze and execute Tasks 4-5 validation and Tasks 6-9 transfer once;",
            "- run prospective selection and independent replication.",
            "",
        ]
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
