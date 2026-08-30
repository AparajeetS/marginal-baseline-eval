import pytest


torch = pytest.importorskip("torch")

from mbe_eval.utils import compute_fim_norm


def test_zero_gradient_fim_is_zero_and_existing_gradients_are_restored() -> None:
    model = torch.nn.Linear(2, 1)
    model.train()
    for parameter in model.parameters():
        parameter.grad = torch.full_like(parameter, 7.0)
    saved = [parameter.grad.clone() for parameter in model.parameters()]
    inputs = torch.ones((3, 2))
    targets = torch.zeros((3, 1))

    value = compute_fim_norm(
        model,
        lambda output, target: output.sum() * 0.0,
        inputs,
        targets,
    )

    assert value == 0.0
    assert model.training is True
    for parameter, expected in zip(model.parameters(), saved):
        torch.testing.assert_close(parameter.grad, expected)
