import json

import pandas as pd
import pytest

from mbe_eval.claim_card import (
    EVIDENCE_STATES,
    ESTIMAND_STATES,
    audit_benchmark_claim,
    claim_card_json,
    claim_card_markdown,
)
from mbe_eval.claim_demo import make_claim_demo


def _audit(frame, **overrides):
    kwargs = {
        "claim_id": "fixture-claim",
        "claim_text": "The candidate adds held-out signal in the named fixture.",
        "metric": "benchmark_score",
        "target": "external_outcome",
        "baselines": ["capability_proxy"],
        "environment": "environment",
        "unit": "model_id",
        "deceptive_control": "deceptive_score",
        "negative_controls": ["random_score"],
        "min_relative_mse_improvement": 0.01,
        "min_transport_relative_mse_improvement": 0.005,
        "permutations": 9,
        "bootstrap": 49,
        "seed": 20260715,
    }
    kwargs.update(overrides)
    return audit_benchmark_claim(frame, **kwargs)


def test_claim_card_separates_candidate_from_deceptive_and_negative_controls():
    card = _audit(make_claim_demo(n_units=32))

    assert card["method_status"] == "experimental"
    assert card["independently_validated"] is False
    assert card["evidence_state"] in EVIDENCE_STATES
    assert "claim_status" not in card
    assert card["evidence"]["E0"]["raw_rank_correlation"] > 0.9
    assert card["evidence"]["E1"]["result"]["relative_mse_improvement"] > 0.8
    assert card["evidence"]["E2"]["result"]["relative_mse_improvement"] > 0.8
    assert (
        card["control_results"]["deceptive_score"]["evidence"]["E0"]
        ["descriptive_classification"]
        == "washout"
    )
    assert (
        card["control_results"]["deceptive_score"]["evidence"]["E2"]["state"]
        != "meets-declared-threshold"
    )
    assert card["evidence"]["E3"]["state"] == "unresolved"
    assert card["evidence"]["E4"]["state"] == "unresolved"
    assert {
        card["evidence"][key]["state"] for key in ("E0", "E1", "E2", "E3", "E4")
    } <= ESTIMAND_STATES


def test_no_predeclared_thresholds_forces_inconclusive_status():
    card = _audit(
        make_claim_demo(n_units=24),
        deceptive_control=None,
        negative_controls=(),
        min_relative_mse_improvement=None,
        min_transport_relative_mse_improvement=None,
        permutations=0,
        bootstrap=0,
    )

    assert card["evidence_state"] == "unresolved-under-declared-tests"
    assert "No positive practical thresholds" in card["interpretation"]


def test_claim_card_json_is_deterministic_and_has_no_nonstandard_nan():
    card = _audit(
        make_claim_demo(n_units=24),
        deceptive_control=None,
        negative_controls=(),
        min_relative_mse_improvement=None,
        min_transport_relative_mse_improvement=None,
        permutations=0,
        bootstrap=0,
    )

    first = claim_card_json(card)
    second = claim_card_json(card)
    parsed = json.loads(first)

    assert first == second
    assert "NaN" not in first
    assert "Infinity" not in first
    assert parsed["schema_version"] == "mbe-benchmark-claim-card/0.2"
    assert "claim_status" not in parsed
    markdown = claim_card_markdown(card)
    assert "Not independently validated" in markdown
    assert "not certification" in markdown
    assert "Predeclared test outcome" in markdown


def test_claim_card_strictly_rejects_missing_columns_and_direct_target_leakage():
    frame = make_claim_demo(n_units=24)
    with pytest.raises(ValueError, match="missing required columns"):
        _audit(frame.drop(columns=["capability_proxy"]))

    leaked = frame.copy()
    leaked["benchmark_score"] = leaked["external_outcome"]
    with pytest.raises(ValueError, match="leakage guard"):
        _audit(leaked)


def test_claim_card_rejects_nonnumeric_candidate_and_too_few_environments():
    frame = make_claim_demo(n_units=24)
    nonnumeric = frame.copy()
    nonnumeric["benchmark_score"] = "text"
    with pytest.raises(ValueError, match="must be numeric"):
        _audit(nonnumeric)

    two_environments = frame[frame["environment"].isin(frame["environment"].unique()[:2])]
    with pytest.raises(ValueError, match="at least three environments"):
        _audit(two_environments)
