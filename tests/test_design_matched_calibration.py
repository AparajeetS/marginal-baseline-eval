from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import numpy as np


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "experiments"
    / "21_design_matched_calibration"
    / "run_calibration.py"
)
SPEC = importlib.util.spec_from_file_location("design_matched_calibration", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def test_frozen_design_sizes_and_balance() -> None:
    image = MODULE.make_image_design().frame
    text = MODULE.make_text_design().frame

    assert len(image) == 96
    assert image["config_id"].nunique() == 48
    assert image.groupby("config_id").size().eq(2).all()
    assert image["arch"].value_counts().to_dict() == {
        "cnn": 32,
        "resnet": 32,
        "wide_resnet": 32,
    }

    assert len(text) == 48
    assert text["config_id"].nunique() == 24
    assert text.groupby("config_id").size().eq(2).all()
    assert text["model_size"].value_counts().to_dict() == {
        "small": 24,
        "medium": 24,
    }


def test_simulation_is_deterministic_and_finite() -> None:
    first = MODULE.simulate_frame("image", "interaction_increment", 0.30, 0.35, 17)
    second = MODULE.simulate_frame("image", "interaction_increment", 0.30, 0.35, 17)
    columns = [
        "synthetic_metric",
        "synthetic_target",
        "final_train_batch_loss",
        "val_loss",
        "negative_control",
    ]
    assert np.isfinite(first[columns].to_numpy()).all()
    assert np.array_equal(first[columns].to_numpy(), second[columns].to_numpy())


def test_null_scenarios_reject_nonzero_effects() -> None:
    try:
        MODULE.simulate_frame("text", "interaction_proxy_null", 0.80, 0.20, 19)
    except ValueError as error:
        assert "beta=0" in str(error)
    else:
        raise AssertionError("null simulation accepted a nonzero increment")
