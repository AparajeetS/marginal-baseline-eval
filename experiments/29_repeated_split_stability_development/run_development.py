from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict, dataclass
import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from mbe_eval import repeated_split_orthogonal_audit  # noqa: E402


PROTOCOL_ID = "mbe3-repeated-split-stability-development-v1"
REPETITIONS = 20
WILD_DRAWS = 999
ICC_LEVELS = (0.30, 0.80)
NULL_SCENARIOS = (
    "independent_null",
    "additive_proxy_null",
    "nonlinear_proxy_null",
    "interaction_proxy_null",
    "heteroskedastic_proxy_null",
)
SIGNAL_SCENARIO = "increment"
SIGNAL_EFFECTS = (0.35, 0.50)
GROUP_KEYS = ["scope", "baseline", "candidate_id", "scenario", "icc", "beta"]
TASK_KEYS = [*GROUP_KEYS, "repetition"]


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    degree: int
    ridge: float
    repeats: int
    alpha: float
    complexity_rank: int


CANDIDATES = (
    Candidate("d2_r01_repeat3_a05", 2, 0.10, 3, 0.05, 1),
    Candidate("d2_r01_repeat3_a01", 2, 0.10, 3, 0.01, 2),
    Candidate("d2_r01_repeat5_a05", 2, 0.10, 5, 0.05, 3),
    Candidate("d4_r01_repeat3_a05", 4, 0.10, 3, 0.05, 4),
    Candidate("d4_r01_repeat3_a01", 4, 0.10, 3, 0.01, 5),
    Candidate("d4_r01_repeat5_a05", 4, 0.10, 5, 0.05, 6),
)
CANDIDATE_BY_ID = {candidate.candidate_id: candidate for candidate in CANDIDATES}


@dataclass(frozen=True)
class Design:
    scope: str
    frame: pd.DataFrame
    controls: dict[str, list[str]]
    group_col: str
    block_col: str


def _stable_seed(namespace: str, values: tuple[object, ...]) -> int:
    payload = json.dumps([PROTOCOL_ID, namespace, *values], separators=(",", ":"))
    return int.from_bytes(hashlib.sha256(payload.encode("utf-8")).digest()[:8], "big")


def _stable_id(prefix: str, values: tuple[object, ...]) -> str:
    payload = json.dumps(values, separators=(",", ":"))
    return f"{prefix}-{hashlib.sha256(payload.encode('utf-8')).hexdigest()[:12]}"


