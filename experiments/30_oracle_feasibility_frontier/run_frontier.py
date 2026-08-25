from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from scipy.stats import t as student_t


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from mbe_eval.crossfit import _fold_ids  # noqa: E402
from mbe_eval.orthogonal import (  # noqa: E402
    _nuisance_design,
    _predict_nuisance,
    orthogonal_score_audit,
)


PROTOCOL_ID = "mbe3-oracle-feasibility-frontier-v1"
SAMPLE_SIZES = (24, 48, 96, 192)
REPETITIONS = {24: 500, 48: 500, 96: 250, 192: 250}
GEOMETRIES = ("image_like", "text_like")
BASELINES = ("B1_design", "B2_training_state", "B3_validation")
ICC_LEVELS = (0.30, 0.80)
NULL_SCENARIOS = (
    "independent_null",
    "additive_proxy_null",
    "nonlinear_proxy_null",
    "interaction_proxy_null",
    "heteroskedastic_proxy_null",
)
SIGNAL_SCENARIO = "shared_signal"
SIGNAL_EFFECTS = (0.25, 0.50)
METHODS = ("latent_ceiling", "observable_oracle", "learned_raw_d2", "learned_rank_d2")
TASK_KEYS = ["geometry", "n_configurations", "baseline", "scenario", "icc", "beta", "repetition"]
CELL_KEYS = TASK_KEYS[:-1]
SUMMARY_KEYS = [*CELL_KEYS, "method"]
CONTROLS = {
    "B1_design": ["factor_1", "factor_2", "factor_3", "factor_4", "seed_id"],
    "B2_training_state": ["factor_1", "factor_2", "factor_3", "factor_4", "seed_id", "train_loss"],
    "B3_validation": ["factor_1", "factor_2", "factor_3", "factor_4", "seed_id", "train_loss", "val_loss"],
}


def stable_seed(namespace: str, values: tuple[object, ...]) -> int:
    payload = json.dumps([PROTOCOL_ID, namespace, *values], separators=(",", ":"))
    return int.from_bytes(hashlib.sha256(payload.encode("utf-8")).digest()[:8], "big")


