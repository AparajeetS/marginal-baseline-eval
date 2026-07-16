from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run(command: list[str]) -> dict[str, object]:
    completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    return {
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Execute the frozen MBE replication audit.")
    parser.add_argument("--reviewer", required=True)
    parser.add_argument("--conflict-statement", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--skip-tests", action="store_true")
    args = parser.parse_args()

    manifest_path = ROOT / "experiments/11_credibility_freeze/freeze_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    hash_checks = []
    for entry in manifest["files"]:
        path = ROOT / entry["path"]
        actual = sha256(path) if path.is_file() else None
        hash_checks.append(
            {
                "path": entry["path"],
                "expected": entry["sha256"],
                "actual": actual,
                "matches": actual == entry["sha256"],
            }
        )

    commands = [
        run([sys.executable, "experiments/11_credibility_freeze/validate_claims.py", "experiments/11_credibility_freeze/claim_ledger.json"]),
    ]
    if not args.skip_tests:
        commands.append(run([sys.executable, "-m", "pytest", "-q"]))

    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()
    dirty = subprocess.run(
        ["git", "status", "--porcelain"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.splitlines()
    report = {
        "schema_version": 1,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "reviewer": args.reviewer,
        "conflict_statement": args.conflict_statement,
        "commit": commit,
        "freeze_base_commit": manifest["base_commit"],
        "hash_checks": hash_checks,
        "commands": commands,
        "dirty_paths": dirty,
        "reviewer_conclusion": "REVIEWER MUST COMPLETE",
        "material_discrepancies": [],
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "replication_audit.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    passed = all(item["matches"] for item in hash_checks) and all(
        item["returncode"] == 0 for item in commands
    )
    lines = [
        "# Independent Replication Audit",
        "",
        f"Reviewer: {args.reviewer}",
        f"Conflict statement: {args.conflict_statement}",
        f"Commit: `{commit}`",
        f"Frozen hashes match: {'yes' if all(item['matches'] for item in hash_checks) else 'no'}",
        f"Automated checks pass: {'yes' if passed else 'no'}",
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
    (args.output_dir / "REPLICATION_REPORT.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"replication_automation_pass={passed}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
