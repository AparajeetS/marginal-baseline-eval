from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "experiments" / "31_image_target_transport_atlas" / "mbe3_image_transport_atlas.py"
SPEC = importlib.util.spec_from_file_location("image_transport_atlas", RUNNER)
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)


def test_each_dataset_has_120_runs_and_24_independent_configurations() -> None:
    for dataset in ("cifar10", "cifar100", "svhn"):
        grid = module.frozen_grid(dataset, False)
        assert len(grid) == 120
        assert len({config.config_id for config in grid}) == 24
        assert len({config.run_id for config in grid}) == 120
        assert {config.arch for config in grid} == {"cnn", "resnet", "wide_resnet"}
        assert {config.seed for config in grid} == {8311, 8312, 8313, 8314, 8315}


def test_dataset_specs_cover_frozen_environments() -> None:
    assert module.dataset_spec("cifar10")["classes"] == 10
    assert module.dataset_spec("cifar100")["classes"] == 100
    assert module.dataset_spec("svhn")["test_population"] == 26_032
