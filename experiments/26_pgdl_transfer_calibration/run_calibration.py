from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
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


PROTOCOL_ID = "mbe3-pgdl-transfer-calibration-v1"
TRANSFER_TASKS = ("task6", "task7", "task8", "task9")
EXPECTED_COUNTS = {"task6": 96, "task7": 48, "task8": 64, "task9": 32}
REPETITIONS = 100
WILD_DRAWS = 4999
DECISION_ALPHA = 0.001
RELIABILITY_LEVELS = (0.30, 0.80)
SIGNAL_EFFECTS = (0.20, 0.35, 0.50)
NULL_SCENARIOS = (
    "independent_null",
    "additive_proxy_null",
    "nonlinear_proxy_null",
    "interaction_proxy_null",
    "heteroskedastic_proxy_null",
)
SIGNAL_SCENARIO = "interaction_increment"
NUISANCE_MODEL = "polynomial_ridge_interactions"
DEGREE = 4
RIDGE = 10.0
BASELINES = {
    "B1_design": ["task", *[f"control_{index}" for index in range(6)]],
    "B2_training_loss": [
        "task",
        *[f"control_{index}" for index in range(6)],
        "train_loss",
    ],
    "B3_training_state": [
        "task",
        *[f"control_{index}" for index in range(6)],
        "train_loss",
        "train_acc",
    ],
}
GROUP_KEYS = ["baseline", "scenario", "reliability", "beta"]
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


