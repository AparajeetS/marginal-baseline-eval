from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "experiments" / "30_oracle_feasibility_frontier" / "run_frontier.py"
SPEC = importlib.util.spec_from_file_location("oracle_frontier", RUNNER)
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


def test_full_grid_is_frozen_size_and_balanced() -> None:
    tasks = module.task_grid(False)
    assert len(tasks) == 126_000
    assert len({tuple(task[key] for key in module.TASK_KEYS) for task in tasks}) == len(tasks)


def test_simulator_returns_balanced_groups_and_exact_null_residuals() -> None:
    frame = module.simulate_frame("image_like", 24, "B3_validation", "interaction_proxy_null", 0.30, 0.0, 7)
    assert len(frame) == 48
    assert frame["config_id"].nunique() == 24
    assert frame.groupby("config_id").size().eq(2).all()
    assert np.isfinite(frame[["metric_mu", "target_mu", "metric", "target"]].to_numpy()).all()


def test_baselines_share_generated_observations_but_change_exact_target_mean() -> None:
    arguments = ("text_like", 24, "shared_signal", 0.80, 0.50, 11)
    b1 = module.simulate_frame(arguments[0], arguments[1], "B1_design", *arguments[2:])
    b3 = module.simulate_frame(arguments[0], arguments[1], "B3_validation", *arguments[2:])
    assert np.array_equal(b1["metric"].to_numpy(), b3["metric"].to_numpy())
    assert np.array_equal(b1["target"].to_numpy(), b3["target"].to_numpy())
    assert not np.array_equal(b1["target_mu"].to_numpy(), b3["target_mu"].to_numpy())


def test_single_cell_estimates_all_methods() -> None:
    task = module.task_grid(True)[0]
    result = module._run_cell(task)
    assert result["status"] == "estimated"
    for method in module.METHODS:
        assert np.isfinite(result[f"{method}_score"])
        assert 0.0 <= result[f"{method}_p"] <= 1.0
