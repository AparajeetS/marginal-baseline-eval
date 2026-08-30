import numpy as np
import pandas as pd
import pytest

from mbe_eval import run_published_reaudit, validate_study_manifest


def _study_frame(seed=12, n=160):
    rng = np.random.default_rng(seed)
    dataset = np.where(np.arange(n) % 2 == 0, "image_a", "image_b")
    baseline = rng.normal(size=n) + 0.4 * (dataset == "image_b")
    metric = rng.normal(size=n)
    target = baseline + 0.8 * metric + rng.normal(0, 0.4, n)
    return pd.DataFrame(
        {
            "run_id": [f"run_{i:04d}" for i in range(n)],
            "config_id": [f"cfg_{i // 4:03d}" for i in range(n)],
            "dataset": dataset,
            "baseline": baseline,
            "candidate_metric": metric,
            "target": target,
        }
    )


def _manifest():
    return {
        "schema_version": 1,
        "study_id": "example-2026",
        "title": "Example metric study",
        "citation_url": "https://example.org/paper",
        "data_path": "study.csv",
        "row_id": "run_id",
        "target": "target",
        "metrics": ["candidate_metric"],
        "baseline_ladder": [
            {"level": "B1", "controls": ["dataset", "baseline"], "polynomial_degree": 4}
        ],
        "group_column": "config_id",
        "environment_columns": ["dataset"],
    }


def test_manifest_reaudit_runs_pooled_and_environment_scopes():
    report = run_published_reaudit(
        _study_frame(),
        _manifest(),
        permutations=9,
        bootstrap=19,
        minimum_scope_rows=30,
    )

    assert set(report["scope"]) == {"pooled", "dataset=image_a", "dataset=image_b"}
    assert (report["crossfit_residual_r"] > 0.6).all()
    assert (report["delta_mse"] > 0.01).all()
    assert report["crossfit_residual_ci_low"].notna().all()
    assert report["delta_mse_ci_high"].notna().all()
    assert report["crossfit_permutation_q"].between(0, 1).all()


def test_manifest_validation_rejects_duplicate_run_ids():
    df = _study_frame()
    df.loc[1, "run_id"] = df.loc[0, "run_id"]

    with pytest.raises(ValueError, match="duplicates"):
        validate_study_manifest(_manifest(), df)


def test_environment_scope_with_one_group_abstains_instead_of_using_rows():
    frame = _study_frame(n=80)
    frame["dataset"] = np.where(frame.index < 40, "image_a", "image_b")
    frame["config_id"] = np.where(frame.index < 40, "cfg_a", "cfg_b")
    report = run_published_reaudit(
        frame,
        _manifest(),
        permutations=9,
        bootstrap=9,
        minimum_scope_rows=30,
    )
    scoped = report.loc[report["scope"].ne("pooled")]
    assert scoped["independence_units"].eq(1).all()
    assert scoped["estimation_status"].str.startswith("not-estimable").all()
    assert scoped["increment_classification"].eq("not-estimable").all()
    assert scoped["crossfit_permutation_p"].isna().all()