def _standardize(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    scale = float(values.std(ddof=1))
    if not np.isfinite(scale) or scale <= 0:
        return values - float(values.mean())
    return (values - float(values.mean())) / scale


def _encode_control(values: pd.Series) -> tuple[np.ndarray, dict[str, object]]:
    numeric = pd.to_numeric(values, errors="coerce")
    if numeric.notna().all():
        return numeric.to_numpy(dtype=float), {"kind": "numeric"}
    labels = values.astype(str)
    levels = sorted(labels.unique().tolist())
    mapping = {level: index for index, level in enumerate(levels)}
    encoded = labels.map(mapping)
    if encoded.isna().any():
        raise ValueError("categorical control encoding produced missing values")
    return encoded.to_numpy(dtype=float), {
        "kind": "categorical_sorted_integer",
        "mapping": mapping,
    }


def load_design(
    ledger_path: Path, plan_path: Path
) -> tuple[pd.DataFrame, dict[str, dict[str, object]]]:
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    task_controls = {
        task: list(plan["task_controls"][task]) for task in TRANSFER_TASKS
    }
    allowed = {
        "run_id",
        "task",
        "train_loss",
        "train_acc",
        *(control for controls in task_controls.values() for control in controls),
    }
    frame = pd.read_csv(ledger_path, usecols=lambda column: column in allowed)
    frame = frame.loc[frame["task"].isin(TRANSFER_TASKS)].copy()
    counts = frame.groupby("task").size().to_dict()
    if counts != EXPECTED_COUNTS:
        raise ValueError(f"PGDL transfer counts changed: {counts}")
    if len(frame) != 240 or frame["run_id"].nunique() != 240:
        raise ValueError("PGDL transfer design requires 240 unique models")

    for index in range(6):
        frame[f"control_{index}"] = 0.0
    encodings: dict[str, dict[str, object]] = {}
    for task, controls in task_controls.items():
        task_rows = frame["task"].eq(task)
        for index, control in enumerate(controls):
            values, encoding = _encode_control(frame.loc[task_rows, control])
            frame.loc[task_rows, f"control_{index}"] = values
            encodings[f"{task}:{control}"] = {
                "slot": f"control_{index}",
                **encoding,
            }
    required = [column for controls in BASELINES.values() for column in controls]
    required = list(dict.fromkeys(["run_id", *required]))
    if frame[required].isna().any(axis=None):
        raise ValueError("PGDL transfer design contains missing required values")
    design = frame[required].sort_values("run_id").reset_index(drop=True)
    return design, encodings


def _surface_matrix(frame: pd.DataFrame, controls: list[str]) -> np.ndarray:
    columns: list[np.ndarray] = []
    task_codes = frame["task"].map(
        {"task6": -1.5, "task7": -0.5, "task8": 0.5, "task9": 1.5}
    )
    columns.append(task_codes.to_numpy(dtype=float) / 1.5)
    for control in controls:
        if control == "task":
            continue
        ranked = frame.groupby("task", sort=False)[control].rank(
            method="average", pct=True
        )
        columns.append(2.0 * ranked.to_numpy(dtype=float) - 1.0)
    return np.column_stack(columns)


def _surfaces(frame: pd.DataFrame, controls: list[str]) -> dict[str, np.ndarray]:
    x = _surface_matrix(frame, controls)
    additive = np.zeros(len(frame), dtype=float)
    for index in range(x.shape[1]):
        additive += ((-1.0) ** index) * x[:, index] / math.sqrt(index + 1.0)
    nonlinear = additive.copy()
    if x.shape[1] > 2:
        nonlinear += 0.65 * np.square(x[:, 1]) - 0.45 * np.cos(np.pi * x[:, 2])
    interaction = nonlinear.copy()
    if x.shape[1] > 3:
        interaction += 0.70 * x[:, 0] * x[:, 1] - 0.55 * x[:, 2] * x[:, 3]
    if x.shape[1] > 5:
        interaction += 0.45 * x[:, 1] * x[:, 5]
    threshold = interaction.copy()
    if x.shape[1] > 2:
        threshold += 0.60 * (x[:, 1] > 0).astype(float) * x[:, 2]
    return {
        "additive": _standardize(additive),
        "nonlinear": _standardize(nonlinear),
        "interaction": _standardize(interaction),
        "threshold": _standardize(threshold),
    }


def simulate_frame(
    design: pd.DataFrame,
    baseline: str,
    scenario: str,
    reliability: float,
    beta: float,
    repetition: int,
) -> pd.DataFrame:
    frame = design.copy()
    controls = BASELINES[baseline]
    surfaces = _surfaces(frame, controls)
    identity = (baseline, scenario, reliability, beta, repetition)
    rng = np.random.default_rng(_stable_seed("simulation", identity))
    latent = rng.normal(size=len(frame))
    noise = rng.normal(size=(len(frame), 3))

    if scenario == "independent_null":
        metric_surface = np.zeros(len(frame), dtype=float)
        target_surface = surfaces["interaction"]
        heteroskedastic = np.ones(len(frame), dtype=float)
    elif scenario == "additive_proxy_null":
        metric_surface = surfaces["additive"]
        target_surface = 0.75 * surfaces["additive"] + 0.25 * surfaces["nonlinear"]
        heteroskedastic = np.ones(len(frame), dtype=float)
    elif scenario == "nonlinear_proxy_null":
        metric_surface = surfaces["nonlinear"]
        target_surface = 0.65 * surfaces["nonlinear"] + 0.35 * surfaces["threshold"]
        heteroskedastic = np.ones(len(frame), dtype=float)
    elif scenario == "interaction_proxy_null":
        metric_surface = surfaces["interaction"]
        target_surface = surfaces["threshold"]
        heteroskedastic = np.ones(len(frame), dtype=float)
    elif scenario == "heteroskedastic_proxy_null":
        metric_surface = surfaces["threshold"]
        target_surface = surfaces["interaction"]
        heteroskedastic = 0.45 + 0.75 * (surfaces["additive"] > 0).astype(float)
    elif scenario == SIGNAL_SCENARIO:
        metric_surface = surfaces["interaction"]
        target_surface = surfaces["threshold"]
        heteroskedastic = np.ones(len(frame), dtype=float)
    else:
        raise ValueError(f"unknown scenario: {scenario}")

    if scenario in NULL_SCENARIOS and beta != 0.0:
        raise ValueError("null scenario requires beta zero")
    if scenario == SIGNAL_SCENARIO and beta <= 0.0:
        raise ValueError("signal scenario requires positive beta")
    metric = (
        0.65 * metric_surface
        + math.sqrt(reliability) * latent
        + math.sqrt(1.0 - reliability) * noise[:, 0]
    )
    target = 0.80 * target_surface + beta * latent + heteroskedastic * noise[:, 1]
    frame["synthetic_metric"] = _standardize(metric)
    frame["synthetic_target"] = _standardize(target)
    frame["negative_control"] = _standardize(noise[:, 2])
    return frame


def _task_grid(repetitions: int, wild_draws: int, smoke: bool) -> list[dict[str, object]]:
    baselines = ("B1_design",) if smoke else tuple(BASELINES)
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
        for scenario, reliability, beta in conditions:
            for repetition in range(repetitions):
                tasks.append(
                    {
                        "protocol_id": PROTOCOL_ID,
                        "baseline": baseline,
                        "scenario": scenario,
                        "reliability": reliability,
                        "beta": beta,
                        "repetition": repetition,
                        "wild_draws": wild_draws,
                    }
                )
    return tasks


_DESIGN: pd.DataFrame | None = None


def _run_cell(payload: dict[str, object]) -> dict[str, object]:
    if _DESIGN is None:
        raise RuntimeError("worker design was not initialized")
    baseline = str(payload["baseline"])
    frame = simulate_frame(
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
            "n_groups": result["n_groups"],
            "orthogonal_wild_p": p_value,
            "orthogonal_score_mean": score,
            "partial_rank_slope": result["partial_rank_slope"],
            "supported": supported,
            "positive_supported": bool(supported and score > 0),
        }
    except (ImportError, RuntimeError, ValueError, np.linalg.LinAlgError) as error:
        return {**payload, "status": f"not_estimable: {error}"}


def _wilson(successes: int, total: int) -> tuple[float, float]:
    z = 1.959963984540054
    rate = successes / total
    denominator = 1.0 + z**2 / total
    center = (rate + z**2 / (2.0 * total)) / denominator
    half = z * math.sqrt(rate * (1.0 - rate) / total + z**2 / (4.0 * total**2)) / denominator
    return center - half, center + half


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


def eligibility(summary: pd.DataFrame) -> dict[str, object]:
    decisions: list[dict[str, object]] = []
    for baseline, cell in summary.groupby("baseline", sort=True):
        null = cell.loc[cell["scenario"].isin(NULL_SCENARIOS)]
        signal = cell.loc[cell["scenario"].eq(SIGNAL_SCENARIO) & cell["beta"].eq(0.50)]
        estimability = float(cell["estimability_rate"].min())
        max_null = float(null["support_wilson_95_high"].max())
        min_power = float(signal["positive_support_wilson_95_low"].min())
        passed = bool(estimability >= 0.98 and max_null <= 0.10 and min_power >= 0.50)
        decisions.append(
            {
                "baseline": baseline,
                "minimum_estimability": estimability,
                "maximum_null_support_wilson_upper": max_null,
                "minimum_beta_0_50_positive_power_wilson_lower": min_power,
                "pass": passed,
            }
        )
    global_pass = bool(len(decisions) == 3 and all(row["pass"] for row in decisions))
    return {
        "protocol_id": PROTOCOL_ID,
        "global_pass": global_pass,
        "baseline_decisions": decisions,
        "eligible_to_freeze_pgdl_transfer_analysis": global_pass,
        "checkpoint_metric_association_open_authorized": False,
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
    tasks: list[dict[str, object]],
    output_dir: Path,
    workers: int,
    design: pd.DataFrame,
) -> pd.DataFrame:
    output_dir.mkdir(parents=True, exist_ok=True)
    partial_path = output_dir / "calibration_ledger.partial.csv"
    rows: list[dict[str, object]] = []
    if partial_path.is_file():
        rows = pd.read_csv(partial_path).to_dict(orient="records")
        completed = {_task_key(row) for row in rows}
        tasks = [task for task in tasks if _task_key(task) not in completed]
        print(f"resuming={len(completed)} remaining={len(tasks)}", flush=True)
    with ProcessPoolExecutor(
        max_workers=workers,
        initializer=_initialize_worker,
        initargs=(design,),
    ) as executor:
        futures = [executor.submit(_run_cell, task) for task in tasks]
        for completed, future in enumerate(as_completed(futures), start=1):
            rows.append(future.result())
            if completed % 25 == 0 or completed == len(futures):
                _atomic_csv(pd.DataFrame(rows), partial_path)
                print(f"completed={completed}/{len(futures)}", flush=True)
    return pd.DataFrame(rows).sort_values(TASK_KEYS, ignore_index=True)


def _initialize_worker(design: pd.DataFrame) -> None:
    global _DESIGN
    _DESIGN = design


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="PGDL transfer known-truth calibration")
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
    global _DESIGN
    _DESIGN, control_encodings = load_design(args.ledger, args.plan)
    repetitions = 2 if args.smoke else REPETITIONS
    wild_draws = 19 if args.smoke else WILD_DRAWS
    tasks = _task_grid(repetitions, wild_draws, args.smoke)
    ledger = run_tasks(tasks, args.output_dir, args.workers, _DESIGN)
    if len(ledger) != len(tasks) or ledger.duplicated(TASK_KEYS).any():
        raise RuntimeError("PGDL calibration failed row-count or duplicate-key gate")
    summary = summarize(ledger)
    decision = eligibility(summary)
    decision["smoke"] = args.smoke
    if args.smoke:
        decision["global_pass"] = False
        decision["eligible_to_freeze_pgdl_transfer_analysis"] = False

    ledger_path = args.output_dir / "calibration_ledger.csv"
    summary_path = args.output_dir / "calibration_summary.csv"
    decision_path = args.output_dir / "FINAL_ELIGIBILITY.json"
    manifest_path = args.output_dir / "run_manifest.json"
    _atomic_csv(ledger, ledger_path)
    _atomic_csv(summary, summary_path)
    decision_path.write_text(json.dumps(decision, indent=2, allow_nan=False), encoding="utf-8")
    manifest = {
        "protocol_id": PROTOCOL_ID,
        "smoke": args.smoke,
        "planned_rows": len(tasks),
        "observed_rows": len(ledger),
        "repetitions": repetitions,
        "wild_draws": wild_draws,
        "decision_alpha": DECISION_ALPHA,
        "transfer_counts": EXPECTED_COUNTS,
        "pooled_models": 240,
        "control_encodings": control_encodings,
        "ledger_sha256": _sha256(args.ledger),
        "plan_sha256": _sha256(args.plan),
        "estimator_sha256": _sha256(REPO_ROOT / "mbe_eval" / "orthogonal.py"),
        "preregistration_sha256": _sha256(Path(__file__).with_name("PREREGISTRATION.md")),
        "generalization_target_columns_read": False,
        "checkpoint_metric_columns_read": False,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, allow_nan=False), encoding="utf-8")
    hashed = [ledger_path, summary_path, decision_path, manifest_path]
    lines = [f"{_sha256(path)}  {path.name}" for path in sorted(hashed)]
    (args.output_dir / "SHA256SUMS").write_text("\n".join(lines) + "\n", encoding="ascii")
    print(json.dumps(decision, indent=2, allow_nan=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
