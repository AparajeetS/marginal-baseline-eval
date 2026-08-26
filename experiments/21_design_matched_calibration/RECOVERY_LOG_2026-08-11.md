# Extra Trees Seed-Domain Recovery

The first scientific screen completed 48,000 planned task rows on 2026-08-11.
All 38,400 polynomial-ridge rows were estimable. All 9,600 Extra Trees rows
failed before model fitting because the deterministic analysis seeds exceeded
scikit-learn's accepted unsigned 32-bit `random_state` range.

This was classified as an implementation failure rather than a scientific
estimability result. `SCREEN_V1_RECOVERY_SHA256SUMS` preserves the hashes of
the invalid bundle, which remains recoverable from Git history. The redundant
raw failed rows are not kept in the current tree because they contain no model
fits or scientific outcomes.

Recovery changes only the adapter in `mbe_eval.crossfit._extra_trees_predict`:
the existing deterministic seed is mapped modulo `2**32` when passed to
`ExtraTreesRegressor`. A regression test now runs the Extra Trees audit with a
seed greater than `2**32`; the targeted local and VM suites both pass 19/19
tests.

The calibration protocol, design grids, scenarios, task seeds, thresholds,
candidate set, and frozen `run_calibration.py` hash were not changed. The
recovery retains the 38,400 successful rows and reruns exactly the missing
9,600 Extra Trees cells. Confirmation remains conditional on the corrected
screen's original automatic selection rule.
