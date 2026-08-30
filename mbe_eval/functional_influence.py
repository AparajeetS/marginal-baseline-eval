from __future__ import annotations

import math
from typing import Sequence

import numpy as np


class FunctionalInfluenceInputError(ValueError):
    """Raised when a functional-influence input is malformed."""


def _as_finite_array(name: str, values: np.ndarray, ndim: int) -> np.ndarray:
    array = np.asarray(values, dtype=np.float64)
    if array.ndim != ndim:
        raise FunctionalInfluenceInputError(
            f"{name} must have {ndim} dimensions; received shape {array.shape}"
        )
    if not np.isfinite(array).all():
        raise FunctionalInfluenceInputError(f"{name} contains non-finite values")
    return array


def _output_geometry(
    jacobians: np.ndarray,
    probabilities: np.ndarray | None,
    output_metric: np.ndarray | None,
) -> tuple[np.ndarray, str]:
    samples, outputs, _ = jacobians.shape
    if probabilities is not None and output_metric is not None:
        raise FunctionalInfluenceInputError(
            "provide probabilities or output_metric, not both"
        )
    if probabilities is not None:
        probabilities = _as_finite_array("probabilities", probabilities, 2)
        if probabilities.shape != (samples, outputs):
            raise FunctionalInfluenceInputError(
                "probabilities must match the first two Jacobian dimensions"
            )
        if (probabilities < 0).any():
            raise FunctionalInfluenceInputError("probabilities must be non-negative")
        row_sums = probabilities.sum(axis=1)
        if not np.allclose(row_sums, 1.0, rtol=1e-6, atol=1e-8):
            raise FunctionalInfluenceInputError("probability rows must sum to one")
        geometry = np.empty((samples, outputs, outputs), dtype=np.float64)
        for index, probability in enumerate(probabilities):
            geometry[index] = np.diag(probability) - np.outer(probability, probability)
        return geometry, "categorical_fisher"
    if output_metric is None:
        return np.broadcast_to(np.eye(outputs), (samples, outputs, outputs)), "euclidean"
    output_metric = _as_finite_array("output_metric", output_metric, 3)
    if output_metric.shape != (samples, outputs, outputs):
        raise FunctionalInfluenceInputError(
            "output_metric must have shape (samples, outputs, outputs)"
        )
    if not np.allclose(output_metric, output_metric.transpose(0, 2, 1), atol=1e-10):
        raise FunctionalInfluenceInputError("output_metric must be symmetric")
    minimum = min(float(np.linalg.eigvalsh(matrix).min()) for matrix in output_metric)
    if minimum < -1e-10:
        raise FunctionalInfluenceInputError("output_metric must be positive semidefinite")
    return output_metric, "custom"


