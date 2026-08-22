from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
import importlib.metadata
import importlib.util
import json
import math
from pathlib import Path
import sys
import time

import numpy as np
import pandas as pd
from scipy.stats import spearmanr


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from mbe_eval import cross_fitted_audit, orthogonal_score_audit  # noqa: E402
from mbe_eval.comparators import (  # noqa: E402
    cross_fitted_rank_residuals,
    gcm_rank_test,
    wgcm_est_rank_test,
)


SOURCE_PATH = (
    REPO_ROOT / "experiments" / "21_design_matched_calibration" / "run_calibration.py"
)


def _load_source():
    spec = importlib.util.spec_from_file_location("_mbe_comparator_design", SOURCE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load the design-matched simulator")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


SOURCE = _load_source()
PROTOCOL_ID = "mbe3-conditional-comparator-benchmark-v1"
SOURCE.PROTOCOL_ID = PROTOCOL_ID
REPETITIONS = 100
ORTHOGONAL_DRAWS = 4999
MBE_PERMUTATIONS = 999
MBE_BOOTSTRAP = 199
ALPHA = 0.05
ORTHOGONAL_ALPHA = 0.001
METRICS = ("synthetic_metric", "negative_control")
METHODS = (
    "raw_spearman",
    "residual_spearman",
    "gcm_student",
    "orthogonal_wild",
    "wgcm_est",
    "kci",
    "mbe_crossfit",
    "crt",
)
DATASET_KEYS = ["scope", "baseline", "scenario", "icc", "beta", "repetition"]
ROW_KEYS = [*DATASET_KEYS, "metric_name", "method"]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _stable_seed(namespace: str, values: tuple[object, ...]) -> int:
    payload = json.dumps([PROTOCOL_ID, namespace, *values], separators=(",", ":"))
    return int.from_bytes(hashlib.sha256(payload.encode()).digest()[:8], "big")


def _task_grid(repetitions: int, smoke: bool) -> list[dict[str, object]]:
    scopes = ("text",) if smoke else ("image", "text")
    baselines = ("B1_design",) if smoke else tuple(SOURCE.BASELINES)
    iccs = (0.30,) if smoke else SOURCE.ICC_LEVELS
    nulls = ("independent_null",) if smoke else SOURCE.NULL_SCENARIOS
    effects = (0.50,) if smoke else SOURCE.SIGNAL_EFFECTS
    tasks: list[dict[str, object]] = []
    for scope in scopes:
        for baseline in baselines:
            conditions = [
                (scenario, icc, 0.0) for scenario in nulls for icc in iccs
            ] + [
                ("interaction_increment", icc, beta)
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
                            "simulation_seed": _stable_seed("simulation", identity),
                        }
                    )
    return tasks


def _configuration_frame(
    frame: pd.DataFrame, group_col: str, controls: list[str]
) -> tuple[pd.DataFrame, list[str]]:
    config_controls = [control for control in controls if control != "seed_id"]
    aggregations: dict[str, str] = {
        "synthetic_metric": "mean",
        "negative_control": "mean",
        "synthetic_target": "mean",
    }
    for control in config_controls:
        if pd.api.types.is_numeric_dtype(frame[control]):
            aggregations[control] = "mean"
        else:
            if (frame.groupby(group_col, sort=False)[control].nunique() > 1).any():
                raise ValueError(f"categorical control varies within configuration: {control}")
            aggregations[control] = "first"
    grouped = frame.groupby(group_col, sort=True, as_index=False).agg(aggregations)
    return grouped, config_controls


def _method_row(
    payload: dict[str, object],
    metric_name: str,
    method: str,
    *,
    status: str = "estimated",
    score: float = math.nan,
    p_value: float = math.nan,
    supported: bool = False,
    positive_supported: bool = False,
    n_groups: int = 0,
    runtime_seconds: float = 0.0,
    estimand: str = "",
    detail: str = "",
) -> dict[str, object]:
    return {
        **payload,
        "metric_name": metric_name,
        "method": method,
        "status": status,
        "score": score,
        "p_value": p_value,
        "supported": supported,
        "positive_supported": positive_supported,
        "n_groups": n_groups,
        "runtime_seconds": runtime_seconds,
        "estimand": estimand,
        "detail": detail,
    }


