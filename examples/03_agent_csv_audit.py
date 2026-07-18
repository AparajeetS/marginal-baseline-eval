"""Run a tiny MBE CSV audit and write machine-readable output.

This is the smallest example for AI coding assistants: it uses a prebuilt CSV
ledger, no PyTorch dependency, and the same function as the CLI.
"""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mbe_eval.cli import audit_csv
from mbe_eval.reporting import summarize_audit, write_markdown_report

CSV = ROOT / "examples" / "tiny_metric_ledger.csv"
OUT = ROOT / "examples" / "tiny_metric_audit_report.md"
JSON = ROOT / "examples" / "tiny_metric_audit_results.json"


def main() -> None:
    report = audit_csv(
        CSV,
        metrics=["fim_norm", "val_loss_ep20"],
        target="test_accuracy",
        controls=["learning_rate", "weight_decay", "arch"],
        groupby=["task"],
        bootstrap=50,
        seed=42,
        results=JSON,
    )
    write_markdown_report(
        report,
        OUT,
        title="Tiny MBE Audit",
        target="test_accuracy",
        controls=["learning_rate", "weight_decay", "arch"],
        notes=["Example ledger: `examples/tiny_metric_ledger.csv`"],
    )
    print(summarize_audit(report).to_string(index=False))
    print(f"Wrote {OUT}")
    print(f"Wrote {JSON}")


if __name__ == "__main__":
    main()
