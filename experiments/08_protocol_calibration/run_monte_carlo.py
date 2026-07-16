from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from mbe_eval import run_monte_carlo_calibration


def _integer_list(value: str) -> tuple[int, ...]:
    parsed = tuple(int(item.strip()) for item in value.split(",") if item.strip())
    if not parsed:
        raise argparse.ArgumentTypeError("provide at least one integer")
    return parsed


def write_report(summary: pd.DataFrame, path: Path, alpha: float) -> None:
    lines = [
        "# Repeated MBE Calibration",
        "",
        "This is a repeated-simulation calibration of the compact polynomial-ridge MBE reference implementation. Conditional-null rows report empirical false-positive behavior; conditional-signal rows report power. The joint decision requires both a residual permutation rejection and a 95% out-of-fold Delta-MSE interval entirely above zero.",
        "",
        "| Scenario | Signal expected | Nuisance | n | Degree | Repetitions | Legacy reject | Cross-fit reject [95% CI] | Joint decision [95% CI] | Median Delta MSE |",
        "|---|---:|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in summary.iterrows():
        lines.append(
            f"| `{row['scenario']}` | {str(bool(row['expected_signal'])).lower()} | "
            f"{row['nuisance_model']} | {int(row['n'])} | {int(row['polynomial_degree'])} | {int(row['repetitions'])} | "
            f"{row['legacy_partial_reject_rate']:.3f} | "
            f"{row['crossfit_residual_reject_rate']:.3f} "
            f"[{row['crossfit_residual_reject_ci_low']:.3f}, {row['crossfit_residual_reject_ci_high']:.3f}] | "
            f"{row['joint_increment_decision_rate']:.3f} "
            f"[{row['joint_increment_decision_ci_low']:.3f}, {row['joint_increment_decision_ci_high']:.3f}] | "
            f"{row['median_delta_mse']:.4f} |"
        )
    null_rows = summary.loc[~summary["expected_signal"]]
    signal_rows = summary.loc[summary["expected_signal"]]
    lines.extend(
        [
            "",
            "## Reading The Table",
            "",
            f"The nominal residual-test level is {alpha:.3f}. A low null rejection rate supports calibration only for the simulated nuisance structures; it does not prove conditional independence testing is universally valid. Power must be interpreted together with sample size and nuisance degree.",
            "",
            f"Across the displayed grid, conditional-null cross-fit rejection ranges from {null_rows['crossfit_residual_reject_rate'].min():.3f} to {null_rows['crossfit_residual_reject_rate'].max():.3f}; conditional-signal joint detection ranges from {signal_rows['joint_increment_decision_rate'].min():.3f} to {signal_rows['joint_increment_decision_rate'].max():.3f}.",
            "",
            "The post-treatment scenario is a conditional null for the direct-information estimand after controlling the mediator. Its raw association is real; loss of conditional signal is not a causal verdict.",
            "",
            "This report calibrates one reference nuisance model. Submission evidence must add alternative nuisance learners, semi-synthetic real-design tests, and held-out task-family prediction.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run repeated MBE calibration.")
    parser.add_argument("--sample-sizes", type=_integer_list, default=(150, 300, 600))
    parser.add_argument("--degrees", type=_integer_list, default=(2, 6))
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
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--seed", type=int, default=20260716)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).parent / "out")
    args = parser.parse_args()

    ledger, summary = run_monte_carlo_calibration(
        sample_sizes=args.sample_sizes,
        degrees=args.degrees,
        repetitions=args.repetitions,
        permutations=args.permutations,
        bootstrap=args.bootstrap,
        nuisance_model=args.nuisance_model,
        alpha=args.alpha,
        seed=args.seed,
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    ledger.to_csv(args.output_dir / "monte_carlo_ledger.csv", index=False)
    summary.to_csv(args.output_dir / "monte_carlo_summary.csv", index=False)
    write_report(summary, args.output_dir / "MONTE_CARLO_CALIBRATION.md", args.alpha)
    print(summary.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
