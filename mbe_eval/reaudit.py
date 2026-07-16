from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence

import pandas as pd
import numpy as np

from .core import audit_metric
from .crossfit import classify_increment_evidence, cross_fitted_audit


REQUIRED_MANIFEST_FIELDS = {
    "schema_version",
    "study_id",
    "title",
    "citation_url",
    "data_path",
    "row_id",
    "target",
    "metrics",
    "baseline_ladder",
}


def load_study_manifest(path: str | Path) -> dict[str, Any]:
    manifest_path = Path(path)
    with manifest_path.open("r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    if not isinstance(manifest, dict):
        raise ValueError("study manifest must contain one JSON object")
    return manifest


def _metric_columns(metrics: Sequence[Any]) -> list[str]:
    columns: list[str] = []
    for metric in metrics:
        if isinstance(metric, str):
            columns.append(metric)
        elif isinstance(metric, Mapping) and isinstance(metric.get("column"), str):
            columns.append(str(metric["column"]))
        else:
            raise ValueError("each metric must be a column name or an object with a column field")
    if not columns:
        raise ValueError("metrics must contain at least one metric column")
    return columns


def validate_study_manifest(manifest: Mapping[str, Any], df: pd.DataFrame) -> None:
    missing_fields = sorted(REQUIRED_MANIFEST_FIELDS - set(manifest))
    if missing_fields:
        raise ValueError(f"manifest is missing fields: {', '.join(missing_fields)}")
    if manifest["schema_version"] != 1:
        raise ValueError("unsupported manifest schema_version; expected 1")

    metrics = _metric_columns(manifest["metrics"])
    ladder = manifest["baseline_ladder"]
    if not isinstance(ladder, list) or not ladder:
        raise ValueError("baseline_ladder must contain at least one level")

    required_columns = {
        str(manifest["row_id"]),
        str(manifest["target"]),
        *metrics,
    }
    for level in ladder:
        if not isinstance(level, Mapping) or not {"level", "controls"} <= set(level):
            raise ValueError("each baseline level requires level and controls fields")
        if not isinstance(level["controls"], list):
            raise ValueError("baseline controls must be a JSON list")
        if level.get("nuisance_model", "polynomial_ridge") not in {
            "polynomial_ridge",
            "polynomial_ridge_interactions",
            "extra_trees",
        }:
            raise ValueError("unsupported baseline nuisance_model")
        required_columns.update(str(control) for control in level["controls"])

    group_column = manifest.get("group_column")
    if group_column:
        required_columns.add(str(group_column))
    for column in manifest.get("environment_columns", []):
        required_columns.add(str(column))

    missing_columns = sorted(required_columns - set(df.columns))
    if missing_columns:
        raise ValueError(f"dataset is missing manifest columns: {', '.join(missing_columns)}")
    row_id = str(manifest["row_id"])
    if df[row_id].isna().any():
        raise ValueError(f"row_id column {row_id!r} contains missing values")
    if df[row_id].duplicated().any():
        raise ValueError(f"row_id column {row_id!r} contains duplicates")


def _audit_scope(
    frame: pd.DataFrame,
    manifest: Mapping[str, Any],
    scope: str,
    *,
    permutations: int,
    bootstrap: int,
    seed: int,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    metrics = _metric_columns(manifest["metrics"])
    group_column = str(manifest.get("group_column") or "") or None
    usable_group = group_column
    if usable_group and frame[usable_group].nunique(dropna=True) < 2:
        usable_group = None

    for level_index, level in enumerate(manifest["baseline_ladder"]):
        controls = [str(control) for control in level["controls"]]
        degree = int(level.get("polynomial_degree", 4))
        nuisance_model = str(level.get("nuisance_model", "polynomial_ridge"))
        for metric_index, metric in enumerate(metrics):
            legacy = audit_metric(frame, metric, str(manifest["target"]), controls)
            crossfit = cross_fitted_audit(
                frame,
                metric,
                str(manifest["target"]),
                controls,
                group_col=usable_group,
                degree=degree,
                nuisance_model=nuisance_model,
                permutations=permutations,
                bootstrap=bootstrap,
                seed=seed + level_index * 1000 + metric_index,
            )
            rows.append(
                {
                    "study_id": manifest["study_id"],
                    "scope": scope,
                    "baseline_level": level["level"],
                    "metric": metric,
                    "target": manifest["target"],
                    "controls": ",".join(controls),
                    "nuisance_model": nuisance_model,
                    "n": legacy["n"],
                    "independence_units": crossfit["independence_units"],
                    "raw_r": legacy["raw_r"],
                    "partial_r": legacy["partial_r"],
                    "legacy_classification": legacy["classification"],
                    "crossfit_run_residual_r": crossfit["run_residual_r"],
                    "crossfit_residual_r": crossfit["residual_r"],
                    "crossfit_permutation_p": crossfit["residual_p"],
                    "crossfit_residual_ci_low": crossfit["residual_ci_low"],
                    "crossfit_residual_ci_high": crossfit["residual_ci_high"],
                    "baseline_mse": crossfit["baseline_mse"],
                    "augmented_mse": crossfit["augmented_mse"],
                    "delta_mse": crossfit["delta_mse"],
                    "delta_mse_ci_low": crossfit["delta_mse_ci_low"],
                    "delta_mse_ci_high": crossfit["delta_mse_ci_high"],
                    "relative_mse_improvement": crossfit["relative_mse_improvement"],
                }
            )
    return rows


def run_published_reaudit(
    df: pd.DataFrame,
    manifest: Mapping[str, Any],
    *,
    permutations: int = 199,
    bootstrap: int = 0,
    seed: int = 2026,
    minimum_scope_rows: int = 30,
) -> pd.DataFrame:
    """Run a manifest-declared audit without silently changing study scope."""

    validate_study_manifest(manifest, df)
    rows = _audit_scope(
        df, manifest, "pooled", permutations=permutations, bootstrap=bootstrap, seed=seed
    )
    for environment_column in manifest.get("environment_columns", []):
        for value, group in df.groupby(environment_column, dropna=False):
            if len(group) < minimum_scope_rows:
                continue
            scope = f"{environment_column}={value}"
            rows.extend(
                _audit_scope(
                    group,
                    manifest,
                    scope,
                    permutations=permutations,
                    bootstrap=bootstrap,
                    seed=seed + len(rows),
                )
            )
    report = pd.DataFrame(rows)
    report["crossfit_permutation_q"] = np.nan
    for _, index in report.groupby(["scope", "baseline_level"]).groups.items():
        group_index = np.asarray(index)
        p_values = report.loc[group_index, "crossfit_permutation_p"].to_numpy(dtype=float)
        finite = np.isfinite(p_values)
        if not finite.any():
            continue
        finite_positions = np.flatnonzero(finite)
        order = finite_positions[np.argsort(p_values[finite])]
        ranked = p_values[order] * len(order) / np.arange(1, len(order) + 1)
        adjusted = np.minimum.accumulate(ranked[::-1])[::-1]
        report.loc[group_index[order], "crossfit_permutation_q"] = np.minimum(adjusted, 1.0)
    report["increment_classification"] = [
        classify_increment_evidence(q_value, delta_low)
        for q_value, delta_low in zip(
            report["crossfit_permutation_q"], report["delta_mse_ci_low"]
        )
    ]
    return report


def reaudit_markdown(report: pd.DataFrame, manifest: Mapping[str, Any]) -> str:
    columns = [
        "scope",
        "baseline_level",
        "metric",
        "n",
        "independence_units",
        "raw_r",
        "partial_r",
        "crossfit_residual_r",
        "crossfit_residual_ci_low",
        "crossfit_residual_ci_high",
        "crossfit_permutation_q",
        "delta_mse",
        "delta_mse_ci_low",
        "delta_mse_ci_high",
        "increment_classification",
        "legacy_classification",
    ]
    lines = [
        f"# Published Metric Reaudit: {manifest['title']}",
        "",
        f"- Study ID: `{manifest['study_id']}`",
        f"- Citation: {manifest['citation_url']}",
        f"- Target: `{manifest['target']}`",
        "- Status: retrospective audit; this report does not replace the source paper.",
        "",
        "| Scope | Baseline | Metric | Runs | Units | Raw rho | Partial rho | Cross-fit residual rho [95% CI] | BH q | Delta MSE [95% CI] | Increment evidence | Legacy class |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for _, row in report[columns].iterrows():
        lines.append(
            "| {scope} | {baseline_level} | `{metric}` | {n} | {independence_units} | {raw_r:.3f} | "
            "{partial_r:.3f} | {crossfit_residual_r:.3f} [{crossfit_residual_ci_low:.3f}, {crossfit_residual_ci_high:.3f}] | "
            "{crossfit_permutation_q:.3f} | {delta_mse:.4f} [{delta_mse_ci_low:.4f}, {delta_mse_ci_high:.4f}] | "
            "{increment_classification} | {legacy_classification} |".format(
                **row.to_dict()
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation Boundary",
            "",
            "The baseline ladder defines different questions. A change across levels is a result, not permission to select the most favorable level. Cross-fitted residual association is descriptive and does not identify a causal effect.",
            "",
        ]
    )
    return "\n".join(lines)


def run_manifest_reaudit(
    manifest_path: str | Path,
    *,
    data_path: str | Path | None = None,
    output_prefix: str | Path | None = None,
    permutations: int = 199,
    bootstrap: int = 0,
    seed: int = 2026,
) -> pd.DataFrame:
    manifest_file = Path(manifest_path)
    manifest = load_study_manifest(manifest_file)
    dataset = Path(data_path) if data_path else manifest_file.parent / manifest["data_path"]
    df = pd.read_csv(dataset)
    report = run_published_reaudit(
        df,
        manifest,
        permutations=permutations,
        bootstrap=bootstrap,
        seed=seed,
    )
    if output_prefix:
        prefix = Path(output_prefix)
        prefix.parent.mkdir(parents=True, exist_ok=True)
        report.to_csv(prefix.with_suffix(".csv"), index=False)
        prefix.with_suffix(".md").write_text(
            reaudit_markdown(report, manifest),
            encoding="utf-8",
        )
    return report


__all__ = [
    "load_study_manifest",
    "reaudit_markdown",
    "run_manifest_reaudit",
    "run_published_reaudit",
    "validate_study_manifest",
]
