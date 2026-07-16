from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from mbe_eval.calibration import run_calibration


def main() -> int:
    parser = argparse.ArgumentParser(description="Run known-ground-truth MBE calibration cases.")
    parser.add_argument("--n", type=int, default=600, help="Rows per calibration scenario.")
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--permutations", type=int, default=199)
    parser.add_argument("--output-dir", default="experiments/08_protocol_calibration/out")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    ledger, summary = run_calibration(
        n=args.n,
        seed=args.seed,
        permutations=args.permutations,
    )
    ledger.to_csv(output_dir / "calibration_ledger.csv", index=False)
    summary.to_csv(output_dir / "calibration_summary.csv", index=False)

    lines = [
        "# MBE Protocol Calibration",
        "",
        "These synthetic cases have known data-generating structure. Passing means the declared audit profile matched that structure under the frozen thresholds; it does not validate MBE on real model populations.",
        "",
        "| Scenario | Expected profile | Raw rho | Partial rho | Cross-fit residual rho | Delta MSE | Pass |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for _, row in summary.iterrows():
        lines.append(
            f"| {row['scenario']} | {row['expected_profile']} | {row['raw_r']:.3f} | "
            f"{row['partial_r']:.3f} | {row['crossfit_residual_r']:.3f} | "
            f"{row['delta_mse']:.4f} | {'yes' if row['calibration_pass'] else 'no'} |"
        )
    lines.extend(
        [
            "",
            "The nonlinear-proxy case is intentionally diagnostic: linear partial ranks retain a false signal, while the cross-fitted polynomial nuisance model should remove it. The post-treatment case is an estimand warning, not evidence that the original metric has no total effect.",
            "",
        ]
    )
    (output_dir / "CALIBRATION_REPORT.md").write_text("\n".join(lines), encoding="utf-8")
    print(summary.to_string(index=False))
    if not bool(summary["calibration_pass"].all()):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
