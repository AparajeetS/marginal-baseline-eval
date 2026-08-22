from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from mbe_eval.comparators import (
    gcm_rank_test,
    granulated_kendall,
    jiang_normalized_cmi,
    wgcm_est_rank_test,
)


def factorial_frame(repeats: int = 2) -> pd.DataFrame:
    rows = []
    for a in range(3):
        for b in range(3):
            for repeat in range(repeats):
                rows.append(
                    {
                        "config": f"{a}-{b}",
                        "a": a,
                        "b": b,
                        "target": 2 * a + b + repeat * 0.01,
                        "metric": 2 * a + b + repeat * 0.01,
                    }
                )
    return pd.DataFrame(rows)


def test_granulated_kendall_recovers_consistent_factorial_ordering() -> None:
    score, detail = granulated_kendall(
        factorial_frame(), "metric", "target", ["a", "b"], group_col="config"
    )
    assert score == pytest.approx(1.0)
    assert (detail["finite_cells"] == 3).all()


def test_jiang_cmi_is_high_for_identical_pairwise_ordering() -> None:
    score, detail = jiang_normalized_cmi(
        factorial_frame(), "metric", "target", ["a", "b"], group_col="config"
    )
    assert score == pytest.approx(1.0)
    assert set(detail["conditioning_size"]) == {0, 1, 2}


def test_comparators_reject_inconsistent_group_hyperparameters() -> None:
    frame = factorial_frame()
    frame.loc[1, "a"] = 99
    with pytest.raises(ValueError, match="fixed hyperparameters"):
        granulated_kendall(frame, "metric", "target", ["a", "b"], group_col="config")


def test_jiang_cmi_null_is_small_in_balanced_factorial() -> None:
    frame = factorial_frame(repeats=1)
    frame["metric"] = np.tile([0.0, 1.0, 2.0], 3)
    frame["target"] = np.repeat([0.0, 1.0, 2.0], 3)
    score, _ = jiang_normalized_cmi(frame, "metric", "target", ["a", "b"])
    assert score < 0.05


def _frame(seed: int, signal: float) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    n = 240
    z = rng.normal(size=n)
    latent = rng.normal(size=n)
    metric = np.sin(z) + latent + rng.normal(scale=0.4, size=n)
    target = np.square(z) + signal * latent + rng.normal(scale=0.4, size=n)
    return pd.DataFrame(
        {"group": [f"g{i}" for i in range(n)], "z": z, "metric": metric, "target": target}
    )


def test_gcm_rank_test_detects_strong_increment() -> None:
    result = gcm_rank_test(
        _frame(7, 1.0), "metric", "target", ["z"], group_col="group", seed=11
    )
    assert result["n_groups"] == 240
    assert result["score_mean"] > 0
    assert result["p_value"] < 0.01


def test_wgcm_est_is_deterministic_and_split_safe() -> None:
    frame = _frame(9, 0.8)
    first = wgcm_est_rank_test(
        frame, "metric", "target", ["z"], group_col="group", seed=13
    )
    second = wgcm_est_rank_test(
        frame, "metric", "target", ["z"], group_col="group", seed=13
    )
    assert first == second
    assert first["weight_groups"] == 72
    assert first["n_groups"] == 168
    assert np.isfinite(first["p_value"])
