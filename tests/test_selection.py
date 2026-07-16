import numpy as np
import pandas as pd
import pytest

from mbe_eval.selection import (
    coverage_regret_curve,
    leave_one_task_out_global_choice,
    score_recommendations,
    validate_utility_table,
)


def utility_table() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "task_family": ["a", "a", "b", "b", "c", "c"],
            "metric": ["x", "y", "x", "y", "x", "y"],
            "utility": [0.8, 0.2, 0.7, 0.3, 0.6, 0.4],
        }
    )


def test_global_choice_never_uses_held_out_task() -> None:
    choices = leave_one_task_out_global_choice(utility_table())
    assert choices["recommended_metric"].tolist() == ["x", "x", "x"]
    assert choices.loc[choices.task_family == "a", "selector_score"].item() == pytest.approx(0.65)


def test_score_recommendations_accounts_for_abstention() -> None:
    recommendations = pd.DataFrame(
        {
            "task_family": ["a", "b", "c"],
            "recommended_metric": ["x", None, "y"],
        }
    )
    scored = score_recommendations(
        utility_table(), recommendations, abstention_utility=0.1
    )
    assert scored["covered"].tolist() == [True, False, True]
    assert scored["regret"].tolist() == pytest.approx([0.0, 0.6, 0.2])


def test_coverage_regret_curve_uses_confidence_order() -> None:
    scored = pd.DataFrame(
        {
            "oracle_utility": [1.0, 1.0, 1.0],
            "selected_utility": [0.9, 0.2, 0.8],
            "selector_confidence": [0.9, 0.1, 0.7],
        }
    )
    curve = coverage_regret_curve(scored)
    assert curve["covered_tasks"].tolist() == [1, 2, 3]
    assert curve.loc[1, "covered_mean_regret"] == pytest.approx(0.15)
    assert curve.loc[2, "covered_mean_regret"] == pytest.approx((0.1 + 0.2 + 0.8) / 3)


def test_selector_validation_rejects_duplicate_task_metric_pairs() -> None:
    duplicated = pd.concat([utility_table(), utility_table().iloc[[0]]])
    with pytest.raises(ValueError, match="must be unique"):
        validate_utility_table(duplicated)


def test_single_task_global_choice_abstains() -> None:
    one_task = utility_table().query("task_family == 'a'")
    choice = leave_one_task_out_global_choice(one_task)
    assert choice["recommended_metric"].isna().all()
    assert np.isnan(choice["selector_score"].item())
