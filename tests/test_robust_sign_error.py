import numpy as np
import pandas as pd

from mbe_eval.robust_sign_error import (
    hoeffding_weight,
    robust_sign_error_environments,
    source_metric_columns,
    weighted_environment_loss,
)


def test_weighted_environment_matches_literal_source_loop():
    gap_a = np.array([0.10, 0.12, 0.09])
    gap_b = np.array([0.20, 0.18])
    metric_a = np.array([[1.0, 3.0], [1.2, 2.5], [0.9, 3.2]])
    metric_b = np.array([[2.0, 2.0], [1.8, 2.2]])
    losses, weight_sum, effective_sample_size = weighted_environment_loss(
        gap_a, gap_b, metric_a, metric_b
    )

    literal_weight = 0.0
    literal_squared_weight = 0.0
    literal_loss = np.zeros(2)
    for i, first_gap in enumerate(gap_a):
        for j, second_gap in enumerate(gap_b):
            weight = max(float(hoeffding_weight(abs(first_gap - second_gap))) - 0.5, 0.0)
            literal_weight += weight
            literal_squared_weight += weight * weight
            for metric in range(2):
                error = (
                    1
                    - np.sign(metric_a[i, metric] - metric_b[j, metric])
                    * np.sign(first_gap - second_gap)
                ) / 2
                literal_loss[metric] += error * weight

    np.testing.assert_allclose(losses, literal_loss / literal_weight)
    assert np.isclose(weight_sum, literal_weight)
    assert np.isclose(
        effective_sample_size, literal_weight**2 / literal_squared_weight
    )


def test_environment_builder_returns_both_source_directions():
    frame = pd.DataFrame(
        {
            "config_id": ["a", "a", "b", "b"],
            "hp.dataset": ["x", "x", "x", "x"],
            "hp.lr": [0.1, 0.1, 0.2, 0.2],
            "gen.gap": [0.1, 0.11, 0.3, 0.31],
            "complexity.metric": [1.0, 1.1, 2.0, 2.1],
        }
    )
    result = robust_sign_error_environments(
        frame,
        ["complexity.metric"],
        ["hp.dataset", "hp.lr"],
        minimum_effective_sample_size=0,
    )

    assert len(result) == 2
    assert set(result["source_config"]) == {"a", "b"}
    assert np.allclose(result["complexity.metric"], 0.0)


def test_fft_variant_preference_matches_source_figure_rule():
    columns = [
        "complexity.spec",
        "complexity.spec_fft",
        "complexity.margin",
        "target",
    ]
    assert source_metric_columns(columns) == [
        "complexity.spec_fft",
        "complexity.margin",
    ]


def test_environment_builder_uses_source_isclose_ess_boundary():
    frame = pd.DataFrame(
        {
            "config_id": ["a", "a", "b", "b"],
            "hp.lr": [0.1, 0.1, 0.2, 0.2],
            "gen.gap": [0.10, 0.11, 0.30, 0.31],
            "complexity.metric": [1.0, 1.1, 2.0, 2.1],
        }
    )
    unfiltered = robust_sign_error_environments(
        frame,
        ["complexity.metric"],
        ["hp.lr"],
        minimum_effective_sample_size=0,
    )
    ess = float(unfiltered["effective_sample_size"].iloc[0])
    result = robust_sign_error_environments(
        frame,
        ["complexity.metric"],
        ["hp.lr"],
        minimum_effective_sample_size=ess + 1e-6,
    )
    assert len(result) == 2
