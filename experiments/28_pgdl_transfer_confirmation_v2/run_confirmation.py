from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_PATH = (
    REPO_ROOT / "experiments" / "26_pgdl_transfer_calibration" / "run_calibration.py"
)
PROTOCOL_ID = "mbe3-pgdl-transfer-confirmation-v2"
DEGREE = 2
RIDGE = 0.1
REPETITIONS = 100
WILD_DRAWS = 4999


def _load_source():
    spec = importlib.util.spec_from_file_location("_mbe_pgdl_transfer_confirmation", SOURCE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load the frozen PGDL transfer runner")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


SOURCE = _load_source()


def _initialize_worker(design) -> None:
    SOURCE.PROTOCOL_ID = PROTOCOL_ID
    SOURCE.DEGREE = DEGREE
    SOURCE.RIDGE = RIDGE
    SOURCE._DESIGN = design


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="PGDL transfer confirmation v2")
    parser.add_argument("ledger", type=Path)
    parser.add_argument("plan", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--smoke", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.workers < 1:
        raise ValueError("workers must be positive")

    SOURCE.PROTOCOL_ID = PROTOCOL_ID
    SOURCE.DEGREE = DEGREE
    SOURCE.RIDGE = RIDGE
    SOURCE._initialize_worker = _initialize_worker
    design, control_encodings = SOURCE.load_design(args.ledger, args.plan)
    repetitions = 2 if args.smoke else REPETITIONS
    wild_draws = 19 if args.smoke else WILD_DRAWS
    tasks = SOURCE._task_grid(repetitions, wild_draws, args.smoke)
    ledger = SOURCE.run_tasks(tasks, args.output_dir, args.workers, design)
    if len(ledger) != len(tasks) or ledger.duplicated(SOURCE.TASK_KEYS).any():
        raise RuntimeError("confirmation row-count or duplicate-key gate failed")
    summary = SOURCE.summarize(ledger)
    decision = SOURCE.eligibility(summary)
    decision["protocol_id"] = PROTOCOL_ID
    decision["smoke"] = args.smoke
    if args.smoke:
        decision["global_pass"] = False
        decision["eligible_to_freeze_pgdl_transfer_analysis"] = False

    args.output_dir.mkdir(parents=True, exist_ok=True)
    ledger_path = args.output_dir / "confirmation_ledger.csv"
    summary_path = args.output_dir / "confirmation_summary.csv"
    decision_path = args.output_dir / "FINAL_ELIGIBILITY.json"
    manifest_path = args.output_dir / "run_manifest.json"
    SOURCE._atomic_csv(ledger, ledger_path)
    SOURCE._atomic_csv(summary, summary_path)
    decision_path.write_text(json.dumps(decision, indent=2), encoding="utf-8")
    manifest = {
        "protocol_id": PROTOCOL_ID,
        "smoke": args.smoke,
        "planned_rows": len(tasks),
        "observed_rows": len(ledger),
        "repetitions": repetitions,
        "wild_draws": wild_draws,
        "decision_alpha": SOURCE.DECISION_ALPHA,
        "nuisance_model": SOURCE.NUISANCE_MODEL,
        "degree": DEGREE,
        "ridge": RIDGE,
        "transfer_counts": SOURCE.EXPECTED_COUNTS,
        "pooled_models": 240,
        "control_encodings": control_encodings,
        "ledger_sha256": _sha256(args.ledger),
        "plan_sha256": _sha256(args.plan),
        "estimator_sha256": _sha256(REPO_ROOT / "mbe_eval" / "orthogonal.py"),
        "source_runner_sha256": _sha256(SOURCE_PATH),
        "confirmation_runner_sha256": _sha256(Path(__file__)),
        "preregistration_sha256": _sha256(Path(__file__).with_name("PREREGISTRATION.md")),
        "generalization_target_columns_read": False,
        "checkpoint_metric_columns_read": False,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    outputs = [ledger_path, summary_path, decision_path, manifest_path]
    (args.output_dir / "SHA256SUMS").write_text(
        "\n".join(f"{_sha256(path)}  {path.name}" for path in outputs) + "\n",
        encoding="ascii",
    )
    print(json.dumps(decision, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
