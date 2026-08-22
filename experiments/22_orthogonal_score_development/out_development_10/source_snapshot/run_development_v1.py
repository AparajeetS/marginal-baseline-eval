from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict, dataclass
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
from typing import Iterable

import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from mbe_eval import orthogonal_score_audit  # noqa: E402


SOURCE_EXPERIMENT = (
    REPO_ROOT / "experiments" / "21_design_matched_calibration" / "run_calibration.py"
)


def _load_design_source():
    spec = importlib.util.spec_from_file_location(
        "_mbe_design_matched_calibration_v1", SOURCE_EXPERIMENT
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load the design-matched simulator")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


DESIGN_SOURCE = _load_design_source()
BASELINES = DESIGN_SOURCE.BASELINES
ICC_LEVELS = DESIGN_SOURCE.ICC_LEVELS
NULL_SCENARIOS = DESIGN_SOURCE.NULL_SCENARIOS
SIGNAL_EFFECTS = DESIGN_SOURCE.SIGNAL_EFFECTS
SIGNAL_SCENARIOS = DESIGN_SOURCE.SIGNAL_SCENARIOS
get_design = DESIGN_SOURCE.get_design
simulate_frame = DESIGN_SOURCE.simulate_frame
wilson_interval = DESIGN_SOURCE.wilson_interval

PROTOCOL_ID = "mbe3-orthogonal-score-development-v1"
ALPHA = 0.05
DEFAULT_REPETITIONS = 20
DEFAULT_WILD_DRAWS = 499


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    nuisance_model: str
    degree: int
    complexity_rank: int


CANDIDATES = (
    Candidate("score_additive_d4", "polynomial_ridge", 4, 1),
    Candidate("score_additive_d6", "polynomial_ridge", 6, 2),
    Candidate("score_interactions_d4", "polynomial_ridge_interactions", 4, 3),
    Candidate("score_interactions_d6", "polynomial_ridge_interactions", 6, 4),
    Candidate("score_extra_trees", "extra_trees", 1, 5),
)
CANDIDATE_BY_ID = {candidate.candidate_id: candidate for candidate in CANDIDATES}
GROUP_KEYS = ["scope", "baseline", "candidate_id", "scenario", "icc", "beta"]
TASK_KEYS = [*GROUP_KEYS, "repetition"]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _stable_seed(namespace: str, values: Iterable[object]) -> int:
    payload = json.dumps(
        [PROTOCOL_ID, namespace, *values], separators=(",", ":"), sort_keys=False
    )
    return int.from_bytes(hashlib.sha256(payload.encode()).digest()[:8], "big")


def _task_grid(
    repetitions: int,
    wild_draws: int,
    candidate_ids: tuple[str, ...],
    smoke: bool,
) -> list[dict[str, object]]:
    scopes = ("image",) if smoke else ("image", "text")
    baselines = ("B1_design",) if smoke else tuple(BASELINES)
    iccs = (0.30,) if smoke else ICC_LEVELS
    null_scenarios = ("independent_null",) if smoke else NULL_SCENARIOS
    effects = (0.50,) if smoke else SIGNAL_EFFECTS
    candidates = (
        (CANDIDATE_BY_ID[candidate_ids[0]],)
        if smoke
        else tuple(CANDIDATE_BY_ID[candidate_id] for candidate_id in candidate_ids)
    )
    tasks: list[dict[str, object]] = []
    for scope in scopes:
        for baseline in baselines:
            for candidate in candidates:
                conditions = [
                    (scenario, icc, 0.0)
                    for scenario in null_scenarios
                    for icc in iccs
                ] + [
                    (scenario, icc, beta)
                    for scenario in SIGNAL_SCENARIOS
                    for icc in iccs
                    for beta in effects
                ]
                for scenario, icc, beta in conditions:
                    for repetition in range(repetitions):
                        identity = (
                            scope,
                            baseline,
                            candidate.candidate_id,
                            scenario,
                            icc,
                            beta,
                            repetition,
                        )
                        tasks.append(
                            {
                                "protocol_id": PROTOCOL_ID,
                                "scope": scope,
                                "baseline": baseline,
                                "candidate_id": candidate.candidate_id,
                                "scenario": scenario,
                                "icc": icc,
                                "beta": beta,
                                "repetition": repetition,
                                "wild_draws": wild_draws,
                                "simulation_seed": _stable_seed("simulation", identity),
                                "analysis_seed": _stable_seed("analysis", identity),
                            }
                        )
    return tasks


def _task_key(row: dict[str, object]) -> tuple[object, ...]:
    return tuple(row[column] for column in TASK_KEYS)


def _run_cell(payload: dict[str, object]) -> dict[str, object]:
    design = get_design(str(payload["scope"]))
    candidate = CANDIDATE_BY_ID[str(payload["candidate_id"])]
    frame = simulate_frame(
        design.scope,
        str(payload["scenario"]),
        float(payload["icc"]),
        float(payload["beta"]),
        int(payload["simulation_seed"]),
    )
    controls = BASELINES[str(payload["baseline"])][design.scope]
    try:
        result = orthogonal_score_audit(
            frame,
            "synthetic_metric",
            "synthetic_target",
            controls,
            group_col=design.group_col,
            permutation_block_col=design.block_col,
            n_splits=5,
            degree=candidate.degree,
            nuisance_model=candidate.nuisance_model,
            wild_draws=int(payload["wild_draws"]),
            seed=int(payload["analysis_seed"]),
            alpha=ALPHA,
        )
        p_value = float(result["orthogonal_wild_p"])
        score = float(result["orthogonal_score_mean"])
        supported = bool(np.isfinite(p_value) and p_value <= ALPHA)
        return {
            **payload,
            "status": "estimated",
            "orthogonal_score_mean": score,
            "orthogonal_score_t": result["orthogonal_score_t"],
            "orthogonal_student_p": result["orthogonal_student_p"],
            "orthogonal_wild_p": p_value,
            "partial_rank_slope": result["partial_rank_slope"],
            "partial_rank_slope_ci_low": result["partial_rank_slope_ci_low"],
            "partial_rank_slope_ci_high": result["partial_rank_slope_ci_high"],
            "supported": supported,
            "positive_supported": bool(supported and score > 0),
        }
    except (ImportError, RuntimeError, ValueError, np.linalg.LinAlgError) as error:
        return {**payload, "status": f"not_estimable: {error}"}


def summarize(ledger: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for key, cell in ledger.groupby(GROUP_KEYS, sort=True, dropna=False):
        estimated = cell.loc[cell["status"].eq("estimated")]
        total = len(cell)
        support_count = int(estimated["supported"].fillna(False).sum())
        positive_count = int(estimated["positive_supported"].fillna(False).sum())
        support_low, support_high = wilson_interval(support_count, total)
        positive_low, positive_high = wilson_interval(positive_count, total)
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


def development_diagnostics(summary: pd.DataFrame) -> dict[str, object]:
    diagnostics: list[dict[str, object]] = []
    for (scope, baseline, candidate_id), cell in summary.groupby(
        ["scope", "baseline", "candidate_id"], sort=True
    ):
        null = cell.loc[cell["scenario"].isin(NULL_SCENARIOS)]
        large_signal = cell.loc[
            cell["scenario"].isin(SIGNAL_SCENARIOS) & cell["beta"].eq(0.50)
        ]
        minimum_estimability = float(cell["estimability_rate"].min())
        maximum_null_upper = float(null["support_wilson_95_high"].max())
        minimum_power_lower = float(
            large_signal["positive_support_wilson_95_low"].min()
        )
        diagnostic_pass = bool(
            minimum_estimability >= 0.98
            and maximum_null_upper <= 0.10
            and minimum_power_lower >= 0.50
        )
        diagnostics.append(
            {
                "scope": scope,
                "baseline": baseline,
                "candidate_id": candidate_id,
                "minimum_estimability": minimum_estimability,
                "maximum_null_support_wilson_upper": maximum_null_upper,
                "minimum_beta_0_50_positive_power_wilson_lower": minimum_power_lower,
                "development_gate_pass": diagnostic_pass,
            }
        )
    return {
        "protocol_id": PROTOCOL_ID,
        "status": "development-only",
        "gate": {
            "minimum_estimability": 0.98,
            "maximum_null_support_wilson_upper": 0.10,
            "minimum_beta_0_50_positive_power_wilson_lower": 0.50,
        },
        "diagnostics": diagnostics,
        "protected_analysis_open_authorized": False,
        "next_step": (
            "Freeze candidate, untouched confirmation seeds, and comparator set only "
            "after development; this output cannot unlock protected associations."
        ),
    }


def run_tasks(
    tasks: list[dict[str, object]], output_dir: Path, workers: int
) -> pd.DataFrame:
    output_dir.mkdir(parents=True, exist_ok=True)
    partial_path = output_dir / "development_ledger.partial.csv"
    rows: list[dict[str, object]] = []
    completed_keys: set[tuple[object, ...]] = set()
    if partial_path.is_file():
        partial = pd.read_csv(partial_path)
        rows = partial.to_dict(orient="records")
        completed_keys = {_task_key(row) for row in rows}
        tasks = [task for task in tasks if _task_key(task) not in completed_keys]
        print(f"resuming={len(completed_keys)} remaining={len(tasks)}", flush=True)

    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(_run_cell, task) for task in tasks]
        for completed, future in enumerate(as_completed(futures), start=1):
            rows.append(future.result())
            if completed % 25 == 0 or completed == len(futures):
                pd.DataFrame(rows).to_csv(partial_path, index=False)
                print(f"completed={completed}/{len(futures)}", flush=True)
    return pd.DataFrame(rows).sort_values(TASK_KEYS, ignore_index=True)


def _write_hashes(output_dir: Path, paths: Iterable[Path]) -> None:
    lines = [f"{_sha256(path)}  {path.name}" for path in sorted(paths)]
    (output_dir / "SHA256SUMS").write_text("\n".join(lines) + "\n", encoding="ascii")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Known-truth development screen for grouped orthogonal score inference"
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--repetitions", type=int, default=DEFAULT_REPETITIONS)
    parser.add_argument("--wild-draws", type=int, default=DEFAULT_WILD_DRAWS)
    parser.add_argument(
        "--candidates",
        nargs="+",
        choices=tuple(CANDIDATE_BY_ID),
        default=tuple(CANDIDATE_BY_ID),
    )
    parser.add_argument("--smoke", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.workers < 1:
        raise ValueError("workers must be positive")
    if args.repetitions < 1:
        raise ValueError("repetitions must be positive")
    if args.wild_draws < 19:
        raise ValueError("wild-draws must be at least 19")
    repetitions = 2 if args.smoke else args.repetitions
    wild_draws = 19 if args.smoke else args.wild_draws
    candidate_ids = tuple(dict.fromkeys(args.candidates))
    tasks = _task_grid(repetitions, wild_draws, candidate_ids, args.smoke)
    active_candidate_ids = tuple(
        dict.fromkeys(str(task["candidate_id"]) for task in tasks)
    )
    ledger = run_tasks(tasks, args.output_dir, args.workers)
    if len(ledger) != len(tasks) or ledger.duplicated(TASK_KEYS).any():
        raise RuntimeError("development ledger failed row-count or duplicate-key gate")
    summary = summarize(ledger)
    diagnostic = development_diagnostics(summary)
    diagnostic["smoke"] = args.smoke
    diagnostic["warning"] = (
        "Smoke or development output never authorizes protected analysis."
    )

    ledger_path = args.output_dir / "development_ledger.csv"
    summary_path = args.output_dir / "development_summary.csv"
    diagnostic_path = args.output_dir / "DEVELOPMENT_DIAGNOSTIC.json"
    manifest_path = args.output_dir / "run_manifest.json"
    ledger.to_csv(ledger_path, index=False)
    summary.to_csv(summary_path, index=False)
    diagnostic_path.write_text(
        json.dumps(diagnostic, indent=2, allow_nan=False), encoding="utf-8"
    )
    manifest = {
        "protocol_id": PROTOCOL_ID,
        "status": "development-only",
        "smoke": args.smoke,
        "planned_rows": len(tasks),
        "observed_rows": len(ledger),
        "repetitions": repetitions,
        "wild_draws": wild_draws,
        "candidates": [asdict(CANDIDATE_BY_ID[item]) for item in active_candidate_ids],
        "icc_levels": [0.30] if args.smoke else list(ICC_LEVELS),
        "signal_effects": [0.50] if args.smoke else list(SIGNAL_EFFECTS),
        "null_scenarios": ["independent_null"] if args.smoke else list(NULL_SCENARIOS),
        "signal_scenarios": list(SIGNAL_SCENARIOS),
        "design_rows": {scope: len(get_design(scope).frame) for scope in ("image", "text")},
        "design_groups": {
            scope: int(get_design(scope).frame[get_design(scope).group_col].nunique())
            for scope in ("image", "text")
        },
        "design_source": str(SOURCE_EXPERIMENT.relative_to(REPO_ROOT)),
        "design_source_sha256": _sha256(SOURCE_EXPERIMENT),
        "estimator_source_sha256": _sha256(REPO_ROOT / "mbe_eval" / "orthogonal.py"),
        "protected_result_csv_read": False,
        "protected_analysis_open_authorized": False,
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, allow_nan=False), encoding="utf-8"
    )
    _write_hashes(
        args.output_dir,
        [ledger_path, summary_path, diagnostic_path, manifest_path],
    )
    print(json.dumps(diagnostic, indent=2, allow_nan=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
