import numpy as np
import pytest

from mbe_eval.checkpoint_metrics import (
    matrix_view,
    spectral_norm_exact,
    spectral_norm_power,
    summarize_checkpoint_pair,
)


def test_matrix_view_uses_last_axis_as_output() -> None:
    tensor = np.arange(2 * 3 * 4).reshape(2, 3, 4)
    assert matrix_view(tensor).shape == (6, 4)


def test_power_iteration_matches_exact_spectral_norm() -> None:
    matrix = np.diag([5.0, 2.0, 1.0])
    assert spectral_norm_power(matrix, iterations=25, seed=3) == pytest.approx(5.0)
    assert spectral_norm_exact(matrix) == pytest.approx(5.0)


def test_checkpoint_summary_pairs_by_role_not_full_keras_name() -> None:
    initial = [
        ("conv2d_1/kernel:0", np.eye(2)),
        ("conv2d_1/bias:0", np.zeros(2)),
    ]
    final = [
        ("conv2d_8/kernel:0", 2.0 * np.eye(2)),
        ("conv2d_8/bias:0", np.ones(2)),
    ]
    result = summarize_checkpoint_pair(final, initial, spectral_iterations=25)
    assert result["parameter_count"] == 6
    assert result["kernel_count"] == 1
    assert result["parameter_l2"] == pytest.approx(np.sqrt(10.0))
    assert result["distance_from_initialization_l2"] == pytest.approx(2.0)
    assert result["spectral_sum_sq"] == pytest.approx(4.0)


def test_checkpoint_summary_rejects_misaligned_shapes() -> None:
    with pytest.raises(ValueError, match="shape mismatch"):
        summarize_checkpoint_pair(
            [("dense/kernel:0", np.ones((2, 3)))],
            [("dense_2/kernel:0", np.ones((3, 2)))],
        )
