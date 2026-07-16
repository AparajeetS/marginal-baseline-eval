from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "experiments" / "10_method_comparison" / "run_inference_stress.py"
SPEC = spec_from_file_location("run_inference_stress", SCRIPT)
assert SPEC and SPEC.loader
MODULE = module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_wilson_interval_contains_observed_rate() -> None:
    low, high = MODULE.wilson_interval(25, 500)
    assert low < 0.05 < high


def test_block_null_shapes_and_groups() -> None:
    ordinary, ordinary_group = MODULE.make_block_null("homoskedastic", seed=1)
    clustered, clustered_group = MODULE.make_block_null("clustered", seed=1)
    assert len(ordinary) == 200
    assert ordinary_group is None
    assert clustered_group == "config_id"
    assert clustered.groupby("config_id")["block"].nunique().max() == 1
