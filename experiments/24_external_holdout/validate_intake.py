from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_hash_manifest(path: Path) -> list[dict[str, object]]:
    checks: list[dict[str, object]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, name = line.split("  ", 1)
        target = ROOT / name
        actual = sha256(target) if target.is_file() else None
        checks.append(
            {
                "path": name,
                "expected": expected,
                "actual": actual,
                "matches": actual == expected,
            }
        )
    return checks


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate external holdout intake")
    parser.add_argument(
        "intake",
        nargs="?",
        type=Path,
        default=Path(__file__).with_name("PGDL_TASKS_6_9_INTAKE.json"),
    )
    parser.add_argument("--require-open-authorized", action="store_true")
    args = parser.parse_args()

    intake = json.loads(args.intake.read_text(encoding="utf-8"))
    envelope_checks = verify_hash_manifest(ROOT / intake["intake_hash_manifest"])
    counts = {key: int(value) for key, value in intake["task_model_counts"].items()}
    total = sum(counts.values())
    ledger = pd.read_csv(ROOT / intake["model_ledger"], usecols=["run_id", "task"])
    transfer = ledger.loc[ledger["task"].isin(counts)]
    observed = transfer.groupby("task").size().astype(int).to_dict()
    decision = json.loads(
        (ROOT / intake["calibration_decision"]).read_text(encoding="utf-8")
    )
    authorized = bool(
        decision.get("global_pass", False)
        and decision.get("eligible_to_freeze_pgdl_transfer_analysis", False)
    )
    checks = {
        "declared_total_matches": total == int(intake["total_independent_models"]),
        "ledger_counts_match": observed == counts,
        "unique_models_match": transfer["run_id"].nunique() == total,
        "at_least_48_independent_models": total >= 48,
        "at_least_8_metric_families": len(intake["planned_metric_families"]) >= 8,
        "prior_exposure_disclosed": bool(intake["prior_exposure"]["disclosure"]),
        "checkpoint_associations_remain_unopened": not bool(
            intake["prior_exposure"]["checkpoint_metric_associations_opened"]
        ),
        "calibration_opening_authorized": authorized,
        "intake_envelope_hashes_match": all(
            check["matches"] for check in envelope_checks
        ),
    }
    structural_pass = all(
        value for key, value in checks.items() if key != "calibration_opening_authorized"
    )
    report = {
        "dataset_id": intake["dataset_id"],
        "structural_intake_pass": structural_pass,
        "protected_analysis_authorized": authorized,
        "required_action": "remain sealed" if not authorized else "freeze separate analysis packet",
        "intake_envelope_checks": envelope_checks,
        "checks": checks,
    }
    print(json.dumps(report, indent=2))
    if not structural_pass:
        return 1
    if args.require_open_authorized and not authorized:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