def _kci_test(frame: pd.DataFrame, metric: str, controls: list[str]) -> float:
    from causallearn.utils.cit import CIT

    encoded = pd.get_dummies(frame[controls], drop_first=False, dtype=float)
    values = encoded.to_numpy(dtype=float)
    if values.size:
        scale = values.std(axis=0, ddof=1)
        keep = np.isfinite(scale) & (scale > 0)
        values = values[:, keep]
        if values.size:
            values = (values - values.mean(axis=0)) / values.std(axis=0, ddof=1)
    metric_values = frame[metric].rank(method="average", pct=True).to_numpy(dtype=float)
    target_values = frame["synthetic_target"].rank(method="average", pct=True).to_numpy(dtype=float)
    data = np.column_stack([metric_values, target_values, values])
    test = CIT(data, "kci", approx=True, est_width="median")
    return float(test(0, 1, list(range(2, data.shape[1]))))


def _run_method(
    payload: dict[str, object],
    frame: pd.DataFrame,
    config_frame: pd.DataFrame,
    config_controls: list[str],
    row_controls: list[str],
    group_col: str,
    block_col: str,
    metric_name: str,
    method: str,
    orthogonal_draws: int,
    mbe_permutations: int,
    mbe_bootstrap: int,
) -> dict[str, object]:
    started = time.perf_counter()
    identity = tuple(payload[key] for key in DATASET_KEYS) + (metric_name, method)
    seed = _stable_seed("analysis", identity)
    try:
        if method == "raw_spearman":
            result = spearmanr(config_frame[metric_name], config_frame["synthetic_target"])
            score, p_value = float(result.statistic), float(result.pvalue)
            supported = bool(np.isfinite(p_value) and p_value <= ALPHA)
            return _method_row(
                payload, metric_name, method, score=score, p_value=p_value,
                supported=supported, positive_supported=bool(supported and score > 0),
                n_groups=len(config_frame), runtime_seconds=time.perf_counter() - started,
                estimand="unconditional monotone association",
            )

        if method == "residual_spearman":
            residuals = cross_fitted_rank_residuals(
                config_frame, metric_name, "synthetic_target", config_controls,
                group_col=group_col, degree=2, ridge=0.1, seed=seed,
            )
            result = spearmanr(residuals["metric_residual"], residuals["target_residual"])
            score, p_value = float(result.statistic), float(result.pvalue)
            supported = bool(np.isfinite(p_value) and p_value <= ALPHA)
            return _method_row(
                payload, metric_name, method, score=score, p_value=p_value,
                supported=supported, positive_supported=bool(supported and score > 0),
                n_groups=len(config_frame), runtime_seconds=time.perf_counter() - started,
                estimand="monotone association of cross-fitted rank residuals",
            )

        if method == "gcm_student":
            result = gcm_rank_test(
                config_frame, metric_name, "synthetic_target", config_controls,
                group_col=group_col, degree=2, ridge=0.1, seed=seed,
            )
            score, p_value = float(result["score_mean"]), float(result["p_value"])
            supported = bool(np.isfinite(p_value) and p_value <= ALPHA)
            return _method_row(
                payload, metric_name, method, score=score, p_value=p_value,
                supported=supported, positive_supported=bool(supported and score > 0),
                n_groups=int(frame[group_col].nunique()), runtime_seconds=time.perf_counter() - started,
                estimand=str(result["estimand"]),
            )

        if method == "orthogonal_wild":
            result = orthogonal_score_audit(
                frame, metric_name, "synthetic_target", row_controls,
                group_col=group_col, permutation_block_col=block_col,
                n_splits=5, degree=2, ridge=0.1,
                nuisance_model="polynomial_ridge_interactions",
                wild_draws=orthogonal_draws, seed=seed,
            )
            score, p_value = float(result["orthogonal_score_mean"]), float(result["orthogonal_wild_p"])
            supported = bool(np.isfinite(p_value) and p_value <= ORTHOGONAL_ALPHA)
            return _method_row(
                payload, metric_name, method, score=score, p_value=p_value,
                supported=supported, positive_supported=bool(supported and score > 0),
                n_groups=int(result["n_groups"]), runtime_seconds=time.perf_counter() - started,
                estimand=str(result["estimand"]),
            )

        if method == "wgcm_est":
            result = wgcm_est_rank_test(
                config_frame, metric_name, "synthetic_target", config_controls,
                group_col=group_col, weight_fraction=0.30, degree=2, ridge=0.1, seed=seed,
            )
            score, p_value = float(result["score_mean"]), float(result["p_value"])
            supported = bool(np.isfinite(p_value) and p_value <= ALPHA)
            return _method_row(
                payload, metric_name, method, score=score, p_value=p_value,
                supported=supported, positive_supported=bool(supported and score > 0),
                n_groups=int(result["n_groups"]), runtime_seconds=time.perf_counter() - started,
                estimand=str(result["estimand"]),
            )

        if method == "kci":
            p_value = _kci_test(config_frame, metric_name, config_controls)
            supported = bool(np.isfinite(p_value) and p_value <= ALPHA)
            return _method_row(
                payload, metric_name, method, p_value=p_value,
                supported=supported, positive_supported=supported,
                n_groups=len(config_frame), runtime_seconds=time.perf_counter() - started,
                estimand="kernel conditional dependence",
                detail="non-directional",
            )

        if method == "mbe_crossfit":
            result = cross_fitted_audit(
                frame, metric_name, "synthetic_target", row_controls,
                group_col=group_col, permutation_block_col=block_col,
                n_splits=5, degree=2, ridge=0.1,
                nuisance_model="polynomial_ridge_interactions",
                permutations=mbe_permutations, bootstrap=mbe_bootstrap, seed=seed,
            )
            p_value = float(result["residual_p"])
            score = float(result["delta_mse"])
            supported = bool(
                np.isfinite(p_value) and p_value <= ALPHA
                and float(result["delta_mse_ci_low"]) > 0
            )
            return _method_row(
                payload, metric_name, method, score=score, p_value=p_value,
                supported=supported, positive_supported=supported,
                n_groups=int(frame[group_col].nunique()), runtime_seconds=time.perf_counter() - started,
                estimand="learner-relative out-of-fold predictive gain",
                detail=f"delta_mse_ci_low={float(result['delta_mse_ci_low']):.12g}",
            )

        if method == "crt":
            return _method_row(
                payload, metric_name, method,
                status="not_estimable: no validated metric-given-controls sampler",
                runtime_seconds=time.perf_counter() - started,
                estimand="conditional randomization test",
            )
        raise ValueError(f"unknown method: {method}")
    except (ImportError, RuntimeError, ValueError, np.linalg.LinAlgError) as error:
        return _method_row(
            payload, metric_name, method, status=f"not_estimable: {error}",
            runtime_seconds=time.perf_counter() - started,
        )


