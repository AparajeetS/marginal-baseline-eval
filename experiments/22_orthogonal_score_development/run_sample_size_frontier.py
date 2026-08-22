from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
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


SOURCE_RUNNER = Path(__file__).with_name("run_development.py")


def _load_source_runner():
    spec = importlib.util.spec_from_file_location(
        "_mbe_orthogonal_development_frontier_source", SOURCE_RUNNER
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

PROTOCOL_ID = "mbe3-orthogonal-sample-size-frontier-v1"
DEFAULT_REPETITIONS = 50
DEFAULT_WILD_DRAWS = 999
DECISION_ALPHA = 0.005
NUISANCE_MODEL = "polynomial_ridge_interactions"
DEGREE = 4
RIDGE = 10.0
PANELS = {"image": (1, 2, 4), "text": (1, 2, 4, 8)}
GROUP_KEYS = [
    "design_scope",
    "panels",
    "n_groups",
    "baseline",
    "scenario",
    "icc",
    "beta",
]
TASK_KEYS = [*GROUP_KEYS, "repetition"]


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


def _panel_frame(
    scope: str,
    panels: int,
    scenario: str,
    icc: float,
    beta: float,
    repetition: int,
) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for panel in range(panels):
        panel_identity = (scope, scenario, icc, beta, repetition, panel)
        frame = simulate_frame(
            scope,
            scenario,
            icc,
            beta,
            _stable_seed("simulation-panel", panel_identity),
        )
        frame = frame.copy()
        frame["panel_id"] = panel
        frame["config_id"] = (
            f"panel-{panel}-" + frame["config_id"].astype(str)
        )
        frames.append(frame)
    return pd.concat(frames, ignore_index=True)


def _task_grid(repetitions: int, wild_draws: int, smoke: bool) -> list[dict[str, object]]:
    panel_grid = {"image": (1,)} if smoke else PANELS
    baselines = ("B1_design",) if smoke else tuple(BASELINES)
    iccs = (0.30,) if smoke else ICC_LEVELS
    nulls = ("independent_null",) if smoke else NULL_SCENARIOS
    effects = (0.50,) if smoke else SIGNAL_EFFECTS
    tasks: list[dict[str, object]] = []
    for scope, panel_counts in panel_grid.items():
        base_groups = int(
            get_design(scope).frame[get_design(scope).group_col].nunique()
        )
        for panels in panel_counts:
            for baseline in baselines:
                conditions = [
                    (scenario, icc, 0.0)
                    for scenario in nulls
                    for icc in iccs
                ] + [
                    (scenario, icc, beta)
                    for scenario in SIGNAL_SCENARIOS
                    for icc in iccs
                    for beta in effects
                ]
                for scenario, icc, beta in conditions:
                    for repetition in range(repetitions):
                        tasks.append(
                            {
                                "protocol_id": PROTOCOL_ID,
                                "design_scope": scope,
                                "panels": panels,
                                "n_groups": base_groups * panels,
                                "baseline": baseline,
                                "scenario": scenario,
                                "icc": icc,
                                "beta": beta,
                                "repetition": repetition,
                                "wild_draws": wild_draws,
                            }
                        )
    return tasks


def _run_cell(payload: dict[str, object]) -> dict[str, object]:
    scope = str(payload["design_scope"])
    design = get_design(scope)
    frame = _panel_frame(
        scope,
        int(payload["panels"]),
        str(payload["scenario"]),
        float(payload["icc"]),
        float(payload["beta"]),
        int(payload["repetition"]),
    )
    controls = BASELINES[str(payload["baseline"])][scope]
    identity = tuple(payload[column] for column in TASK_KEYS)
    try:
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
            seed=_stable_seed("analysis", identity),
        )
        p_value = float(result["orthogonal_wild_p"])
        score = float(result["orthogonal_score_mean"])
        supported = bool(np.isfinite(p_value) and p_value <= DECISION_ALPHA)
        return {
            **payload,
            "status": "estimated",
            "orthogonal_wild_p": p_value,
            "orthogonal_score_mean": score,
            "partial_rank_slope": result["partial_rank_slope"],
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


def diagnostics(summary: pd.DataFrame) -> dict[str, object]:
    rows: list[dict[str, object]] = []
    for (scope, panels, n_groups, baseline), cell in summary.groupby(
        ["design_scope", "panels", "n_groups", "baseline"], sort=True
    ):
        null = cell.loc[cell["scenario"].isin(NULL_SCENARIOS)]
        signal = cell.loc[
            cell["scenario"].isin(SIGNAL_SCENARIOS) & cell["beta"].eq(0.50)
        ]
        max_null = float(null["support_wilson_95_high"].max())
        min_power = float(signal["positive_support_wilson_95_low"].min())
        rows.append(
            {
                "design_scope": scope,
                "panels": int(panels),
                "n_groups": int(n_groups),
                "baseline": baseline,
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
        "decision_alpha": DECISION_ALPHA,
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
    partial_path = output_dir / "frontier_ledger.partial.csv"
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
    parser = argparse.ArgumentParser(description="Configuration-count frontier")
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
        raise RuntimeError("frontier ledger failed row-count or duplicate-key gate")
    summary = summarize(ledger)
    decision = diagnostics(summary)
    decision["smoke"] = args.smoke
    ledger_path = args.output_dir / "frontier_ledger.csv"
    summary_path = args.output_dir / "frontier_summary.csv"
    diagnostic_path = args.output_dir / "FRONTIER_DIAGNOSTIC.json"
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
        "wild_draws": wild_draws,
        "decision_alpha": DECISION_ALPHA,
        "panels": {key: list(value) for key, value in PANELS.items()},
        "nested_panel_seeds": True,
        "candidate": {
            "nuisance_model": NUISANCE_MODEL,
            "degree": DEGREE,
            "ridge": RIDGE,
        },
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