def _standardize(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    scale = float(np.std(values, ddof=1))
    return (values - float(np.mean(values))) / scale


def _factor_support(geometry: str) -> np.ndarray:
    if geometry == "image_like":
        return np.asarray(
            [(a, o, lr, aug) for a in (-1.5, -0.5, 0.5, 1.5) for o in (-1.0, 0.0, 1.0)
             for lr in (-1.0, 1.0) for aug in (-1.0, 1.0)],
            dtype=float,
        )
    if geometry == "text_like":
        return np.asarray(
            [(w, c, lr, d) for w in (-1.0, 0.0, 1.0) for c in (-1.0, 1.0)
             for lr in (-1.0, 1.0) for d in (-1.0, 1.0)],
            dtype=float,
        )
    raise ValueError(f"unknown geometry: {geometry}")


def _balanced_factors(geometry: str, n_configurations: int, rng: np.random.Generator) -> np.ndarray:
    support = _factor_support(geometry)
    repeats = math.ceil(n_configurations / len(support))
    factors = np.tile(support, (repeats, 1))[:n_configurations].copy()
    return factors[rng.permutation(n_configurations)]


def _surfaces(geometry: str, factors: np.ndarray) -> dict[str, np.ndarray]:
    x1, x2, x3, x4 = factors.T
    if geometry == "image_like":
        additive = 0.50 * x1 - 0.35 * x2 + 0.30 * x3 - 0.20 * x4
        nonlinear = additive + 0.45 * x1**2 - 0.40 * np.cos(np.pi * x3 / 2.0)
        interaction = nonlinear + 0.55 * x1 * x2 - 0.45 * x3 * x4
        threshold = interaction + 0.55 * (x1 > 0.0) * x3
    else:
        additive = 0.40 * x1 + 0.30 * x2 - 0.35 * x3 + 0.25 * x4
        nonlinear = additive - 0.50 * x1**2 + 0.35 * np.sin(np.pi * x2 / 2.0)
        interaction = nonlinear - 0.50 * x1 * x4 + 0.45 * x2 * x3
        threshold = interaction - 0.50 * (x1 >= 0.0) * x4
    return {name: _standardize(value) for name, value in {
        "additive": additive,
        "nonlinear": nonlinear,
        "interaction": interaction,
        "threshold": threshold,
    }.items()}


def simulate_frame(
    geometry: str,
    n_configurations: int,
    baseline: str,
    scenario: str,
    icc: float,
    beta: float,
    repetition: int,
) -> pd.DataFrame:
    # The simulation seed deliberately excludes baseline so baseline ladders are paired.
    rng = np.random.default_rng(stable_seed("simulation", (geometry, n_configurations, scenario, icc, beta, repetition)))
    group_factors = _balanced_factors(geometry, n_configurations, rng)
    factors = np.repeat(group_factors, 2, axis=0)
    surfaces = {key: np.repeat(value, 2) for key, value in _surfaces(geometry, group_factors).items()}
    groups = np.repeat(np.arange(n_configurations), 2)
    seed_id = np.tile(np.arange(2), n_configurations)
    latent = np.repeat(rng.normal(size=n_configurations), 2)
    noise = rng.normal(size=(2 * n_configurations, 5))

    train_mu = 0.60 * surfaces["additive"]
    train_loss = train_mu + 0.65 * noise[:, 0]
    val_base_mu = 0.45 * surfaces["nonlinear"]
    val_loss = val_base_mu + 0.30 * train_loss + 0.60 * noise[:, 1]

    if scenario == "independent_null":
        metric_surface = np.zeros_like(latent)
        target_surface = surfaces["interaction"]
        target_scale = np.ones_like(latent)
    elif scenario == "additive_proxy_null":
        metric_surface = surfaces["additive"]
        target_surface = 0.75 * surfaces["additive"] + 0.25 * surfaces["nonlinear"]
        target_scale = np.ones_like(latent)
    elif scenario == "nonlinear_proxy_null":
        metric_surface = surfaces["nonlinear"]
        target_surface = 0.70 * surfaces["nonlinear"] + 0.30 * surfaces["threshold"]
        target_scale = np.ones_like(latent)
    elif scenario == "interaction_proxy_null":
        metric_surface = surfaces["interaction"]
        target_surface = surfaces["threshold"]
        target_scale = np.ones_like(latent)
    elif scenario == "heteroskedastic_proxy_null":
        metric_surface = surfaces["threshold"]
        target_surface = surfaces["interaction"]
        target_scale = 0.40 + 0.85 * (surfaces["additive"] > 0.0)
    elif scenario == SIGNAL_SCENARIO:
        metric_surface = surfaces["interaction"]
        target_surface = surfaces["threshold"]
        target_scale = np.ones_like(latent)
    else:
        raise ValueError(f"unknown scenario: {scenario}")
    if scenario in NULL_SCENARIOS and beta != 0.0:
        raise ValueError("null scenarios require beta=0")
    if scenario == SIGNAL_SCENARIO and beta <= 0.0:
        raise ValueError("signal scenario requires beta>0")

    metric_mu = 0.65 * metric_surface
    target = target_surface + 0.35 * train_loss + 0.45 * val_loss + beta * latent + target_scale * noise[:, 3]
    metric = metric_mu + math.sqrt(icc) * latent + math.sqrt(1.0 - icc) * noise[:, 2]

    if baseline == "B1_design":
        target_mu = target_surface + 0.35 * train_mu + 0.45 * (val_base_mu + 0.30 * train_mu)
    elif baseline == "B2_training_state":
        target_mu = target_surface + 0.35 * train_loss + 0.45 * (val_base_mu + 0.30 * train_loss)
    elif baseline == "B3_validation":
        target_mu = target_surface + 0.35 * train_loss + 0.45 * val_loss
    else:
        raise ValueError(f"unknown baseline: {baseline}")

    frame = pd.DataFrame({
        "config_id": [f"cfg-{index:04d}" for index in groups],
        "seed_id": seed_id.astype(str),
        "factor_1": factors[:, 0].astype(str),
        "factor_2": factors[:, 1].astype(str),
        "factor_3": factors[:, 2].astype(str),
        "factor_4": factors[:, 3].astype(str),
        "train_loss": train_loss,
        "val_loss": val_loss,
        "metric": metric,
        "target": target,
        "metric_mu": metric_mu,
        "target_mu": target_mu,
        "latent": latent,
    })
    return frame


def _score_test(frame: pd.DataFrame, metric_residual: np.ndarray, target_residual: np.ndarray) -> tuple[float, float]:
    residuals = pd.DataFrame({
        "config_id": frame["config_id"].to_numpy(),
        "metric_residual": metric_residual,
        "target_residual": target_residual,
    }).groupby("config_id", sort=True).mean(numeric_only=True)
    scores = (residuals["metric_residual"] * residuals["target_residual"]).to_numpy(dtype=float)
    score_mean = float(np.mean(scores))
    score_se = float(np.std(scores, ddof=1)) / math.sqrt(len(scores))
    if not np.isfinite(score_se) or score_se <= 0:
        return score_mean, math.nan
    statistic = score_mean / score_se
    return score_mean, float(2.0 * student_t.sf(abs(statistic), df=len(scores) - 1))


def _learned_raw(frame: pd.DataFrame, controls: list[str], seed: int) -> tuple[float, float]:
    folds = _fold_ids(frame, 5, seed, "config_id")
    metric_prediction = np.full(len(frame), np.nan)
    target_prediction = np.full(len(frame), np.nan)
    for fold in np.unique(folds):
        test_idx = np.flatnonzero(folds == fold)
        train_idx = np.flatnonzero(folds != fold)
        train, test = frame.iloc[train_idx], frame.iloc[test_idx]
        x_train, x_test = _nuisance_design(train, test, controls, "polynomial_ridge_interactions", 2)
        metric_prediction[test_idx] = _predict_nuisance(
            x_train, train["metric"].to_numpy(dtype=float), x_test,
            "polynomial_ridge_interactions", 0.10, seed + int(fold) * 10007,
        )
        target_prediction[test_idx] = _predict_nuisance(
            x_train, train["target"].to_numpy(dtype=float), x_test,
            "polynomial_ridge_interactions", 0.10, seed + int(fold) * 10007 + 1,
        )
    return _score_test(
        frame,
        frame["metric"].to_numpy(dtype=float) - metric_prediction,
        frame["target"].to_numpy(dtype=float) - target_prediction,
    )


def _run_cell(task: dict[str, object]) -> dict[str, object]:
    identity = tuple(task[key] for key in TASK_KEYS)
    try:
        frame = simulate_frame(
            str(task["geometry"]), int(task["n_configurations"]), str(task["baseline"]),
            str(task["scenario"]), float(task["icc"]), float(task["beta"]), int(task["repetition"]),
        )
        target_residual = frame["target"].to_numpy(dtype=float) - frame["target_mu"].to_numpy(dtype=float)
        latent_result = _score_test(frame, frame["latent"].to_numpy(dtype=float), target_residual)
        oracle_result = _score_test(
            frame,
            frame["metric"].to_numpy(dtype=float) - frame["metric_mu"].to_numpy(dtype=float),
            target_residual,
        )
        analysis_seed = stable_seed("analysis", identity) % (2**32)
        learned_raw_result = _learned_raw(frame, CONTROLS[str(task["baseline"])], analysis_seed)
        rank = orthogonal_score_audit(
            frame, "metric", "target", CONTROLS[str(task["baseline"])],
            group_col="config_id", n_splits=5, degree=2, ridge=0.10,
            nuisance_model="polynomial_ridge_interactions", wild_draws=19,
            seed=analysis_seed, alpha=0.05,
        )
        results = {
            "latent_ceiling": latent_result,
            "observable_oracle": oracle_result,
            "learned_raw_d2": learned_raw_result,
            "learned_rank_d2": (float(rank["orthogonal_score_mean"]), float(rank["orthogonal_student_p"])),
        }
        row: dict[str, object] = {**task, "status": "estimated"}
        for method, (score, p_value) in results.items():
            row[f"{method}_score"] = score
            row[f"{method}_p"] = p_value
            row[f"{method}_support_a05"] = bool(np.isfinite(p_value) and p_value <= 0.05 and score > 0)
            row[f"{method}_support_a001"] = bool(np.isfinite(p_value) and p_value <= 0.001 and score > 0)
        return row
    except (ImportError, RuntimeError, ValueError, np.linalg.LinAlgError) as error:
        return {**task, "status": f"not_estimable: {type(error).__name__}: {error}"}


def task_grid(smoke: bool) -> list[dict[str, object]]:
    geometries = ("image_like",) if smoke else GEOMETRIES
    sizes = (24,) if smoke else SAMPLE_SIZES
    baselines = ("B1_design",) if smoke else BASELINES
    iccs = (0.30,) if smoke else ICC_LEVELS
    nulls = ("independent_null",) if smoke else NULL_SCENARIOS
    effects = (0.50,) if smoke else SIGNAL_EFFECTS
    tasks: list[dict[str, object]] = []
    for geometry in geometries:
        for n_configurations in sizes:
            repetitions = 2 if smoke else REPETITIONS[n_configurations]
            for baseline in baselines:
                conditions = [(scenario, icc, 0.0) for scenario in nulls for icc in iccs]
                conditions += [(SIGNAL_SCENARIO, icc, beta) for icc in iccs for beta in effects]
                for scenario, icc, beta in conditions:
                    for repetition in range(repetitions):
                        tasks.append({
                            "geometry": geometry, "n_configurations": n_configurations,
                            "baseline": baseline, "scenario": scenario, "icc": icc,
                            "beta": beta, "repetition": repetition,
                        })
    return tasks


def _wilson(successes: int, total: int) -> tuple[float, float]:
    if total <= 0:
        return math.nan, math.nan
    z = 1.959963984540054
    rate = successes / total
    denominator = 1.0 + z**2 / total
    center = (rate + z**2 / (2.0 * total)) / denominator
    half = z * math.sqrt(rate * (1.0 - rate) / total + z**2 / (4.0 * total**2)) / denominator
    return center - half, center + half


def summarize(ledger: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for key, cell in ledger.groupby(CELL_KEYS, sort=True, dropna=False):
        for method in METHODS:
            estimated = cell.loc[cell["status"].eq("estimated") & cell[f"{method}_p"].notna()]
            row = dict(zip(CELL_KEYS, key, strict=True)) | {"method": method}
            row["planned_repetitions"] = len(cell)
            row["estimated_repetitions"] = len(estimated)
            row["estimability_rate"] = len(estimated) / len(cell)
            for suffix in ("a05", "a001"):
                supported = int(estimated[f"{method}_support_{suffix}"].fillna(False).sum())
                low, high = _wilson(supported, len(cell))
                row[f"positive_support_count_{suffix}"] = supported
                row[f"positive_support_rate_{suffix}"] = supported / len(cell)
                row[f"positive_support_wilson_low_{suffix}"] = low
                row[f"positive_support_wilson_high_{suffix}"] = high
            rows.append(row)
    return pd.DataFrame(rows)


def diagnose(summary: pd.DataFrame) -> dict[str, object]:
    rows: list[dict[str, object]] = []
    for (method, n_configurations), cell in summary.groupby(["method", "n_configurations"], sort=True):
        null = cell.loc[cell["scenario"].isin(NULL_SCENARIOS)]
        signal = cell.loc[cell["scenario"].eq(SIGNAL_SCENARIO) & cell["beta"].eq(0.50)]
        row = {
            "method": method,
            "n_configurations": int(n_configurations),
            "minimum_estimability": float(cell["estimability_rate"].min()),
            "maximum_null_support_rate_a05": float(null["positive_support_rate_a05"].max()),
            "maximum_null_wilson_high_a05": float(null["positive_support_wilson_high_a05"].max()),
            "minimum_beta_0_50_power_a05": float(signal["positive_support_rate_a05"].min()),
            "minimum_beta_0_50_wilson_low_a05": float(signal["positive_support_wilson_low_a05"].min()),
        }
        row["strictly_calibrated"] = row["minimum_estimability"] >= 0.98 and row["maximum_null_wilson_high_a05"] <= 0.075
        row["useful_beta_0_50_power"] = row["minimum_beta_0_50_wilson_low_a05"] >= 0.50
        rows.append(row)
    return {
        "protocol_id": PROTOCOL_ID,
        "method_sample_size_diagnostics": rows,
        "protected_association_open_authorized": False,
        "generalization_target_columns_read": False,
        "checkpoint_metric_columns_read": False,
    }


def _write_csv(frame: pd.DataFrame, path: Path) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    frame.to_csv(temporary, index=False)
    temporary.replace(path)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run_tasks(tasks: list[dict[str, object]], output_dir: Path, workers: int) -> pd.DataFrame:
    output_dir.mkdir(parents=True, exist_ok=True)
    partial_path = output_dir / "frontier_ledger.partial.csv"
    rows: list[dict[str, object]] = []
    completed: set[tuple[object, ...]] = set()
    if partial_path.exists():
        partial = pd.read_csv(partial_path)
        rows = partial.to_dict("records")
        completed = {tuple(row[key] for key in TASK_KEYS) for row in rows}
    pending = [task for task in tasks if tuple(task[key] for key in TASK_KEYS) not in completed]
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(_run_cell, task) for task in pending]
        for count, future in enumerate(as_completed(futures), start=1):
            rows.append(future.result())
            if count % max(1, workers * 2) == 0 or count == len(pending):
                _write_csv(pd.DataFrame(rows).sort_values(TASK_KEYS), partial_path)
                print(f"completed={len(completed) + count}/{len(tasks)}", flush=True)
    return pd.DataFrame(rows).sort_values(TASK_KEYS, ignore_index=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Oracle feasibility and sample-size frontier")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    if not 1 <= args.workers <= 16:
        raise ValueError("workers must be between 1 and 16")
    tasks = task_grid(args.smoke)
    ledger = run_tasks(tasks, args.output_dir, args.workers)
    if len(ledger) != len(tasks) or ledger.duplicated(TASK_KEYS).any():
        raise RuntimeError("row-count or duplicate task-key gate failed")
    summary = summarize(ledger)
    diagnostic = diagnose(summary)
    diagnostic.update({"smoke": args.smoke, "planned_rows": len(tasks), "observed_rows": len(ledger)})

    ledger_path = args.output_dir / "frontier_ledger.csv"
    summary_path = args.output_dir / "frontier_summary.csv"
    diagnostic_path = args.output_dir / "FRONTIER_DIAGNOSTIC.json"
    manifest_path = args.output_dir / "run_manifest.json"
    _write_csv(ledger, ledger_path)
    _write_csv(summary, summary_path)
    diagnostic_path.write_text(json.dumps(diagnostic, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "protocol_id": PROTOCOL_ID, "smoke": args.smoke,
        "planned_rows": len(tasks), "observed_rows": len(ledger),
        "sample_sizes": SAMPLE_SIZES, "repetitions": REPETITIONS,
        "methods": METHODS, "runner_sha256": _sha256(Path(__file__)),
        "orthogonal_sha256": _sha256(REPO_ROOT / "mbe_eval" / "orthogonal.py"),
        "generalization_target_columns_read": False,
        "checkpoint_metric_columns_read": False,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    outputs = [ledger_path, summary_path, diagnostic_path, manifest_path]
    (args.output_dir / "SHA256SUMS").write_text(
        "\n".join(f"{_sha256(path)}  {path.name}" for path in outputs) + "\n", encoding="ascii"
    )
    print(json.dumps(diagnostic, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