def _standardize(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    scale = float(np.std(values, ddof=1))
    if not np.isfinite(scale) or scale <= 0:
        return values - float(np.mean(values))
    return (values - float(np.mean(values))) / scale


def make_image48_design() -> Design:
    rows: list[dict[str, object]] = []
    for architecture in ("convnet", "resnet", "wide_resnet", "vit"):
        for optimizer in ("adamw", "sgd", "lion"):
            for lr_band in ("low", "high"):
                for augmentation in ("light", "strong"):
                    values = (architecture, optimizer, lr_band, augmentation)
                    config_id = _stable_id("image48", values)
                    for seed_id in ("9111", "9112"):
                        rows.append(
                            {
                                "config_id": config_id,
                                "seed_id": seed_id,
                                "architecture": architecture,
                                "optimizer": optimizer,
                                "lr_band": lr_band,
                                "augmentation": augmentation,
                            }
                        )
    frame = pd.DataFrame(rows)
    if len(frame) != 96 or frame["config_id"].nunique() != 48:
        raise RuntimeError("image48 grid construction failed")
    return Design(
        "image48",
        frame,
        {
            "B1_design": ["architecture", "optimizer", "lr_band", "augmentation", "seed_id"],
            "B2_training_state": ["architecture", "optimizer", "lr_band", "augmentation", "seed_id", "train_loss"],
            "B3_validation": ["architecture", "optimizer", "lr_band", "augmentation", "seed_id", "train_loss", "val_loss"],
        },
        "config_id",
        "architecture",
    )


def make_text24_design() -> Design:
    rows: list[dict[str, object]] = []
    for width in ("small", "medium", "large"):
        for context in ("short", "long"):
            for lr_band in ("low", "high"):
                for dropout in ("none", "regularized"):
                    values = (width, context, lr_band, dropout)
                    config_id = _stable_id("text24", values)
                    for seed_id in ("9211", "9212"):
                        rows.append(
                            {
                                "config_id": config_id,
                                "seed_id": seed_id,
                                "width": width,
                                "context": context,
                                "lr_band": lr_band,
                                "dropout": dropout,
                            }
                        )
    frame = pd.DataFrame(rows)
    if len(frame) != 48 or frame["config_id"].nunique() != 24:
        raise RuntimeError("text24 grid construction failed")
    return Design(
        "text24",
        frame,
        {
            "B1_design": ["width", "context", "lr_band", "dropout", "seed_id"],
            "B2_training_state": ["width", "context", "lr_band", "dropout", "seed_id", "train_loss"],
            "B3_validation": ["width", "context", "lr_band", "dropout", "seed_id", "train_loss", "val_loss"],
        },
        "config_id",
        "width",
    )


def get_design(scope: str) -> Design:
    if scope == "image48":
        return make_image48_design()
    if scope == "text24":
        return make_text24_design()
    raise ValueError(f"unknown scope: {scope}")


def _factor_codes(design: Design) -> np.ndarray:
    frame = design.frame
    if design.scope == "image48":
        columns = (
            frame["architecture"].map({"convnet": -1.5, "resnet": -0.5, "wide_resnet": 0.5, "vit": 1.5}),
            frame["optimizer"].map({"adamw": -1.0, "sgd": 0.0, "lion": 1.0}),
            frame["lr_band"].map({"low": -1.0, "high": 1.0}),
            frame["augmentation"].map({"light": -1.0, "strong": 1.0}),
        )
    else:
        columns = (
            frame["width"].map({"small": -1.0, "medium": 0.0, "large": 1.0}),
            frame["context"].map({"short": -1.0, "long": 1.0}),
            frame["lr_band"].map({"low": -1.0, "high": 1.0}),
            frame["dropout"].map({"none": -1.0, "regularized": 1.0}),
        )
    return np.column_stack([column.to_numpy(dtype=float) for column in columns])


def _surfaces(design: Design) -> dict[str, np.ndarray]:
    x = _factor_codes(design)
    additive = 0.50 * x[:, 0] - 0.35 * x[:, 1] + 0.30 * x[:, 2] - 0.20 * x[:, 3]
    nonlinear = additive + 0.45 * np.square(x[:, 0]) - 0.40 * np.cos(np.pi * x[:, 2] / 2.0)
    interaction = nonlinear + 0.55 * x[:, 0] * x[:, 1] - 0.45 * x[:, 2] * x[:, 3]
    threshold = interaction + 0.55 * (x[:, 0] > 0.0).astype(float) * x[:, 2]
    return {
        "additive": _standardize(additive),
        "nonlinear": _standardize(nonlinear),
        "interaction": _standardize(interaction),
        "threshold": _standardize(threshold),
    }


def _group_draws(frame: pd.DataFrame, rng: np.random.Generator) -> np.ndarray:
    groups = sorted(frame["config_id"].astype(str).unique())
    mapping = dict(zip(groups, rng.normal(size=len(groups)), strict=True))
    return frame["config_id"].astype(str).map(mapping).to_numpy(dtype=float)


def simulate_frame(scope: str, scenario: str, icc: float, beta: float, repetition: int) -> pd.DataFrame:
    design = get_design(scope)
    frame = design.frame.copy()
    rng = np.random.default_rng(_stable_seed("simulation", (scope, scenario, icc, beta, repetition)))
    surfaces = _surfaces(design)
    signal = _group_draws(frame, rng)
    train_state = _group_draws(frame, rng)
    validation_state = _group_draws(frame, rng)
    noise = rng.normal(size=(len(frame), 5))
    frame["train_loss"] = _standardize(0.60 * surfaces["additive"] + 0.70 * train_state + 0.45 * noise[:, 0])
    frame["val_loss"] = _standardize(0.40 * surfaces["nonlinear"] + 0.30 * train_state + 0.65 * validation_state + 0.40 * noise[:, 1])

    if scenario == "independent_null":
        metric_surface, target_surface, heteroskedastic = 0.0, surfaces["interaction"], 1.0
    elif scenario == "additive_proxy_null":
        metric_surface, target_surface, heteroskedastic = surfaces["additive"], 0.75 * surfaces["additive"] + 0.25 * surfaces["nonlinear"], 1.0
    elif scenario == "nonlinear_proxy_null":
        metric_surface, target_surface, heteroskedastic = surfaces["nonlinear"], 0.70 * surfaces["nonlinear"] + 0.30 * surfaces["threshold"], 1.0
    elif scenario == "interaction_proxy_null":
        metric_surface, target_surface, heteroskedastic = surfaces["interaction"], surfaces["threshold"], 1.0
    elif scenario == "heteroskedastic_proxy_null":
        metric_surface, target_surface = surfaces["threshold"], surfaces["interaction"]
        heteroskedastic = 0.40 + 0.85 * (surfaces["additive"] > 0.0).astype(float)
    elif scenario == SIGNAL_SCENARIO:
        metric_surface, target_surface, heteroskedastic = surfaces["interaction"], surfaces["threshold"], 1.0
    else:
        raise ValueError(f"unknown scenario: {scenario}")

    if scenario in NULL_SCENARIOS and beta != 0.0:
        raise ValueError("known-null scenarios require beta=0")
    if scenario == SIGNAL_SCENARIO and beta <= 0.0:
        raise ValueError("signal scenario requires beta>0")

    metric = 0.65 * np.asarray(metric_surface) + math.sqrt(icc) * signal + math.sqrt(1.0 - icc) * noise[:, 2]
    target = 0.80 * np.asarray(target_surface) + 0.35 * train_state + 0.45 * validation_state + beta * signal + np.asarray(heteroskedastic) * noise[:, 3]
    frame["synthetic_metric"] = _standardize(metric)
    frame["synthetic_target"] = _standardize(target)
    frame["negative_control"] = _standardize(noise[:, 4])
    return frame


def _task_grid(repetitions: int, wild_draws: int, smoke: bool) -> list[dict[str, object]]:
    scopes = ("image48",) if smoke else ("image48", "text24")
    baselines = ("B1_design",) if smoke else ("B1_design", "B2_training_state", "B3_validation")
    candidates = (CANDIDATES[0],) if smoke else CANDIDATES
    nulls = ("independent_null",) if smoke else NULL_SCENARIOS
    iccs = (0.30,) if smoke else ICC_LEVELS
    effects = (0.50,) if smoke else SIGNAL_EFFECTS
    tasks: list[dict[str, object]] = []
    for scope in scopes:
        for baseline in baselines:
            for candidate in candidates:
                conditions = [(scenario, icc, 0.0) for scenario in nulls for icc in iccs]
                conditions += [(SIGNAL_SCENARIO, icc, beta) for icc in iccs for beta in effects]
                for scenario, icc, beta in conditions:
                    for repetition in range(repetitions):
                        tasks.append({
                            "scope": scope,
                            "baseline": baseline,
                            "candidate_id": candidate.candidate_id,
                            "scenario": scenario,
                            "icc": icc,
                            "beta": beta,
                            "repetition": repetition,
                            "wild_draws": wild_draws,
                        })
    return tasks


def _run_cell(payload: dict[str, object]) -> dict[str, object]:
    candidate = CANDIDATE_BY_ID[str(payload["candidate_id"])]
    frame = simulate_frame(
        str(payload["scope"]),
        str(payload["scenario"]),
        float(payload["icc"]),
        float(payload["beta"]),
        int(payload["repetition"]),
    )
    design = get_design(str(payload["scope"]))
    identity = tuple(payload[column] for column in TASK_KEYS)
    try:
        result = repeated_split_orthogonal_audit(
            frame,
            "synthetic_metric",
            "synthetic_target",
            design.controls[str(payload["baseline"])],
            group_col=design.group_col,
            permutation_block_col=design.block_col,
            n_splits=5,
            degree=candidate.degree,
            ridge=candidate.ridge,
            nuisance_model="polynomial_ridge_interactions",
            wild_draws=int(payload["wild_draws"]),
            repeats=candidate.repeats,
            seed=_stable_seed("analysis", identity),
            alpha=candidate.alpha,
        )
        return {
            **payload,
            "status": "estimated",
            "n_groups": result["n_groups"],
            "stable_positive": bool(result["stable_positive"]),
            "positive_split_count": result["positive_split_count"],
            "maximum_orthogonal_wild_p": result["maximum_orthogonal_wild_p"],
            "minimum_orthogonal_score_mean": result["minimum_orthogonal_score_mean"],
        }
    except (ImportError, RuntimeError, ValueError, np.linalg.LinAlgError) as error:
        return {**payload, "status": f"not_estimable: {error}"}


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
    for key, cell in ledger.groupby(GROUP_KEYS, sort=True, dropna=False):
        estimated = cell.loc[cell["status"].eq("estimated")]
        total = len(cell)
        supported = int(estimated["stable_positive"].fillna(False).sum())
        low, high = _wilson(supported, total)
        rows.append(dict(zip(GROUP_KEYS, key, strict=True)) | {
            "planned_repetitions": total,
            "estimated_repetitions": len(estimated),
            "estimability_rate": len(estimated) / total,
            "positive_support_count": supported,
            "positive_support_rate": supported / total,
            "positive_support_wilson_95_low": low,
            "positive_support_wilson_95_high": high,
        })
    return pd.DataFrame(rows)


def diagnostics(summary: pd.DataFrame) -> dict[str, object]:
    rows: list[dict[str, object]] = []
    for (scope, baseline, candidate_id), cell in summary.groupby(["scope", "baseline", "candidate_id"], sort=True):
        null = cell.loc[cell["scenario"].isin(NULL_SCENARIOS)]
        signal = cell.loc[cell["scenario"].eq(SIGNAL_SCENARIO) & cell["beta"].eq(0.50)]
        rows.append({
            "scope": scope,
            "baseline": baseline,
            "candidate_id": candidate_id,
            "minimum_estimability": float(cell["estimability_rate"].min()),
            "maximum_null_support_raw": float(null["positive_support_rate"].max()),
            "minimum_beta_0_50_positive_power_raw": float(signal["positive_support_rate"].min()),
        })
    by_candidate: list[dict[str, object]] = []
    for candidate in CANDIDATES:
        cells = [row for row in rows if row["candidate_id"] == candidate.candidate_id]
        eligible = len(cells) == 6 and all(
            row["minimum_estimability"] >= 0.98
            and row["maximum_null_support_raw"] <= 0.05
            and row["minimum_beta_0_50_positive_power_raw"] >= 0.50
            for row in cells
        )
        by_candidate.append({
            **asdict(candidate),
            "scope_baseline_diagnostics": cells,
            "eligible_for_confirmation_design": eligible,
        })
    eligible = [row for row in by_candidate if row["eligible_for_confirmation_design"]]
    selected = None
    if eligible:
        selected = sorted(
            eligible,
            key=lambda row: (
                row["complexity_rank"],
                max(cell["maximum_null_support_raw"] for cell in row["scope_baseline_diagnostics"]),
                -min(cell["minimum_beta_0_50_positive_power_raw"] for cell in row["scope_baseline_diagnostics"]),
                row["candidate_id"],
            ),
        )[0]["candidate_id"]
    return {
        "protocol_id": PROTOCOL_ID,
        "candidate_diagnostics": by_candidate,
        "selected_candidate_for_confirmation": selected,
        "protected_association_open_authorized": False,
        "generalization_target_columns_read": False,
        "checkpoint_metric_columns_read": False,
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _write_csv(frame: pd.DataFrame, path: Path) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    frame.to_csv(temporary, index=False)
    temporary.replace(path)


def run_tasks(tasks: list[dict[str, object]], output_dir: Path, workers: int) -> pd.DataFrame:
    if workers < 1:
        raise ValueError("workers must be positive")
    output_dir.mkdir(parents=True, exist_ok=True)
    partial_path = output_dir / "development_ledger.partial.csv"
    existing: list[dict[str, object]] = []
    completed: set[tuple[object, ...]] = set()
    if partial_path.exists():
        partial = pd.read_csv(partial_path)
        existing = partial.to_dict("records")
        completed = {tuple(row[key] for key in TASK_KEYS) for row in existing}
    pending = [task for task in tasks if tuple(task[key] for key in TASK_KEYS) not in completed]
    rows = list(existing)
    if not pending:
        return pd.DataFrame(rows).sort_values(TASK_KEYS, ignore_index=True)
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(_run_cell, task) for task in pending]
        for completed_count, future in enumerate(as_completed(futures), start=1):
            rows.append(future.result())
            if completed_count % max(1, workers) == 0 or completed_count == len(pending):
                _write_csv(pd.DataFrame(rows).sort_values(TASK_KEYS), partial_path)
                print(f"completed={len(existing) + completed_count}/{len(tasks)}", flush=True)
    return pd.DataFrame(rows).sort_values(TASK_KEYS, ignore_index=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Repeated-split stability development")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--smoke", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repetitions = 2 if args.smoke else REPETITIONS
    wild_draws = 19 if args.smoke else WILD_DRAWS
    tasks = _task_grid(repetitions, wild_draws, args.smoke)
    ledger = run_tasks(tasks, args.output_dir, args.workers)
    if len(ledger) != len(tasks) or ledger.duplicated(TASK_KEYS).any():
        raise RuntimeError("development row-count or duplicate-key gate failed")
    summary = summarize(ledger)
    diagnostic = diagnostics(summary)
    diagnostic["smoke"] = args.smoke
    diagnostic["planned_rows"] = len(tasks)
    diagnostic["observed_rows"] = len(ledger)
    diagnostic["repetitions"] = repetitions
    diagnostic["wild_draws"] = wild_draws

    ledger_path = args.output_dir / "development_ledger.csv"
    summary_path = args.output_dir / "development_summary.csv"
    diagnostic_path = args.output_dir / "DEVELOPMENT_DIAGNOSTIC.json"
    manifest_path = args.output_dir / "run_manifest.json"
    _write_csv(ledger, ledger_path)
    _write_csv(summary, summary_path)
    diagnostic_path.write_text(json.dumps(diagnostic, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "protocol_id": PROTOCOL_ID,
        "smoke": args.smoke,
        "planned_rows": len(tasks),
        "observed_rows": len(ledger),
        "repetitions": repetitions,
        "wild_draws": wild_draws,
        "candidates": [asdict(candidate) for candidate in CANDIDATES],
        "estimator_sha256": _sha256(REPO_ROOT / "mbe_eval" / "orthogonal.py"),
        "runner_sha256": _sha256(Path(__file__)),
        "generalization_target_columns_read": False,
        "checkpoint_metric_columns_read": False,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    outputs = [ledger_path, summary_path, diagnostic_path, manifest_path]
    (args.output_dir / "SHA256SUMS").write_text(
        "\n".join(f"{_sha256(path)}  {path.name}" for path in outputs) + "\n",
        encoding="ascii",
    )
    print(json.dumps(diagnostic, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
