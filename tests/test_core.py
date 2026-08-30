import numpy as np
import pandas as pd
import pytest

from mbe_eval import (
    __version__,
    MBEEvaluator,
    MBEInputError,
    audit_csv,
    audit_metric,
    audit_metrics,
    audit_report_markdown,
    make_demo_runs,
    partial_rank_corr,
    run_demo,
    summarize_audit,
)


def test_public_version_matches_release():
    assert __version__ == "0.5.0"


def synthetic_frame(seed=0, n=300):
    rng = np.random.default_rng(seed)
    learning_rate = rng.choice([1e-4, 3e-4, 1e-3, 3e-3], size=n)
    weight_decay = rng.choice([0.0, 1e-5, 1e-4], size=n)
    architecture = rng.choice(["cnn", "resnet"], size=n)
    baseline = -np.log10(learning_rate) + 0.2 * (architecture == "cnn") + rng.normal(0, 0.05, n)
    target = -baseline + rng.normal(0, 0.08, n)
    proxy_metric = baseline + rng.normal(0, 0.05, n)
    residual_metric = target - 0.3 * baseline + rng.normal(0, 0.05, n)
    return pd.DataFrame(
        {
            "proxy_metric": proxy_metric,
            "residual_metric": residual_metric,
            "baseline": baseline,
            "learning_rate": learning_rate,
            "weight_decay": weight_decay,
            "architecture": architecture,
            "target": target,
        }
    )


def test_audit_metrics_shows_proxy_signal_collapses_after_controls():
    df = synthetic_frame()
    report = audit_metrics(
        df,
        metrics=["proxy_metric", "residual_metric"],
        target="target",
        controls=["baseline", "learning_rate", "weight_decay", "architecture"],
    )
    by_metric = report.set_index("metric")

    assert abs(by_metric.loc["proxy_metric", "raw_r"]) > 0.6
    assert abs(by_metric.loc["proxy_metric", "partial_r"]) < 0.2
    assert by_metric.loc["proxy_metric", "partial_p"] > 0.05
    assert by_metric.loc["residual_metric", "classification"] in {
        "survives",
        "hidden-after-control",
    }


def test_partial_rank_corr_accepts_categorical_controls():
    df = synthetic_frame()
    r, p, n = partial_rank_corr(
        df,
        metric="proxy_metric",
        target="target",
        controls=["baseline", "architecture"],
    )

    assert n == len(df)
    assert np.isfinite(r)
    assert np.isfinite(p)


def test_backward_compatible_evaluator():
    df = synthetic_frame()
    evaluator = MBEEvaluator(metric_name="proxy", baseline_name="baseline")
    report = evaluator.evaluate(
        df["proxy_metric"].to_numpy(),
        df["baseline"].to_numpy(),
        df["target"].to_numpy(),
    )

    assert report.metric_name == "proxy"
    assert report.baseline_name == "baseline"
    assert np.isfinite(report.absolute_r)
    assert np.isfinite(report.partial_r)
    assert report.is_confounded is True


def test_evaluator_does_not_call_every_null_result_confounded():
    rng = np.random.default_rng(12)
    evaluator = MBEEvaluator(metric_name="noise", baseline_name="baseline")
    report = evaluator.evaluate(
        rng.normal(size=300),
        rng.normal(size=300),
        rng.normal(size=300),
    )
    assert report.classification == "weak-or-mixed"
    assert report.is_confounded is False


def test_declared_inference_units_drive_cluster_bootstrap():
    frame = synthetic_frame(n=80)
    frame["config_id"] = np.repeat(np.arange(20), 4)
    row = audit_metric(
        frame,
        metric="proxy_metric",
        target="target",
        controls=["baseline"],
        inference_unit_col="config_id",
        bootstrap=19,
        seed=4,
    )
    assert row["independence_units"] == 20
    assert row["bootstrap_unit"] == "config_id"
    assert np.isnan(row["raw_p"])
    assert np.isnan(row["partial_p"])
    assert np.isfinite(row["partial_ci_low"])


def test_declared_inference_unit_fails_closed_with_one_unit():
    frame = synthetic_frame(n=40)
    frame["config_id"] = "only-unit"
    with pytest.raises(MBEInputError, match="at least two units"):
        audit_metric(
            frame,
            metric="proxy_metric",
            target="target",
            controls=["baseline"],
            inference_unit_col="config_id",
            bootstrap=9,
        )


def test_audit_metric_ignores_metric_when_it_is_also_a_control():
    df = synthetic_frame()
    row = audit_metric(
        df,
        metric="baseline",
        target="target",
        controls=["baseline", "learning_rate", "architecture"],
    )

    assert row["metric"] == "baseline"
    assert np.isfinite(row["raw_r"])
    assert np.isfinite(row["partial_r"])


def test_reporting_helpers_create_markdown():
    df = synthetic_frame()
    report = audit_metrics(
        df,
        metrics=["proxy_metric", "residual_metric"],
        target="target",
        controls=["baseline", "learning_rate", "architecture"],
    )
    summary = summarize_audit(report)
    markdown = audit_report_markdown(report, target="target", controls=["baseline"])

    assert list(summary.columns) == [
        "metric",
        "n",
        "raw_r",
        "partial_r",
        "delta_partial_minus_raw",
        "classification",
    ]
    assert "# MBE Audit Report" in markdown
    assert "| `proxy_metric` |" in markdown


def test_demo_runs_end_to_end_without_writing(tmp_path):
    df = make_demo_runs(n=40, seed=1)
    report = run_demo(n=40, seed=1, bootstrap=0, output=None)

    assert len(df) == 40
    assert set(report["metric"]) == {
        "reported_gain",
        "validation_gain",
        "train_gain",
        "parameter_delta",
        "random_metric",
    }
    assert not (tmp_path / "mbe_demo_report.md").exists()


def test_csv_cli_helper_audits_training_ledger(tmp_path):
    csv_path = tmp_path / "runs.csv"
    out_path = tmp_path / "report.md"
    synthetic_frame(n=80).to_csv(csv_path, index=False)

    report = audit_csv(
        csv_path,
        metrics=["proxy_metric", "residual_metric"],
        target="target",
        controls=["baseline", "learning_rate", "architecture"],
        output=out_path,
    )

    assert set(report["metric"]) == {"proxy_metric", "residual_metric"}
    assert out_path.exists()
    assert "MBE CSV Audit Report" in out_path.read_text(encoding="utf-8")


def test_audit_fails_closed_on_unknown_columns():
    df = synthetic_frame(n=40)

    with pytest.raises(MBEInputError, match="unknown ledger column"):
        audit_metrics(
            df,
            metrics=["proxy_mteric"],
            target="target",
            controls=["baseline"],
        )

    with pytest.raises(MBEInputError, match="unknown ledger column"):
        audit_metric(
            df,
            metric="proxy_metric",
            target="target",
            controls=["basline"],
        )


def test_csv_helper_writes_machine_readable_results(tmp_path):
    csv_path = tmp_path / "runs.csv"
    json_path = tmp_path / "audit.json"
    synthetic_frame(n=80).to_csv(csv_path, index=False)

    report = audit_csv(
        csv_path,
        metrics=["proxy_metric"],
        target="target",
        controls=["baseline"],
        seed=42,
        results=json_path,
    )

    assert len(report) == 1
    assert '"metric":"proxy_metric"' in json_path.read_text(encoding="utf-8")
