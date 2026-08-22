# Design-Matched Calibration

This package is the outcome-blind opening gate for the completed image and
multi-corpus GPU artifacts. Read the
[`PREREGISTRATION.md`](PREREGISTRATION.md) before running it.

The script constructs the frozen factor grids itself. It never reads the
protected result ledgers.

## Screen

```bash
python experiments/21_design_matched_calibration/run_calibration.py \
  --stage screen \
  --output-dir experiments/21_design_matched_calibration/out/screen \
  --workers 16
```

## Confirm

Run confirmation only after the screen completes and its selection file has
been retained unchanged:

```bash
python experiments/21_design_matched_calibration/run_calibration.py \
  --stage confirm \
  --screen-selection experiments/21_design_matched_calibration/out/screen/screen_selection.json \
  --output-dir experiments/21_design_matched_calibration/out/confirm \
  --workers 16
```

`FINAL_ELIGIBILITY.json` is the binding open-or-abstain decision for each
design and baseline. Hash that file before any protected association is
computed.

## Smoke Test

The smoke flag runs a visibly non-scientific two-repetition subset:

```bash
python experiments/21_design_matched_calibration/run_calibration.py \
  --stage screen \
  --output-dir experiments/21_design_matched_calibration/out_smoke/screen \
  --workers 1 \
  --smoke
```

Smoke output cannot be used for learner selection or to unlock an analysis.
