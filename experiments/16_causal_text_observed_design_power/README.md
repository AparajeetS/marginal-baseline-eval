# Causal-Text Observed-Design Power

This work package asks whether the strict MBE rule has enough power at the
exact 36-configuration scale of the corrected causal-text replication. Read
the [preregistration](PREREGISTRATION.md) before interpreting any output.

Primary execution:

```bash
python experiments/16_causal_text_observed_design_power/run_power.py \
  experiments/15_causal_text_factorial_replication/kaggle_downloads/v1/mbe2_causal_text_factorial_replication.csv \
  --output-dir experiments/16_causal_text_observed_design_power/out_primary \
  --repetitions 100 --refit-bootstrap 199 --permutations 99 --workers 14
```

The study is calibration evidence, not a new empirical metric result. Its null
cells measure false support in this fixed environment geometry; positive cells
measure detection power for known injected configuration-level increments.

The completed primary interpretation is in
[`PRIMARY_RESULTS.md`](PRIMARY_RESULTS.md).
The completed post-primary degree-2 comparison is in
[`DEGREE_SENSITIVITY_RESULTS.md`](DEGREE_SENSITIVITY_RESULTS.md).
