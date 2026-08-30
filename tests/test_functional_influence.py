import numpy as np
import pytest

from mbe_eval.functional_influence import (
    FunctionalInfluenceInputError,
    bootstrap_functional_influence,
    functional_influence_spectrum,
)


def _known_mechanism(seed: int = 0):
    rng = np.random.default_rng(seed)
    activations = rng.normal(size=(400, 6))
    jacobians = np.zeros((400, 2, 6))
    jacobians[:, 0, 0] = 3.0
    jacobians[:, 0, 1] = 1.0
    jacobians[:, 1, 0] = -3.0
    jacobians[:, 1, 1] = -1.0
    probabilities = np.full((400, 2), 0.5)
    return activations, jacobians, probabilities


def test_known_mechanism_finds_functionally_active_subspace() -> None:
    activations, jacobians, probabilities = _known_mechanism()
    result = functional_influence_spectrum(
        activations, jacobians, probabilities=probabilities
    )
    assert result["activation_rank"] == 6
    assert result["active_rank"] == 1
    assert result["inactive_activation_dimensions"] == 5
    assert result["effective_dimension"] == pytest.approx(1.0)
    assert result["top_1_share"] == pytest.approx(1.0)


def test_spectrum_is_invariant_to_invertible_hidden_reparameterization() -> None:
    activations, jacobians, probabilities = _known_mechanism(7)
    transform = np.array(
        [
            [2.0, 0.4, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.7, 0.2, 0.0, 0.0, 0.0],
            [0.0, 0.0, 1.4, 0.3, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.8, 0.2, 0.0],
            [0.0, 0.0, 0.0, 0.0, 1.2, 0.1],
            [0.1, 0.0, 0.0, 0.0, 0.0, 0.9],
        ]
    )
    transformed_activations = activations @ transform.T
    transformed_jacobians = jacobians @ np.linalg.inv(transform)
    original = functional_influence_spectrum(
        activations, jacobians, probabilities=probabilities
    )
    transformed = functional_influence_spectrum(
        transformed_activations,
        transformed_jacobians,
        probabilities=probabilities,
    )
    np.testing.assert_allclose(
        original["spectrum"], transformed["spectrum"], rtol=1e-10, atol=1e-10
    )
    assert transformed["functional_mass"] == pytest.approx(
        original["functional_mass"], rel=1e-10
    )
    assert transformed["effective_dimension"] == pytest.approx(
        original["effective_dimension"], rel=1e-10
    )


def test_metric_distinguishes_variance_from_functional_influence() -> None:
    rng = np.random.default_rng(11)
    activations = rng.normal(size=(500, 4))
    activations[:, 3] *= 100.0
    jacobians = np.zeros((500, 1, 4))
    jacobians[:, 0, 0] = 1.0
    result = functional_influence_spectrum(activations, jacobians)
    assert result["active_rank"] == 1
    assert result["top_1_share"] == pytest.approx(1.0)
    assert result["inactive_activation_dimensions"] == 3


def test_active_rank_is_invariant_to_global_jacobian_scale() -> None:
    activations, jacobians, probabilities = _known_mechanism(17)
    original = functional_influence_spectrum(
        activations, jacobians, probabilities=probabilities
    )
    rescaled = functional_influence_spectrum(
        activations, jacobians * 1e-8, probabilities=probabilities
    )
    assert rescaled["active_rank"] == original["active_rank"] == 1
    np.testing.assert_allclose(
        rescaled["normalized_spectrum"],
        original["normalized_spectrum"],
        rtol=1e-10,
        atol=1e-10,
    )


def test_bootstrap_reports_paired_uncertainty() -> None:
    activations, jacobians, probabilities = _known_mechanism(13)
    result = bootstrap_functional_influence(
        activations,
        jacobians,
        probabilities=probabilities,
        draws=20,
        seed=4,
    )
    assert result["bootstrap"]["draws"] == 20
    interval = result["bootstrap"]["intervals"]["functional_mass"]
    assert interval["low"] <= interval["high"]


def test_rejects_malformed_probabilities() -> None:
    activations, jacobians, probabilities = _known_mechanism()
    probabilities[0] = [0.8, 0.8]
    with pytest.raises(FunctionalInfluenceInputError, match="sum to one"):
        functional_influence_spectrum(
            activations, jacobians, probabilities=probabilities
        )
