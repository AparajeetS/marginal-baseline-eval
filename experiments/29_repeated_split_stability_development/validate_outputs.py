from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = Path(__file__).resolve().parent
TASK_KEYS = ["scope", "baseline", "candidate_id", "scenario", "icc", "beta", "repetition"]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def frozen_hash_checks() -> list[dict[str, object]]:
    checks: list[dict[str, object]] = []
    for line in (EXPERIMENT / "FROZEN_SHA256SUMS").read_text(encoding="ascii").splitlines():
        if not line.strip():
            continue
        expected, relative = line.split("  ", 1)
        target = ROOT / relative
        actual = sha256(target) if target.is_file() else None
        checks.append({"path": relative, "expected": expected, "actual": actual, "matches": expected == actual})
    return checks


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate repeated-split development outputs")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    output_dir = args.output_dir
    ledger = pd.read_csv(output_dir / "development_ledger.csv")
    summary = pd.read_csv(output_dir / "development_summary.csv")
    diagnostic = json.loads((output_dir / "DEVELOPMENT_DIAGNOSTIC.json").read_text(encoding="utf-8"))
    manifest = json.loads((output_dir / "run_manifest.json").read_text(encoding="utf-8"))
    hashes = frozen_hash_checks()

    expected_rows = 10_080
    expected_cells = 504
    repetitions = 20
    cell_counts = ledger.groupby(TASK_KEYS[:-1], dropna=False).size()
    checks = {
        "frozen_hashes_match": all(check["matches"] for check in hashes),
        "expected_rows": len(ledger) == expected_rows,
        "expected_summary_cells": len(summary) == expected_cells,
        "no_duplicate_task_keys": not ledger.duplicated(TASK_KEYS).any(),
        "repetition_balance": bool(
            len(cell_counts) == expected_cells and cell_counts.eq(repetitions).all()
        ),
        "no_nonestimable_rows": bool(ledger["status"].eq("estimated").all()),
        "manifest_rows_match": manifest["planned_rows"] == expected_rows and manifest["observed_rows"] == expected_rows,
        "manifest_no_protected_reads": not manifest["generalization_target_columns_read"] and not manifest["checkpoint_metric_columns_read"],
        "diagnostic_no_open_authorization": not diagnostic["protected_association_open_authorized"],
    }
    report = {
        "protocol_id": diagnostic["protocol_id"],
        "output_dir": str(output_dir),
        "checks": checks,
        "frozen_hash_checks": hashes,
        "selected_candidate_for_confirmation": diagnostic["selected_candidate_for_confirmation"],
        "valid": all(checks.values()),
    }
    print(json.dumps(report, indent=2))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
