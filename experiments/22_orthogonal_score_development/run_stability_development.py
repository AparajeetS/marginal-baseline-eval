from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
import time

import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from mbe_eval import orthogonal_score_audit  # noqa: E402


SOURCE_RUNNER = Path(__file__).with_name("run_development.py")


def _load_source_runner():
    spec = importlib.util.spec_from_file_location(
        "_mbe_orthogonal_development_v2", SOURCE_RUNNER
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load experiment 22 development runner")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


SOURCE = _load_source_runner()
BASELINES = SOURCE.BASELINES
ICC_LEVELS = SOURCE.ICC_LEVELS
NULL_SCENARIOS = SOURCE.NULL_SCENARIOS
SIGNAL_EFFECTS = SOURCE.SIGNAL_EFFECTS
SIGNAL_SCENARIOS = SOURCE.SIGNAL_SCENARIOS
get_design = SOURCE.get_design
simulate_frame = SOURCE.simulate_frame
wilson_interval = SOURCE.wilson_interval

PROTOCOL_ID = "mbe3-orthogonal-split-stability-development-v1"
DEFAULT_REPETITIONS = 20
DEFAULT_WILD_DRAWS = 499
SPLIT_REPEATS = 3
CANDIDATE_ID = "configmean_interactions_d4_r10"
NUISANCE_MODEL = "polynomial_ridge_interactions"
DEGREE = 4
RIDGE = 10.0
GROUP_KEYS = ["scope", "baseline", "scenario", "icc", "beta"]
TASK_KEYS = [*GROUP_KEYS, "repetition"]
RULES = (
    "single_005",
    "unanimous_050",
    "unanimous_025",
    "unanimous_010",
    "two_of_three_010",
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _stable_seed(namespace: str, values: tuple[object, ...]) -> int:
    payload = json.dumps(
        [PROTOCOL_ID, namespace, *values], separators=(",", ":"), sort_keys=False
    )
    return int.from_bytes(hashlib.sha256(payload.encode()).digest()[:8], "big")


def _task_grid(repetitions: int, wild_draws: int, smoke: bool) -> list[dict[str, object]]:
    scopes = ("image",) if smoke else ("image", "text")
    baselines = ("B1_design",) if smoke else tuple(BASELINES)
    iccs = (0.30,) if smoke else ICC_LEVELS
    nulls = ("independent_null",) if smoke else NULL_SCENARIOS
    effects = (0.50,) if smoke else SIGNAL_EFFECTS
    tasks: list[dict[str, object]] = []
    for scope in scopes:
        for baseline in baselines:
            conditions = [
                (scenario, icc, 0.0) for scenario in nulls for icc in iccs
            ] + [
                (scenario, icc, beta)
                for scenario in SIGNAL_SCENARIOS
                for icc in iccs
                for beta in effects
            ]
            for scenario, icc, beta in conditions:
                for repetition in range(repetitions):
                    identity = (scope, scenario, icc, beta, repetition)
                    tasks.append(
                        {
                            "protocol_id": PROTOCOL_ID,
                            "scope": scope,
                            "baseline": baseline,
                            "scenario": scenario,
                            "icc": icc,
                            "beta": beta,
                            "repetition": repetition,
                            "wild_draws": wild_draws,
                            "simulation_seed": _stable_seed("simulation", identity),
                        }
                    )
    return tasks


def _same_sign_support(p_values: np.ndarray, scores: np.ndarray, threshold: float) -> bool:
    significant = p_values <= threshold
    return bool(
        significant.all() and ((scores > 0).all() or (scores < 0).all())
    )


def _run_cell(payload: dict[str, object]) -> dict[str, object]:
    design = get_design(str(payload["scope"]))
    frame = simulate_frame(
        design.scope,
        str(payload["scenario"]),
        float(payload["icc"]),
        float(payload["beta"]),
        int(payload["simulation_seed"]),
    )
    controls = BASELINES[str(payload["baseline"])][design.scope]
    p_values: list[float] = []
    scores: list[float] = []
    try:
        identity = tuple(payload[column] for column in TASK_KEYS)
        for repeat in range(SPLIT_REPEATS):
            result = orthogonal_score_audit(
                frame,
                "synthetic_metric",
                "synthetic_target",
                controls,
                group_col=design.group_col,
                permutation_block_col=design.block_col,
                n_splits=5,
                degree=DEGREE,
                ridge=RIDGE,
                nuisance_model=NUISANCE_MODEL,
                wild_draws=int(payload["wild_draws"]),
                seed=_stable_seed(f"analysis-split-{repeat}", identity),
            )
            p_values.append(float(result["orthogonal_wild_p"]))
            scores.append(float(result["orthogonal_score_mean"]))
        p_array = np.asarray(p_values)
        score_array = np.asarray(scores)
        positive_010 = (p_array <= 0.010) & (score_array > 0)
        negative_010 = (p_array <= 0.010) & (score_array < 0)
        decisions = {
            "single_005": bool(p_array[0] <= 0.005),
            "unanimous_050": _same_sign_support(p_array, score_array, 0.050),
            "unanimous_025": _same_sign_support(p_array, score_array, 0.025),
            "unanimous_010": _same_sign_support(p_array, score_array, 0.010),
            "two_of_three_010": bool(
                positive_010.sum() >= 2 or negative_010.sum() >= 2
            ),
        }
        positive_decisions = {
            "single_005": bool(p_array[0] <= 0.005 and score_array[0] > 0),
            "unanimous_050": bool(
                decisions["unanimous_050"] and (score_array > 0).all()
            ),
            "unanimous_025": bool(
                decisions["unanimous_025"] and (score_array > 0).all()
            ),
            "unanimous_010": bool(
                decisions["unanimous_010"] and (score_array > 0).all()
            ),
            "two_of_three_010": bool(positive_010.sum() >= 2),
        }
        row: dict[str, object] = {**payload, "status": "estimated"}
        for repeat, (p_value, score) in enumerate(zip(p_values, scores, strict=True)):
            row[f"split_{repeat}_p"] = p_value
            row[f"split_{repeat}_score"] = score
        for rule in RULES:
            row[f"{rule}_supported"] = decisions[rule]
            row[f"{rule}_positive_supported"] = positive_decisions[rule]
        return row
    except (ImportError, RuntimeError, ValueError, np.linalg.LinAlgError) as error:
        return {**payload, "status": f"not_estimable: {error}"}


def summarize(ledger: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for key, cell in ledger.groupby(GROUP_KEYS, sort=True, dropna=False):
        estimated = cell.loc[cell["status"].eq("estimated")]
        total = len(cell)
        row: dict[str, object] = dict(zip(GROUP_KEYS, key, strict=True))
        row.update(
            {
                "planned_repetitions": total,
                "estimated_repetitions": len(estimated),
                "estimability_rate": len(estimated) / total,
            }
        )
        for rule in RULES:
            for prefix in ("", "positive_"):
                column = f"{rule}_{prefix}supported" if prefix else f"{rule}_supported"
                label = f"{rule}_{prefix}support" if prefix else f"{rule}_support"
                count = int(estimated[column].fillna(False).sum())
                low, high = wilson_interval(count, total)
                row[f"{label}_count"] = count
                row[f"{label}_rate"] = count / total
                row[f"{label}_wilson_95_low"] = low
                row[f"{label}_wilson_95_high"] = high
        rows.append(row)
    return pd.DataFrame(rows)


def diagnostics(summary: pd.DataFrame) -> dict[str, object]:
    rows: list[dict[str, object]] = []
    for (scope, baseline), cell in summary.groupby(["scope", "baseline"], sort=True):
        null = cell.loc[cell["scenario"].isin(NULL_SCENARIOS)]
        signal = cell.loc[
            cell["scenario"].isin(SIGNAL_SCENARIOS) & cell["beta"].eq(0.50)
        ]
        for rule in RULES:
            max_null = float(null[f"{rule}_support_wilson_95_high"].max())
            min_power = float(
                signal[f"{rule}_positive_support_wilson_95_low"].min()
            )
            rows.append(
                {
                    "scope": scope,
                    "baseline": baseline,
                    "rule": rule,
                    "minimum_estimability": float(cell["estimability_rate"].min()),
                    "maximum_null_support_wilson_upper": max_null,
                    "minimum_beta_0_50_positive_power_wilson_lower": min_power,
                    "development_gate_pass": bool(
                        max_null <= 0.10 and min_power >= 0.50
                    ),
                }
            )
    return {
        "protocol_id": PROTOCOL_ID,
        "status": "development-only",
        "candidate_id": CANDIDATE_ID,
        "split_repeats": SPLIT_REPEATS,
        "diagnostics": rows,
        "protected_analysis_open_authorized": False,
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


def run_tasks(tasks: list[dict[str, object]], output_dir: Path, workers: int) -> pd.DataFrame:
    output_dir.mkdir(parents=True, exist_ok=True)
    partial_path = output_dir / "stability_ledger.partial.csv"
    rows: list[dict[str, object]] = []
    if partial_path.is_file():
        rows = pd.read_csv(partial_path).to_dict(orient="records")
        completed = {_task_key(row) for row in rows}
        tasks = [task for task in tasks if _task_key(task) not in completed]
        print(f"resuming={len(completed)} remaining={len(tasks)}", flush=True)
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(_run_cell, task) for task in tasks]
        for completed, future in enumerate(as_completed(futures), start=1):
            rows.append(future.result())
            if completed % 25 == 0 or completed == len(futures):
                _atomic_csv(pd.DataFrame(rows), partial_path)
                print(f"completed={completed}/{len(futures)}", flush=True)
    return pd.DataFrame(rows).sort_values(TASK_KEYS, ignore_index=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Repeated-split stability development")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--repetitions", type=int, default=DEFAULT_REPETITIONS)
    parser.add_argument("--wild-draws", type=int, default=DEFAULT_WILD_DRAWS)
    parser.add_argument("--smoke", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repetitions = 2 if args.smoke else args.repetitions
    wild_draws = 19 if args.smoke else args.wild_draws
    if args.workers < 1 or repetitions < 1 or wild_draws < 19:
        raise ValueError("workers/repetitions must be positive and wild-draws >= 19")
    tasks = _task_grid(repetitions, wild_draws, args.smoke)
    ledger = run_tasks(tasks, args.output_dir, args.workers)
    if len(ledger) != len(tasks) or ledger.duplicated(TASK_KEYS).any():
        raise RuntimeError("stability ledger failed row-count or duplicate-key gate")
    summary = summarize(ledger)
    decision = diagnostics(summary)
    decision["smoke"] = args.smoke
    ledger_path = args.output_dir / "stability_ledger.csv"
    summary_path = args.output_dir / "stability_summary.csv"
    diagnostic_path = args.output_dir / "STABILITY_DIAGNOSTIC.json"
    manifest_path = args.output_dir / "run_manifest.json"
    _atomic_csv(ledger, ledger_path)
    _atomic_csv(summary, summary_path)
    diagnostic_path.write_text(
        json.dumps(decision, indent=2, allow_nan=False), encoding="utf-8"
    )
    manifest = {
        "protocol_id": PROTOCOL_ID,
        "status": "development-only",
        "smoke": args.smoke,
        "planned_rows": len(tasks),
        "observed_rows": len(ledger),
        "repetitions": repetitions,
        "wild_draws_per_split": wild_draws,
        "split_repeats": SPLIT_REPEATS,
        "candidate": {
            "candidate_id": CANDIDATE_ID,
            "nuisance_model": NUISANCE_MODEL,
            "degree": DEGREE,
            "ridge": RIDGE,
        },
        "rules": list(RULES),
        "source_runner_sha256": _sha256(SOURCE_RUNNER),
        "estimator_sha256": _sha256(REPO_ROOT / "mbe_eval" / "orthogonal.py"),
        "protected_result_csv_read": False,
        "protected_analysis_open_authorized": False,
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, allow_nan=False), encoding="utf-8"
    )
    hashed = [ledger_path, summary_path, diagnostic_path, manifest_path]
    lines = [f"{_sha256(path)}  {path.name}" for path in sorted(hashed)]
    (args.output_dir / "SHA256SUMS").write_text(
        "\n".join(lines) + "\n", encoding="ascii"
    )
    print(json.dumps(decision, indent=2, allow_nan=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
