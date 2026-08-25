from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = Path(__file__).resolve().parent
TASK_KEYS = ["geometry", "n_configurations", "baseline", "scenario", "icc", "beta", "repetition"]
CELL_KEYS = TASK_KEYS[:-1]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate oracle frontier outputs")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--allow-smoke", action="store_true")
    args = parser.parse_args()
    ledger = pd.read_csv(args.output_dir / "frontier_ledger.csv")
    summary = pd.read_csv(args.output_dir / "frontier_summary.csv")
    diagnostic = json.loads((args.output_dir / "FRONTIER_DIAGNOSTIC.json").read_text(encoding="utf-8"))
    manifest = json.loads((args.output_dir / "run_manifest.json").read_text(encoding="utf-8"))

    if diagnostic["smoke"] and not args.allow_smoke:
        raise RuntimeError("refusing to validate smoke output as the frozen campaign")
    expected_rows = 4 if diagnostic["smoke"] else 126_000
    expected_cells = 2 if diagnostic["smoke"] else 336
    expected_summary_rows = expected_cells * 4
    expected_repetitions = {24: 500, 48: 500, 96: 250, 192: 250}
    cell_counts = ledger.groupby(CELL_KEYS, dropna=False).size()
    balance = True
    if not diagnostic["smoke"]:
        balance = all(count == expected_repetitions[int(key[1])] for key, count in cell_counts.items())

    frozen_checks = []
    frozen_path = EXPERIMENT / "FROZEN_SHA256SUMS"
    if frozen_path.exists():
        for line in frozen_path.read_text(encoding="ascii").splitlines():
            if line.strip():
                expected, relative = line.split("  ", 1)
                actual = sha256(ROOT / relative) if (ROOT / relative).is_file() else None
                frozen_checks.append({"path": relative, "expected": expected, "actual": actual, "matches": expected == actual})
    checks = {
        "frozen_hashes_present": bool(frozen_checks),
        "frozen_hashes_match": bool(frozen_checks) and all(item["matches"] for item in frozen_checks),
        "expected_rows": len(ledger) == expected_rows,
        "expected_cells": len(cell_counts) == expected_cells,
        "expected_summary_rows": len(summary) == expected_summary_rows,
        "no_duplicate_task_keys": not ledger.duplicated(TASK_KEYS).any(),
        "repetition_balance": balance,
        "no_nonestimable_rows": bool(ledger["status"].eq("estimated").all()),
        "manifest_rows_match": manifest["planned_rows"] == expected_rows and manifest["observed_rows"] == expected_rows,
        "no_protected_reads": not manifest["generalization_target_columns_read"] and not manifest["checkpoint_metric_columns_read"],
        "no_open_authorization": not diagnostic["protected_association_open_authorized"],
    }
    report = {"protocol_id": diagnostic["protocol_id"], "checks": checks, "frozen_hash_checks": frozen_checks, "valid": all(checks.values())}
    print(json.dumps(report, indent=2))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

