import numpy as np
import pandas as pd
import pytest

from mbe_eval import (
    classify_increment_evidence,
    cross_fitted_audit,
    repeated_cross_fitted_audit,
    run_calibration,
    run_monte_carlo_calibration,
)
from mbe_eval.crossfit import _fold_ids, _rank_train_test


def test_cross_fitted_audit_detects_incremental_signal():
    rng = np.random.default_rng(7)
    n = 300
    baseline = rng.normal(size=n)
    metric = rng.normal(size=n)
    target = baseline + metric + rng.normal(0, 0.3, n)
    df = pd.DataFrame(
        {
            "config_id": [f"cfg_{i // 3}" for i in range(n)],
            "baseline": baseline,
            "metric": metric,
            "target": target,
        }
    )

    result = cross_fitted_audit(
        df,
        "metric",
        "target",
        ["baseline"],
        group_col="config_id",
        degree=4,
        permutations=19,
        seed=7,
    )

    assert result["n"] == n
    assert result["residual_r"] > 0.7
    assert result["delta_mse"] > 0.02
    assert result["residual_p"] <= 0.05


def test_frozen_calibration_profiles_pass():
    ledger, summary = run_calibration(n=300, seed=2026, permutations=9)

    assert len(ledger) == 2400
    assert len(summary) == 8
    assert bool(summary["calibration_pass"].all())

    nonlinear = summary.set_index("scenario").loc["nonlinear_proxy"]
    assert abs(nonlinear["partial_r"]) > 0.8
    assert abs(nonlinear["crossfit_residual_r"]) < 0.15


def test_rank_transform_is_fitted_on_training_values_only():
    train = np.array([1.0, 2.0, 3.0, 4.0])
    test = np.array([-100.0, 2.0, 100.0])
    train_rank, test_rank = _rank_train_test(train, test)
    changed_train_rank, _ = _rank_train_test(train, test * 1_000_000)

    assert train_rank.tolist() == pytest.approx([0.25, 0.5, 0.75, 1.0])
    assert test_rank.tolist() == pytest.approx([0.25, 0.5, 1.0])
    assert changed_train_rank.tolist() == pytest.approx(train_rank)


def test_grouped_folds_never_split_a_configuration():
    frame = pd.DataFrame(
        {
            "config_id": np.repeat(["a", "b", "c", "d"], 5),
            "value": np.arange(20),
        }
    )
    folds = _fold_ids(frame, n_splits=3, seed=9, group_col="config_id")
    assignments = pd.DataFrame({"config_id": frame.config_id, "fold": folds})

    assert assignments.groupby("config_id")["fold"].nunique().eq(1).all()


def test_extra_trees_nuisance_model_detects_incremental_signal():
    rng = np.random.default_rng(17)
    n = 150
    baseline_a = rng.uniform(-2.0, 2.0, n)
    baseline_b = rng.uniform(-2.0, 2.0, n)
    metric = rng.normal(size=n)
    target = baseline_a * baseline_b + metric + rng.normal(0, 0.25, n)
    result = cross_fitted_audit(
        pd.DataFrame(
            {
                "baseline_a": baseline_a,
                "baseline_b": baseline_b,
                "metric": metric,
                "target": target,
            }
        ),
        "metric",
        "target",
        ["baseline_a", "baseline_b"],
        nuisance_model="extra_trees",
        permutations=19,
        seed=17,
    )

    assert result["nuisance_model"] == "extra_trees"
    assert result["delta_mse"] > 0.0


@pytest.mark.parametrize(
    ("residual_p", "delta_low", "expected"),
    [
        (0.01, 0.002, "increment-supported"),
        (0.01, -0.001, "residual-dependence-only"),
        (0.20, 0.002, "predictive-improvement-only"),
        (0.20, -0.001, "no-supported-increment"),
    ],
)
def test_increment_evidence_keeps_estimands_separate(
    residual_p, delta_low, expected
):
    assert classify_increment_evidence(residual_p, delta_low) == expected


def test_repeated_crossfit_reports_fold_assignment_sensitivity():
    rng = np.random.default_rng(29)
    n = 120
    baseline = rng.normal(size=n)
    metric = rng.normal(size=n)
    frame = pd.DataFrame(
        {
            "baseline": baseline,
            "metric": metric,
            "target": baseline + metric + rng.normal(0, 0.35, n),
        }
    )
    sensitivity = repeated_cross_fitted_audit(
        frame,
        "metric",
        "target",
        ["baseline"],
        repeats=3,
        seed=29,
        permutations=9,
        bootstrap=19,
        degree=4,
    )

    assert sensitivity["split_seed"].nunique() == 3
    assert len(sensitivity) == 3
    assert (sensitivity["delta_mse"] > 0).all()


def test_monte_carlo_calibration_reports_error_and_power_rates():
    ledger, summary = run_monte_carlo_calibration(
        sample_sizes=(100,),
        degrees=(2,),
        repetitions=20,
        permutations=19,
        bootstrap=19,
        seed=123,
    )

    assert len(ledger) == 8 * 20
    assert len(summary) == 8
    assert set(summary["expected_signal"]) == {False, True}
    assert summary["crossfit_residual_reject_rate"].between(0.0, 1.0).all()
    assert summary["joint_increment_decision_rate"].between(0.0, 1.0).all()
