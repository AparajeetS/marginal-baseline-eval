import pandas as pd

from mbe_eval.diagnostics import abstention_reasons, minimum_detectable_correlation


def test_detectable_correlation_decreases_with_sample_size() -> None:
    assert minimum_detectable_correlation(200) < minimum_detectable_correlation(30)


def test_abstention_reports_model_disagreement_and_missing_refit() -> None:
    rows = pd.DataFrame(
        {
            "independence_units": [40, 40],
            "nuisance_model": ["a", "b"],
            "increment_classification": [
                "increment-supported",
                "no-supported-increment",
            ],
            "delta_mse_ci_low": [0.01, -0.01],
        }
    )
    reasons = abstention_reasons(rows, require_refit_interval=True)
    assert "nuisance-model-disagreement" in reasons
    assert "refit-aware-uncertainty-not-run" in reasons


def test_different_metrics_are_not_mislabeled_as_nuisance_disagreement() -> None:
    rows = pd.DataFrame(
        {
            "metric": ["metric_a", "metric_b"],
            "independence_units": [40, 40],
            "nuisance_model": ["ridge", "ridge"],
            "increment_classification": [
                "increment-supported",
                "no-supported-increment",
            ],
            "delta_mse_ci_low": [0.01, -0.01],
        }
    )
    reasons = abstention_reasons(rows)
    assert "nuisance-model-disagreement" not in reasons
    assert "nuisance-sensitivity-not-run" in reasons


def test_all_nan_refit_interval_is_reported_missing() -> None:
    rows = pd.DataFrame(
        {
            "independence_units": [40, 40],
            "nuisance_model": ["ridge", "trees"],
            "increment_classification": ["no-supported-increment"] * 2,
            "delta_mse_ci_low": [-0.01, -0.01],
            "refit_delta_mse_ci_low": [float("nan"), float("nan")],
        }
    )
    assert "refit-aware-uncertainty-not-run" in abstention_reasons(
        rows, require_refit_interval=True
    )
