from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd


def validate_utility_table(
    data: pd.DataFrame,
    *,
    task_col: str = "task_family",
    metric_col: str = "metric",
    utility_col: str = "utility",
) -> None:
    """Validate a task-by-metric utility table used for selector evaluation."""
    required = {task_col, metric_col, utility_col}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"missing selector columns: {sorted(missing)}")
    if data.empty:
        raise ValueError("selector utility table is empty")
    if data[[task_col, metric_col]].isna().any().any():
        raise ValueError("task and metric identifiers cannot be missing")
    if data.duplicated([task_col, metric_col]).any():
        raise ValueError("task-metric pairs must be unique")
    utility = pd.to_numeric(data[utility_col], errors="coerce").to_numpy()
    if not np.isfinite(utility).all():
        raise ValueError("utility values must be finite")


def leave_one_task_out_global_choice(
    data: pd.DataFrame,
    *,
    task_col: str = "task_family",
    metric_col: str = "metric",
    utility_col: str = "utility",
) -> pd.DataFrame:
    """Choose the best mean-utility metric without using the held-out task."""
    validate_utility_table(
        data,
        task_col=task_col,
        metric_col=metric_col,
        utility_col=utility_col,
    )
    rows = []
    for task in sorted(data[task_col].unique(), key=str):
        eligible = set(data.loc[data[task_col] == task, metric_col])
        training = data.loc[
            (data[task_col] != task) & data[metric_col].isin(eligible)
        ]
        means = training.groupby(metric_col, sort=True)[utility_col].mean()
        if means.empty:
            rows.append(
                {
                    task_col: task,
                    "recommended_metric": None,
                    "selector_score": np.nan,
                    "abstention_reason": "no_transfer_evidence",
                }
            )
            continue
        best_score = float(means.max())
        best_metric = sorted(means.index[means == best_score], key=str)[0]
        rows.append(
            {
                task_col: task,
                "recommended_metric": best_metric,
                "selector_score": best_score,
                "abstention_reason": "",
            }
        )
    return pd.DataFrame(rows)


def score_recommendations(
    utilities: pd.DataFrame,
    recommendations: pd.DataFrame,
    *,
    task_col: str = "task_family",
    metric_col: str = "metric",
    utility_col: str = "utility",
    recommendation_col: str = "recommended_metric",
    abstention_utility: float = 0.0,
) -> pd.DataFrame:
    """Score recommendations against each task's oracle and abstention option."""
    validate_utility_table(
        utilities,
        task_col=task_col,
        metric_col=metric_col,
        utility_col=utility_col,
    )
    required = {task_col, recommendation_col}
    missing = required.difference(recommendations.columns)
    if missing:
        raise ValueError(f"missing recommendation columns: {sorted(missing)}")
    if recommendations.duplicated(task_col).any():
        raise ValueError("recommendations must contain at most one row per task")

    tasks = set(utilities[task_col])
    if set(recommendations[task_col]) != tasks:
        raise ValueError("recommendations must contain exactly the utility-table tasks")

    oracle = (
        utilities.groupby(task_col, sort=False)[utility_col]
        .max()
        .rename("oracle_utility")
    )
    lookup = utilities.rename(
        columns={metric_col: recommendation_col, utility_col: "selected_utility"}
    )[[task_col, recommendation_col, "selected_utility"]]
    scored = recommendations.merge(oracle, on=task_col, validate="one_to_one")
    scored = scored.merge(
        lookup,
        on=[task_col, recommendation_col],
        how="left",
        validate="one_to_one",
    )
    scored["covered"] = scored[recommendation_col].notna()
    invalid = scored["covered"] & scored["selected_utility"].isna()
    if invalid.any():
        bad = scored.loc[invalid, [task_col, recommendation_col]].to_dict("records")
        raise ValueError(f"recommended metric is unavailable for its task: {bad}")
    scored["decision_utility"] = scored["selected_utility"].fillna(
        float(abstention_utility)
    )
    scored["regret"] = scored["oracle_utility"] - scored["decision_utility"]
    return scored


def coverage_regret_curve(
    scored: pd.DataFrame,
    *,
    confidence_col: str = "selector_confidence",
    abstention_utility: float = 0.0,
    max_points: Optional[int] = None,
) -> pd.DataFrame:
    """Evaluate confidence-ranked recommendations with lower-coverage abstention."""
    required = {"oracle_utility", "selected_utility", confidence_col}
    missing = required.difference(scored.columns)
    if missing:
        raise ValueError(f"missing scored columns: {sorted(missing)}")
    values = scored[list(required)].apply(pd.to_numeric, errors="coerce")
    if not np.isfinite(values.to_numpy()).all():
        raise ValueError("coverage-regret inputs must be finite")
    ordered = scored.sort_values(confidence_col, ascending=False).reset_index(drop=True)
    n_tasks = len(ordered)
    if n_tasks == 0:
        raise ValueError("scored recommendation table is empty")
    coverage_counts = np.arange(1, n_tasks + 1)
    if max_points is not None and max_points > 0 and n_tasks > max_points:
        coverage_counts = np.unique(
            np.linspace(1, n_tasks, max_points, dtype=int)
        )

    rows = []
    for covered_count in coverage_counts:
        covered = ordered.iloc[:covered_count]
        abstained = ordered.iloc[covered_count:]
        covered_regret = covered["oracle_utility"] - covered["selected_utility"]
        abstained_regret = abstained["oracle_utility"] - float(abstention_utility)
        system_regret = pd.concat([covered_regret, abstained_regret])
        rows.append(
            {
                "covered_tasks": int(covered_count),
                "total_tasks": n_tasks,
                "coverage": covered_count / n_tasks,
                "confidence_threshold": float(covered[confidence_col].iloc[-1]),
                "covered_mean_regret": float(covered_regret.mean()),
                "system_mean_regret": float(system_regret.mean()),
            }
        )
    return pd.DataFrame(rows)