def functional_influence_spectrum(
    activations: np.ndarray,
    output_jacobians: np.ndarray,
    *,
    probabilities: np.ndarray | None = None,
    output_metric: np.ndarray | None = None,
    top_k: Sequence[int] = (1, 3, 5, 10),
    relative_tolerance: float | None = None,
) -> dict[str, object]:
    """Summarize naturally varying hidden directions that affect model output.

    ``activations`` has shape ``(samples, hidden_dimensions)`` and
    ``output_jacobians`` has shape
    ``(samples, output_dimensions, hidden_dimensions)``. The method forms the
    activation covariance ``C`` and downstream sensitivity geometry ``G``.
    The eigenvalues of ``C G`` are reported through the symmetric equivalent
    ``C**(1/2) G C**(1/2)``.

    The spectrum is invariant to invertible linear reparameterizations of the
    hidden coordinates when activations and downstream Jacobians are transformed
    consistently. It describes local functional influence on the supplied
    sample distribution; it is not a semantic or causal-abstraction certificate.
    """
    activations = _as_finite_array("activations", activations, 2)
    jacobians = _as_finite_array("output_jacobians", output_jacobians, 3)
    samples, hidden_dimensions = activations.shape
    if samples < 2:
        raise FunctionalInfluenceInputError("at least two activation samples are required")
    if jacobians.shape[0] != samples or jacobians.shape[2] != hidden_dimensions:
        raise FunctionalInfluenceInputError(
            "output_jacobians must match activation samples and hidden dimensions"
        )
    if hidden_dimensions < 1 or jacobians.shape[1] < 1:
        raise FunctionalInfluenceInputError("hidden and output dimensions must be positive")
    if relative_tolerance is not None and relative_tolerance < 0:
        raise FunctionalInfluenceInputError("relative_tolerance must be non-negative")

    geometry, geometry_name = _output_geometry(jacobians, probabilities, output_metric)
    centered = activations - activations.mean(axis=0, keepdims=True)
    covariance = centered.T @ centered / (samples - 1)
    weighted_jacobians = np.einsum("noi,nij->noj", geometry, jacobians, optimize=True)
    sensitivity = np.einsum(
        "noi,noj->ij", jacobians, weighted_jacobians, optimize=True
    ) / samples
    covariance = (covariance + covariance.T) / 2.0
    sensitivity = (sensitivity + sensitivity.T) / 2.0

    covariance_values, covariance_vectors = np.linalg.eigh(covariance)
    covariance_values = np.clip(covariance_values, 0.0, None)
    covariance_sqrt = (
        covariance_vectors * np.sqrt(covariance_values)
    ) @ covariance_vectors.T
    influence = covariance_sqrt @ sensitivity @ covariance_sqrt
    influence = (influence + influence.T) / 2.0
    eigenvalues = np.linalg.eigvalsh(influence)[::-1]
    numerical_scale = max(1.0, float(np.max(np.abs(eigenvalues), initial=0.0)))
    negative_floor = -1e-9 * numerical_scale
    if float(np.min(eigenvalues, initial=0.0)) < negative_floor:
        raise RuntimeError("functional influence matrix is unexpectedly non-PSD")
    eigenvalues = np.clip(eigenvalues, 0.0, None)
    functional_mass = float(eigenvalues.sum())
    normalized = (
        eigenvalues / functional_mass
        if functional_mass > 0
        else np.zeros_like(eigenvalues)
    )
    positive = normalized[normalized > 0]
    effective_dimension = (
        float(np.exp(-np.sum(positive * np.log(positive))))
        if positive.size
        else 0.0
    )
    participation_ratio = (
        float(1.0 / np.sum(np.square(positive))) if positive.size else 0.0
    )
    tolerance = (
        float(relative_tolerance)
        if relative_tolerance is not None
        else max(samples, hidden_dimensions) * np.finfo(np.float64).eps
    )
    leading = float(eigenvalues[0]) if eigenvalues.size else 0.0
    active_rank = (
        int(np.count_nonzero(eigenvalues > tolerance * leading))
        if leading > 0.0
        else 0
    )
    activation_leading = float(covariance_values.max(initial=0.0))
    activation_rank = (
        int(np.count_nonzero(covariance_values > tolerance * activation_leading))
        if activation_leading > 0.0
        else 0
    )

    shares: dict[str, float] = {}
    for requested in top_k:
        count = int(requested)
        if count < 1:
            raise FunctionalInfluenceInputError("top_k values must be positive")
        shares[f"top_{count}_share"] = (
            float(normalized[: min(count, hidden_dimensions)].sum())
            if functional_mass > 0
            else 0.0
        )

    return {
        "metric": "functional_influence_spectrum",
        "estimand": "sample-distribution-weighted local output influence",
        "output_geometry": geometry_name,
        "n_samples": int(samples),
        "hidden_dimensions": int(hidden_dimensions),
        "output_dimensions": int(jacobians.shape[1]),
        "functional_mass": functional_mass,
        "effective_dimension": effective_dimension,
        "participation_ratio": participation_ratio,
        "active_rank": active_rank,
        "activation_rank": activation_rank,
        "inactive_activation_dimensions": max(0, activation_rank - active_rank),
        "spectrum": eigenvalues.tolist(),
        "normalized_spectrum": normalized.tolist(),
        **shares,
    }


def bootstrap_functional_influence(
    activations: np.ndarray,
    output_jacobians: np.ndarray,
    *,
    probabilities: np.ndarray | None = None,
    output_metric: np.ndarray | None = None,
    draws: int = 200,
    confidence: float = 0.95,
    seed: int = 0,
) -> dict[str, object]:
    """Add paired sample-bootstrap intervals to a functional influence profile."""
    activations = _as_finite_array("activations", activations, 2)
    jacobians = _as_finite_array("output_jacobians", output_jacobians, 3)
    if draws < 1:
        raise FunctionalInfluenceInputError("draws must be positive")
    if not 0.0 < confidence < 1.0:
        raise FunctionalInfluenceInputError("confidence must lie between zero and one")
    base = functional_influence_spectrum(
        activations,
        jacobians,
        probabilities=probabilities,
        output_metric=output_metric,
    )
    rng = np.random.default_rng(seed)
    samples = len(activations)
    statistics = {"functional_mass": [], "effective_dimension": [], "participation_ratio": []}
    for _ in range(draws):
        indices = rng.integers(0, samples, size=samples)
        profile = functional_influence_spectrum(
            activations[indices],
            jacobians[indices],
            probabilities=probabilities[indices] if probabilities is not None else None,
            output_metric=output_metric[indices] if output_metric is not None else None,
        )
        for name in statistics:
            statistics[name].append(float(profile[name]))
    tail = (1.0 - confidence) / 2.0
    base["bootstrap"] = {
        "draws": int(draws),
        "confidence": float(confidence),
        "seed": int(seed),
        "intervals": {
            name: {
                "low": float(np.quantile(values, tail)),
                "high": float(np.quantile(values, 1.0 - tail)),
            }
            for name, values in statistics.items()
        },
    }
    return base