def _run_dataset(
    payload: dict[str, object], orthogonal_draws: int, mbe_permutations: int,
    mbe_bootstrap: int,
) -> list[dict[str, object]]:
    SOURCE.PROTOCOL_ID = PROTOCOL_ID
    scope = str(payload["scope"])
    design = SOURCE.get_design(scope)
    frame = SOURCE.simulate_frame(
        scope, str(payload["scenario"]), float(payload["icc"]),
        float(payload["beta"]), int(payload["simulation_seed"]),
    )
    controls = list(SOURCE.BASELINES[str(payload["baseline"])][scope])
    config_frame, config_controls = _configuration_frame(frame, design.group_col, controls)
    rows: list[dict[str, object]] = []
    for metric_name in METRICS:
        for method in METHODS:
            rows.append(
                _run_method(
                    payload, frame, config_frame, config_controls, controls,
                    design.group_col, design.block_col, metric_name, method,
                    orthogonal_draws, mbe_permutations, mbe_bootstrap,
                )
            )
    return rows


def _wilson(successes: int, total: int) -> tuple[float, float]:
    return SOURCE.wilson_interval(successes, total)


def summarize(ledger: pd.DataFrame) -> pd.DataFrame:
    group_keys = [
        "scope", "baseline", "metric_name", "method", "scenario", "icc", "beta"
    ]
    rows: list[dict[str, object]] = []
    for key, cell in ledger.groupby(group_keys, sort=True, dropna=False):
        estimated = cell.loc[cell["status"].eq("estimated")]
        total = len(cell)
        support_count = int(estimated["supported"].fillna(False).sum())
        positive_count = int(estimated["positive_supported"].fillna(False).sum())
        support_low, support_high = _wilson(support_count, total)
        positive_low, positive_high = _wilson(positive_count, total)
        rows.append(
            dict(zip(group_keys, key, strict=True))
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
                "runtime_seconds_median": float(estimated["runtime_seconds"].median()) if len(estimated) else math.nan,
            }
        )
    return pd.DataFrame(rows)


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


