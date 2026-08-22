from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict, dataclass
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time

import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from mbe_eval import orthogonal_score_audit  # noqa: E402


SOURCE_PATH = (
    REPO_ROOT / "experiments" / "26_pgdl_transfer_calibration" / "run_calibration.py"
)


def _load_source():
    spec = importlib.util.spec_from_file_location("_mbe_pgdl_transfer_v1", SOURCE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load the frozen PGDL transfer simulator")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


SOURCE = _load_source()
PROTOCOL_ID = "mbe3-pgdl-nuisance-development-v1"
SOURCE.PROTOCOL_ID = PROTOCOL_ID
BASELINES = SOURCE.BASELINES
NULL_SCENARIOS = SOURCE.NULL_SCENARIOS
SIGNAL_SCENARIO = SOURCE.SIGNAL_SCENARIO
RELIABILITY_LEVELS = SOURCE.RELIABILITY_LEVELS
SIGNAL_EFFECTS = SOURCE.SIGNAL_EFFECTS
DECISION_ALPHA = 0.001
DEFAULT_REPETITIONS = 20
DEFAULT_WILD_DRAWS = 999
GROUP_KEYS = ["baseline", "candidate_id", "scenario", "reliability", "beta"]
TASK_KEYS = [*GROUP_KEYS, "repetition"]


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    degree: int
    ridge: float
    complexity_rank: int


CANDIDATES = (
    Candidate("interactions_d2_r0", 2, 0.0, 1),
    Candidate("interactions_d2_r001", 2, 0.01, 2),
    Candidate("interactions_d2_r01", 2, 0.1, 3),
    Candidate("interactions_d2_r1", 2, 1.0, 4),
    Candidate("interactions_d4_r0", 4, 0.0, 5),
    Candidate("interactions_d4_r0001", 4, 0.001, 6),
    Candidate("interactions_d4_r001", 4, 0.01, 7),
    Candidate("interactions_d4_r01", 4, 0.1, 8),
    Candidate("interactions_d4_r1", 4, 1.0, 9),
    Candidate("interactions_d6_r001", 6, 0.01, 10),
    Candidate("interactions_d6_r01", 6, 0.1, 11),
)
CANDIDATE_BY_ID = {candidate.candidate_id: candidate for candidate in CANDIDATES}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _stable_seed(namespace: str, values: tuple[object, ...]) -> int:
    payload = json.dumps([PROTOCOL_ID, namespace, *values], separators=(",", ":"))
    return int.from_bytes(hashlib.sha256(payload.encode()).digest()[:8], "big")


def _task_grid(repetitions: int, wild_draws: int, smoke: bool) -> list[dict[str, object]]:
    baselines = ("B1_design",) if smoke else tuple(BASELINES)
    candidates = (CANDIDATES[0],) if smoke else CANDIDATES
    reliabilities = (0.30,) if smoke else RELIABILITY_LEVELS
    nulls = ("independent_null",) if smoke else NULL_SCENARIOS
    effects = (0.50,) if smoke else SIGNAL_EFFECTS
    tasks: list[dict[str, object]] = []
    for baseline in baselines:
        conditions = [
            (scenario, reliability, 0.0)
            for scenario in nulls
            for reliability in reliabilities
        ] + [
            (SIGNAL_SCENARIO, reliability, beta)
            for reliability in reliabilities
            for beta in effects
        ]
        for candidate in candidates:
            for scenario, reliability, beta in conditions:
                for repetition in range(repetitions):
                    tasks.append(
                        {
                            "protocol_id": PROTOCOL_ID,
                            "baseline": baseline,
                            "candidate_id": candidate.candidate_id,
                            "scenario": scenario,
                            "reliability": reliability,
                            "beta": beta,
                            "repetition": repetition,
                            "wild_draws": wild_draws,
                        }
                    )
    return tasks


_DESIGN: pd.DataFrame | None = None


def _initialize_worker(design: pd.DataFrame) -> None:
    global _DESIGN
    _DESIGN = design
    SOURCE.PROTOCOL_ID = PROTOCOL_ID


def _run_cell(payload: dict[str, object]) -> dict[str, object]:
    if _DESIGN is None:
        raise RuntimeError("worker design was not initialized")
    candidate = CANDIDATE_BY_ID[str(payload["candidate_id"])]
    baseline = str(payload["baseline"])
    frame = SOURCE.simulate_frame(
        _DESIGN,
        baseline,
        str(payload["scenario"]),
        float(payload["reliability"]),
        float(payload["beta"]),
        int(payload["repetition"]),
    )
    identity = tuple(payload[column] for column in TASK_KEYS)
    try:
        result = orthogonal_score_audit(
            frame,
            "synthetic_metric",
            "synthetic_target",
            BASELINES[baseline],
            group_col="run_id",
            permutation_block_col="task",
            n_splits=5,
            degree=candidate.degree,
            ridge=candidate.ridge,
            nuisance_model="polynomial_ridge_interactions",
            wild_draws=int(payload["wild_draws"]),
            seed=_stable_seed("analysis", identity),
        )
        p_value = float(result["orthogonal_wild_p"])
        score = float(result["orthogonal_score_mean"])
        supported = bool(np.isfinite(p_value) and p_value <= DECISION_ALPHA)
        return {
            **payload,
            "status": "estimated",
            "n_groups": result["n_groups"],
            "orthogonal_wild_p": p_value,
            "orthogonal_score_mean": score,
            "positive_supported": bool(supported and score > 0),
            "supported": supported,
        }
    except (ImportError, RuntimeError, ValueError, np.linalg.LinAlgError) as error:
        return {**payload, "status": f"not_estimable: {error}"}


def _wilson(successes: int, total: int) -> tuple[float, float]:
    return SOURCE._wilson(successes, total)


def summarize(ledger: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for key, cell in ledger.groupby(GROUP_KEYS, sort=True, dropna=False):
        estimated = cell.loc[cell["status"].eq("estimated")]
        total = len(cell)
        support_count = int(estimated["supported"].fillna(False).sum())
        positive_count = int(estimated["positive_supported"].fillna(False).sum())
        support_low, support_high = _wilson(support_count, total)
        positive_low, positive_high = _wilson(positive_count, total)
        rows.append(
            dict(zip(GROUP_KEYS, key, strict=True))
            | {
                "planned_repetitions": total,
                "estimated_repetitions": len(estimated),
                "estimability_rate": len(estimated) / total,
                "support_count": support_count,
                "support_rate": support_count / total,
                "support_wilson_95_low": support_low,
                "support_wilson_95_high": support_high,
                "positive_support_count": positive_count,
                "positive_support_rate": positive_count / total,
                "positive_support_wilson_95_low": positive_low,
                "positive_support_wilson_95_high": positive_high,
            }
        )
    return pd.DataFrame(rows)


def diagnostics(summary: pd.DataFrame) -> dict[str, object]:
    rows: list[dict[str, object]] = []
    for (baseline, candidate_id), cell in summary.groupby(
        ["baseline", "candidate_id"], sort=True
    ):
        null = cell.loc[cell["scenario"].isin(NULL_SCENARIOS)]
        signal = cell.loc[cell["scenario"].eq(SIGNAL_SCENARIO) & cell["beta"].eq(0.50)]
        estimability = float(cell["estimability_rate"].min())
        max_null_raw = float(null["support_rate"].max())
        min_power_raw = float(signal["positive_support_rate"].min())
        screen_pass = bool(
            estimability >= 0.98 and max_null_raw <= 0.05 and min_power_raw >= 0.50
        )
        rows.append(
            {
                "baseline": baseline,
                "candidate_id": candidate_id,
                "minimum_estimability": estimability,
                "maximum_null_support_raw": max_null_raw,
                "minimum_beta_0_50_positive_power_raw": min_power_raw,
                "screen_pass": screen_pass,
            }
        )
    eligible = []
    for candidate in CANDIDATES:
        cells = [row for row in rows if row["candidate_id"] == candidate.candidate_id]
        if len(cells) == 3 and all(row["screen_pass"] for row in cells):
            eligible.append(candidate.candidate_id)
    return {
        "protocol_id": PROTOCOL_ID,
        "candidate_baseline_diagnostics": rows,
        "eligible_candidates_for_confirmation_design": eligible,
        "protected_association_open_authorized": False,
        "generalization_target_columns_read": False,
        "checkpoint_metric_columns_read": False,
    }


def _atomic_csv(frame: pd.DataFrame, path: Path) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    frame.to_csv(temporary, index=False)
    for attempt in range(20):
        try:
            temporary.replace(path)
            return
        except PermissionError:
            if attempt == 19:
                raise
            time.sleep(0.1 * (attempt + 1))


def _task_key(row: dict[str, object]) -> tuple[object, ...]:
    return tuple(row[column] for column in TASK_KEYS)


def run_tasks(
    tasks: list[dict[str, object]], output_dir: Path, workers: int, design: pd.DataFrame
) -> pd.DataFrame:
    output_dir.mkdir(parents=True, exist_ok=True)
    partial_path = output_dir / "development_ledger.partial.csv"
    rows: list[dict[str, object]] = []
    if partial_path.is_file():
        rows = pd.read_csv(partial_path).to_dict(orient="records")
        completed = {_task_key(row) for row in rows}
        tasks = [task for task in tasks if _task_key(task) not in completed]
        print(f"resuming={len(completed)} remaining={len(tasks)}", flush=True)
    with ProcessPoolExecutor(
        max_workers=workers, initializer=_initialize_worker, initargs=(design,)
    ) as executor:
        futures = [executor.submit(_run_cell, task) for task in tasks]
        for completed, future in enumerate(as_completed(futures), start=1):
            rows.append(future.result())
            if completed % 50 == 0 or completed == len(futures):
                _atomic_csv(pd.DataFrame(rows), partial_path)
                print(f"completed={completed}/{len(futures)}", flush=True)
    return pd.DataFrame(rows).sort_values(TASK_KEYS, ignore_index=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="PGDL nuisance development screen")
    parser.add_argument("ledger", type=Path)
    parser.add_argument("plan", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--smoke", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    design, control_encodings = SOURCE.load_design(args.ledger, args.plan)
    repetitions = 2 if args.smoke else DEFAULT_REPETITIONS
    wild_draws = 19 if args.smoke else DEFAULT_WILD_DRAWS
    tasks = _task_grid(repetitions, wild_draws, args.smoke)
    ledger = run_tasks(tasks, args.output_dir, args.workers, design)
    if len(ledger) != len(tasks) or ledger.duplicated(TASK_KEYS).any():
        raise RuntimeError("development row-count or duplicate-key gate failed")
    summary = summarize(ledger)
    diagnostic = diagnostics(summary)
    diagnostic["smoke"] = args.smoke

    ledger_path = args.output_dir / "development_ledger.csv"
    summary_path = args.output_dir / "development_summary.csv"
    diagnostic_path = args.output_dir / "DEVELOPMENT_DIAGNOSTIC.json"
    manifest_path = args.output_dir / "run_manifest.json"
    _atomic_csv(ledger, ledger_path)
    _atomic_csv(summary, summary_path)
    diagnostic_path.write_text(json.dumps(diagnostic, indent=2), encoding="utf-8")
    manifest = {
        "protocol_id": PROTOCOL_ID,
        "smoke": args.smoke,
        "planned_rows": len(tasks),
        "observed_rows": len(ledger),
        "repetitions": repetitions,
        "wild_draws": wild_draws,
        "decision_alpha": DECISION_ALPHA,
        "candidates": [asdict(candidate) for candidate in CANDIDATES],
        "control_encodings": control_encodings,
        "ledger_sha256": _sha256(args.ledger),
        "plan_sha256": _sha256(args.plan),
        "estimator_sha256": _sha256(REPO_ROOT / "mbe_eval" / "orthogonal.py"),
        "source_simulator_sha256": _sha256(SOURCE_PATH),
        "generalization_target_columns_read": False,
        "checkpoint_metric_columns_read": False,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    outputs = [ledger_path, summary_path, diagnostic_path, manifest_path]
    (args.output_dir / "SHA256SUMS").write_text(
        "\n".join(f"{_sha256(path)}  {path.name}" for path in outputs) + "\n",
        encoding="ascii",
    )
    print(json.dumps(diagnostic, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
