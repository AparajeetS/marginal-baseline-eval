from __future__ import annotations

from collections.abc import Sequence
from typing import Union

import numpy as np


Tensor = tuple[str, np.ndarray]


def tensor_role(name: str) -> str:
    """Return the checkpoint role encoded by a Keras tensor name."""
    return name.rsplit("/", 1)[-1].split(":", 1)[0]


def matrix_view(tensor: np.ndarray) -> np.ndarray:
    """Flatten all input axes while retaining the final output axis."""
    if tensor.ndim < 2:
        raise ValueError("spectral metrics require a tensor with at least two axes")
    return np.asarray(tensor, dtype=np.float64).reshape(-1, tensor.shape[-1])


def spectral_norm_power(
    tensor: np.ndarray,
    *,
    iterations: int = 12,
    seed: int = 0,
) -> float:
    """Estimate a tensor's matrix spectral norm deterministically."""
    if iterations < 1:
        raise ValueError("iterations must be positive")
    matrix = matrix_view(tensor)
    rng = np.random.default_rng(seed)
    right = rng.standard_normal(matrix.shape[1])
    right /= np.linalg.norm(right)
    for _ in range(iterations):
        left = matrix @ right
        left_norm = np.linalg.norm(left)
        if left_norm == 0:
            return 0.0
        left /= left_norm
        right = matrix.T @ left
        right_norm = np.linalg.norm(right)
        if right_norm == 0:
            return 0.0
        right /= right_norm
    return float(np.linalg.norm(matrix @ right))


def spectral_norm_exact(tensor: np.ndarray) -> float:
    """Compute a tensor's matrix spectral norm by singular-value decomposition."""
    singular_values = np.linalg.svd(matrix_view(tensor), compute_uv=False)
    return float(singular_values[0]) if singular_values.size else 0.0


def summarize_checkpoint_pair(
    final_tensors: Sequence[Tensor],
    initial_tensors: Sequence[Tensor],
    *,
    spectral_method: str = "exact",
    spectral_iterations: int = 48,
    seed: int = 0,
) -> dict[str, Union[float, int]]:
    """Compute weight and update measures from aligned checkpoint tensors."""
    if len(final_tensors) != len(initial_tensors):
        raise ValueError("initial and final checkpoints have different tensor counts")

    parameter_sq = 0.0
    initial_sq = 0.0
    update_sq = 0.0
    kernel_frobenius_sq: list[float] = []
    kernel_spectral_sq: list[float] = []
    parameter_count = 0

    for index, ((final_name, final), (initial_name, initial)) in enumerate(
        zip(final_tensors, initial_tensors)
    ):
        final = np.asarray(final)
        initial = np.asarray(initial)
        if tensor_role(final_name) != tensor_role(initial_name):
            raise ValueError(f"tensor role mismatch: {final_name} vs {initial_name}")
        if final.shape != initial.shape:
            raise ValueError(f"tensor shape mismatch: {final.shape} vs {initial.shape}")

        final64 = final.astype(np.float64, copy=False)
        initial64 = initial.astype(np.float64, copy=False)
        parameter_count += final.size
        parameter_sq += float(np.sum(final64 * final64))
        initial_sq += float(np.sum(initial64 * initial64))
        difference = final64 - initial64
        update_sq += float(np.sum(difference * difference))

        if tensor_role(final_name) == "kernel" and final.ndim >= 2:
            kernel_frobenius_sq.append(float(np.sum(final64 * final64)))
            if spectral_method == "exact":
                spectral = spectral_norm_exact(final64)
            elif spectral_method == "power":
                spectral = spectral_norm_power(
                    final64,
                    iterations=spectral_iterations,
                    seed=seed + index,
                )
            else:
                raise ValueError(f"unknown spectral method: {spectral_method}")
            kernel_spectral_sq.append(spectral * spectral)

    if parameter_sq <= 0 or initial_sq <= 0 or not kernel_frobenius_sq:
        raise ValueError("checkpoint contains no nonzero kernel parameters")
    tiny = np.finfo(np.float64).tiny
    parameter_l2 = np.sqrt(parameter_sq)
    initial_l2 = np.sqrt(initial_sq)
    update_l2 = np.sqrt(update_sq)
    return {
        "parameter_count": parameter_count,
        "tensor_count": len(final_tensors),
        "kernel_count": len(kernel_frobenius_sq),
        "parameter_l2": parameter_l2,
        "initial_parameter_l2": initial_l2,
        "distance_from_initialization_l2": update_l2,
        "relative_distance_from_initialization": update_l2 / initial_l2,
        "update_to_weight_ratio": update_l2 / parameter_l2,
        "frobenius_sum_sq": float(np.sum(kernel_frobenius_sq)),
        "log_frobenius_product_sq": float(
            np.sum(np.log(np.maximum(kernel_frobenius_sq, tiny)))
        ),
        "spectral_sum_sq": float(np.sum(kernel_spectral_sq)),
        "log_spectral_product_sq": float(
            np.sum(np.log(np.maximum(kernel_spectral_sq, tiny)))
        ),
    }
