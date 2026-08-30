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
ROOT = Path(__file__).resolve().parents[2]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def frozen_source_checks() -> dict[str, bool]:
    checks: dict[str, bool] = {}
    frozen = Path(__file__).with_name("FROZEN_SHA256SUMS")
    correction_path = Path(__file__).with_name("VALIDATOR_CORRECTION.json")
    correction = json.loads(correction_path.read_text(encoding="utf-8"))
    for line in frozen.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, relative = line.split(maxsplit=1)
        path = ROOT / relative.strip()
        observed = sha256(path) if path.is_file() else ""
        if relative.strip().endswith("/validate_outputs.py"):
            checks[f"corrected_source:{relative.strip()}"] = bool(
                expected == correction["original_sha256"]
                and observed == correction["corrected_sha256"]
                and correction["reason"]
            )
        else:
            checks[f"frozen_source:{relative.strip()}"] = observed == expected
    return checks


def recomputed_integrity(ledger: pd.DataFrame, valid: pd.DataFrame) -> dict[str, object]:
    counts = valid.groupby("config_id", dropna=False).size()
    return {
        "rows": len(ledger),
        "valid_rows": len(valid),
        "error_rows": len(ledger) - len(valid),
        "unique_run_ids": int(ledger["run_id"].nunique()),
        "duplicate_run_ids": int(ledger["run_id"].duplicated().sum()),
        "valid_configurations": len(counts),
        "configurations_with_at_least_four_seeds": int(counts.ge(4).sum()),
        "architectures": sorted(valid["arch"].astype(str).unique().tolist()),
        "primary_gate_pass": bool(
            len(valid) >= 108
            and len(counts) == 24
            and counts.ge(4).all()
            and set(valid["arch"].astype(str)) == {"cnn", "resnet", "wide_resnet"}
            and not ledger["run_id"].duplicated().any()
        ),
    }


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
    recomputed = recomputed_integrity(ledger, valid)
    manifest_run_ids = {
        str(row["run_id"]) for row in manifest.get("grid", []) if "run_id" in row
    }
    split_hashes = manifest.get("split_hashes", {})
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
        "manifest_grid_matches_ledger": manifest_run_ids
        == set(ledger["run_id"].astype(str)),
        "split_hashes_well_formed": set(split_hashes)
        == {"train_indices", "validation_indices", "test_indices"}
        and all(
            isinstance(value, str)
            and len(value) == 64
            and all(character in "0123456789abcdef" for character in value)
            for value in split_hashes.values()
        ),
        "integrity_matches_recomputation": integrity == recomputed,
        **frozen_source_checks(),
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
        "custody_status": "not-machine-verifiable",
        "metric_target_associations_inspected": None,
        "custody_note": (
            "Structural validation cannot establish whether a person previously "
            "inspected protected associations; no such claim is made here."
        ),
        "valid": all(checks.values()),
    }
    report_path = args.output_dir / "STRUCTURAL_VALIDATION.json"
    with report_path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
