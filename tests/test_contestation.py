import pytest

from mbe_eval import compare_benchmark_claim_specs
from mbe_eval.claim_demo import make_claim_demo


def _common():
    return {
        "claim_id": "contested-synthetic-claim",
        "claim_text": "The candidate adds held-out signal under the declared tests.",
        "metric": "benchmark_score",
        "target": "external_outcome",
        "baselines": ["capability_proxy"],
        "environment": "environment",
        "unit": "model_id",
        "n_splits": 4,
        "permutations": 0,
        "bootstrap": 39,
        "seed": 17,
    }


def test_compare_specs_exposes_conclusion_change_and_complete_cards():
    bundle = compare_benchmark_claim_specs(
        make_claim_demo(n_units=24),
        {
            "declared-practical-floor": {
                "min_relative_mse_improvement": 0.001,
                "min_transport_relative_mse_improvement": 0.001,
            },
            "stress-test-floor": {
                "min_relative_mse_improvement": 10.0,
                "min_transport_relative_mse_improvement": 10.0,
            },
        },
        common=_common(),
    )

    assert bundle["reference_specification"] == "declared-practical-floor"
    assert bundle["conclusion_changed"] is True
    assert bundle["overall_evidence_state_changed"] is True
    assert bundle["changed_specifications"] == ["stress-test-floor"]
    assert set(bundle["claim_cards"]) == {
        "declared-practical-floor",
        "stress-test-floor",
    }
    assert all(
        "claim_status" not in card for card in bundle["claim_cards"].values()
    )


def test_compare_specs_rejects_a_single_or_unnamed_specification():
    frame = make_claim_demo(n_units=20)
    with pytest.raises(ValueError, match="at least two"):
        compare_benchmark_claim_specs(frame, {"only": {}}, common=_common())

    with pytest.raises(ValueError, match="non-empty"):
        compare_benchmark_claim_specs(
            frame,
            {"reference": {}, "   ": {}},
            common=_common(),
        )
