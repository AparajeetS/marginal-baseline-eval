import numpy as np
import pandas as pd
import pytest

from mbe_eval import orthogonal_score_audit, repeated_split_orthogonal_audit


def _signal_frame(seed: int = 7, groups: int = 100) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    n = groups * 2
    baseline = rng.normal(size=n)
    metric = rng.normal(size=n)
    target = baseline + 1.2 * metric + rng.normal(0, 0.25, n)
    return pd.DataFrame(
        {
            "config_id": np.repeat(np.arange(groups), 2),
            "environment": np.repeat(np.arange(groups) % 4, 2),
            "baseline": baseline,
            "metric": metric,
            "target": target,
        }
    )


def test_orthogonal_score_detects_strong_signal_deterministically() -> None:
    frame = _signal_frame()
    first = orthogonal_score_audit(
        frame,
        "metric",
        "target",
        ["baseline"],
        group_col="config_id",
        permutation_block_col="environment",
        wild_draws=199,
        seed=11,
    )
    second = orthogonal_score_audit(
        frame,
        "metric",
        "target",
        ["baseline"],
        group_col="config_id",
        permutation_block_col="environment",
        wild_draws=199,
        seed=11,
    )

    assert first == second
    assert first["n_groups"] == 100
    assert first["rows_per_group"] == 2
    assert first["n_blocks"] == 4
    assert first["score_aggregation"] == "product-of-group-mean-residuals"
    assert first["orthogonal_score_mean"] > 0
    assert 0 <= first["orthogonal_wild_p"] <= 1
    assert first["orthogonal_wild_p"] <= 0.05
    assert first["partial_rank_slope_ci_low"] > 0


def test_orthogonal_score_accepts_large_extra_trees_seed() -> None:
    result = orthogonal_score_audit(
        _signal_frame(groups=40),
        "metric",
        "target",
        ["baseline"],
        group_col="config_id",
        nuisance_model="extra_trees",
        wild_draws=19,
        seed=2**32 + 17,
    )
    assert result["nuisance_model"] == "extra_trees"
    assert np.isfinite(result["orthogonal_score_mean"])


def test_orthogonal_score_requires_balanced_groups() -> None:
    frame = _signal_frame(groups=20).iloc[:-1].copy()
    with pytest.raises(ValueError, match="balanced"):
        orthogonal_score_audit(
            frame,
            "metric",
            "target",
            ["baseline"],
            group_col="config_id",
            wild_draws=19,
        )


def test_orthogonal_score_requires_block_constant_within_group() -> None:
    frame = _signal_frame(groups=20)
    frame["environment"] = np.arange(len(frame)) % 2
    with pytest.raises(ValueError, match="one permutation block"):
        orthogonal_score_audit(
            frame,
            "metric",
            "target",
            ["baseline"],
            group_col="config_id",
            permutation_block_col="environment",
            wild_draws=19,
        )


def test_repeated_split_orthogonal_requires_stable_signal() -> None:
    first = repeated_split_orthogonal_audit(
        _signal_frame(groups=100),
        "metric",
        "target",
        ["baseline"],
        group_col="config_id",
        permutation_block_col="environment",
        repeats=3,
        wild_draws=199,
        seed=17,
    )
    second = repeated_split_orthogonal_audit(
        _signal_frame(groups=100),
        "metric",
        "target",
        ["baseline"],
        group_col="config_id",
        permutation_block_col="environment",
        repeats=3,
        wild_draws=199,
        seed=17,
    )

    assert first == second
    assert first["stability_repeats"] == 3
    assert first["positive_split_count"] == 3
    assert first["stable_positive"] is True
    assert first["stability_rule"] == "positive_wild_support_in_every_split"
