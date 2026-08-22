from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_hash_manifest(
    path: Path,
    root_relative: bool,
    historical_aliases: dict[tuple[str, str], dict[str, str]],
) -> list[dict[str, object]]:
    checks: list[dict[str, object]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, name = line.split("  ", 1)
        target = ROOT / name if root_relative else path.parent / name
        current_actual = sha256(target) if target.is_file() else None
        alias = historical_aliases.get((name.replace("\\", "/"), expected))
        resolved = ROOT / alias["snapshot"] if alias else target
        actual = sha256(resolved) if resolved.is_file() else None
        checks.append(
            {
                "manifest": str(path.relative_to(ROOT)).replace("\\", "/"),
                "path": name.replace("\\", "/"),
                "resolved_path": (
                    str(resolved.relative_to(ROOT)).replace("\\", "/")
                    if resolved.exists()
                    else str(resolved)
                ),
                "expected": expected,
                "actual": actual,
                "current_path_actual": current_actual,
                "historical_snapshot_used": alias is not None,
                "historical_reason": alias["reason"] if alias else None,
                "matches": actual == expected,
            }
        )
    return checks


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate MBE replication packet v2")
    parser.add_argument("--reviewer", required=True)
    parser.add_argument("--conflict-statement", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--run-tests", action="store_true")
    args = parser.parse_args()

    packet_path = Path(__file__).with_name("replication_packet_v2.json")
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    historical_aliases = {
        (entry["manifest_path"], entry["expected_sha256"]): entry
        for entry in packet.get("historical_source_aliases", [])
    }
    hash_checks: list[dict[str, object]] = []
    hash_checks.extend(
        verify_hash_manifest(
            ROOT / packet["packet_envelope_manifest"],
            root_relative=True,
            historical_aliases=historical_aliases,
        )
    )
    for name in packet["hash_manifests"]:
        hash_checks.extend(
            verify_hash_manifest(
                ROOT / name,
                root_relative=True,
                historical_aliases=historical_aliases,
            )
        )
    for name in packet["artifact_hash_manifests"]:
        hash_checks.extend(
            verify_hash_manifest(
                ROOT / name,
                root_relative=False,
                historical_aliases=historical_aliases,
            )
        )

    table_checks: list[dict[str, object]] = []
    for gate in packet["table_gates"]:
        frame = pd.read_csv(ROOT / gate["path"])
        missing = [column for column in gate["keys"] if column not in frame.columns]
        duplicates = int(frame.duplicated(gate["keys"]).sum()) if not missing else None
        table_checks.append(
            {
                "path": gate["path"],
                "expected_rows": gate["rows"],
                "observed_rows": len(frame),
                "missing_key_columns": missing,
                "duplicate_keys": duplicates,
                "passes": len(frame) == gate["rows"] and not missing and duplicates == 0,
            }
        )

    protected_checks: list[dict[str, object]] = []
    for name in packet["protected_decisions"]:
        decision = json.loads((ROOT / name).read_text(encoding="utf-8"))
        authorized = bool(
            decision.get("checkpoint_metric_association_open_authorized", False)
            or decision.get("eligible_to_freeze_pgdl_transfer_analysis", False)
        )
        protected_checks.append(
            {
                "path": name,
                "global_pass": bool(decision.get("global_pass", False)),
                "opening_authorized": authorized,
                "expected_current_state": "sealed",
                "passes": not authorized,
            }
        )

    test_result = None
    if args.run_tests:
        completed = subprocess.run(
            [sys.executable, "-m", "pytest", "-q"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        test_result = {
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "passes": completed.returncode == 0,
        }

    automated_pass = bool(
        all(check["matches"] for check in hash_checks)
        and all(check["passes"] for check in table_checks)
        and all(check["passes"] for check in protected_checks)
        and (test_result is None or test_result["passes"])
    )
    report = {
        "schema_version": 2,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "reviewer": args.reviewer,
        "conflict_statement": args.conflict_statement,
        "packet_sha256": sha256(packet_path),
        "hash_checks": hash_checks,
        "table_checks": table_checks,
        "protected_checks": protected_checks,
        "test_result": test_result,
        "automated_pass": automated_pass,
        "reviewer_conclusion": "REVIEWER MUST COMPLETE",
        "material_discrepancies": [],
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "replication_validation.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    lines = [
        "# Independent Replication Packet V2",
        "",
        f"Reviewer: {args.reviewer}",
        f"Conflict statement: {args.conflict_statement}",
        f"Automated checks pass: {'yes' if automated_pass else 'no'}",
        "Protected PGDL state: sealed",
        "",
        "## Reviewer Conclusion",
        "",
        "REVIEWER MUST COMPLETE AND SIGN THIS SECTION.",
        "",
        "## Material Discrepancies",
        "",
        "REVIEWER MUST LIST DISCREPANCIES OR WRITE `none observed`.",
        "",
    ]
    (args.output_dir / "REPLICATION_REPORT.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )
    print(f"replication_packet_v2_pass={automated_pass}")
    return 0 if automated_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
