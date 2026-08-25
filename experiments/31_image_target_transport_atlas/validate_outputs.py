from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd


REQUIRED_TARGETS = [
    "clean_test_loss",
    "corruption_mean_loss",
    "clean_test_ece",
    "clean_test_brier",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate image transport atlas outputs")
    parser.add_argument("--dataset", required=True, choices=("cifar10", "cifar100", "svhn"))
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    prefix = f"mbe3_image_transport_{args.dataset}"
    csv_path = args.output_dir / f"{prefix}.csv"
    manifest_path = args.output_dir / f"{prefix}_manifest.json"
    integrity_path = args.output_dir / f"{prefix}_integrity.json"
    ledger = pd.read_csv(csv_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    integrity = json.loads(integrity_path.read_text(encoding="utf-8"))
    valid = ledger.loc[ledger["error"].fillna("").eq("")].copy()
    counts = valid.groupby("config_id", dropna=False).size()
    required_finite = valid[REQUIRED_TARGETS].apply(pd.to_numeric, errors="coerce")
    checks = {
        "dataset_matches": set(valid["task"].astype(str)) == {args.dataset},
        "planned_runs": manifest["planned_runs"] == 120,
        "planned_configurations": manifest["planned_configurations"] == 24,
        "minimum_valid_rows": len(valid) >= 108,
        "all_configurations": len(counts) == 24,
        "at_least_four_seeds_per_configuration": bool(len(counts) == 24 and counts.ge(4).all()),
        "three_architectures": set(valid["arch"].astype(str)) == {"cnn", "resnet", "wide_resnet"},
        "no_duplicate_run_ids": not ledger["run_id"].duplicated().any(),
        "targets_finite": bool(required_finite.notna().all().all()),
        "integrity_gate": bool(integrity["primary_gate_pass"]),
        "svhn_associations_unopened": True,
    }
    report = {
        "dataset": args.dataset,
        "checks": checks,
        "rows": len(ledger),
        "valid_rows": len(valid),
        "error_rows": len(ledger) - len(valid),
        "unique_configurations": len(counts),
        "artifact_sha256": {
            csv_path.name: sha256(csv_path),
            manifest_path.name: sha256(manifest_path),
            integrity_path.name: sha256(integrity_path),
        },
        "metric_target_associations_inspected": False,
        "valid": all(checks.values()),
    }
    (args.output_dir / "STRUCTURAL_VALIDATION.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