def run_tasks(
    tasks: list[dict[str, object]], output_dir: Path, workers: int,
    orthogonal_draws: int, mbe_permutations: int, mbe_bootstrap: int,
) -> pd.DataFrame:
    output_dir.mkdir(parents=True, exist_ok=True)
    partial_path = output_dir / "comparator_ledger.partial.csv"
    rows: list[dict[str, object]] = []
    completed_keys: set[tuple[object, ...]] = set()
    if partial_path.is_file():
        rows = pd.read_csv(partial_path).to_dict(orient="records")
        complete_counts = pd.DataFrame(rows).groupby(DATASET_KEYS).size()
        completed_keys = {tuple(key) for key, count in complete_counts.items() if count == len(METRICS) * len(METHODS)}
        tasks = [task for task in tasks if tuple(task[key] for key in DATASET_KEYS) not in completed_keys]
        print(f"resuming={len(completed_keys)} remaining={len(tasks)}", flush=True)
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(_run_dataset, task, orthogonal_draws, mbe_permutations, mbe_bootstrap)
            for task in tasks
        ]
        for completed, future in enumerate(as_completed(futures), start=1):
            rows.extend(future.result())
            if completed % 100 == 0 or completed == len(futures):
                _atomic_csv(pd.DataFrame(rows), partial_path)
                print(f"completed={completed}/{len(futures)}", flush=True)
    return pd.DataFrame(rows).sort_values(ROW_KEYS, ignore_index=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Conditional comparator benchmark")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--smoke", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repetitions = 2 if args.smoke else REPETITIONS
    orthogonal_draws = 19 if args.smoke else ORTHOGONAL_DRAWS
    mbe_permutations = 19 if args.smoke else MBE_PERMUTATIONS
    mbe_bootstrap = 19 if args.smoke else MBE_BOOTSTRAP
    tasks = _task_grid(repetitions, args.smoke)
    ledger = run_tasks(
        tasks, args.output_dir, args.workers,
        orthogonal_draws, mbe_permutations, mbe_bootstrap,
    )
    expected_rows = len(tasks) * len(METRICS) * len(METHODS)
    if len(ledger) != expected_rows or ledger.duplicated(ROW_KEYS).any():
        raise RuntimeError("comparator row-count or duplicate-key gate failed")
    summary = summarize(ledger)

    ledger_path = args.output_dir / "comparator_ledger.csv"
    summary_path = args.output_dir / "comparator_summary.csv"
    manifest_path = args.output_dir / "run_manifest.json"
    _atomic_csv(ledger, ledger_path)
    _atomic_csv(summary, summary_path)
    manifest = {
        "protocol_id": PROTOCOL_ID,
        "smoke": args.smoke,
        "planned_datasets": len(tasks),
        "planned_rows": expected_rows,
        "observed_rows": len(ledger),
        "repetitions": repetitions,
        "methods": list(METHODS),
        "metrics": list(METRICS),
        "orthogonal_draws": orthogonal_draws,
        "mbe_permutations": mbe_permutations,
        "mbe_bootstrap": mbe_bootstrap,
        "causal_learn_version": importlib.metadata.version("causal-learn"),
        "momentchi2_version": importlib.metadata.version("momentchi2"),
        "source_simulator_sha256": _sha256(SOURCE_PATH),
        "comparators_sha256": _sha256(REPO_ROOT / "mbe_eval" / "comparators.py"),
        "orthogonal_sha256": _sha256(REPO_ROOT / "mbe_eval" / "orthogonal.py"),
        "preregistration_sha256": _sha256(Path(__file__).with_name("PREREGISTRATION.md")),
        "protected_association_read": False,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    outputs = [ledger_path, summary_path, manifest_path]
    (args.output_dir / "SHA256SUMS").write_text(
        "\n".join(f"{_sha256(path)}  {path.name}" for path in outputs) + "\n",
        encoding="ascii",
    )
    print(json.dumps(manifest, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
