# Orthogonal Score Development

This experiment develops a replacement inferential layer after the frozen
design-matched calibration in experiment 21 selected no eligible learner. It
uses synthetic known-truth data with the same 48-group image and 24-group text
designs. It does not read either protected GPU result ledger.

The v2 estimator cross-fits separate nuisance regressions for ranked metric and
target values, multiplies their configuration-mean residuals, and uses a
studentized Rademacher multiplier bootstrap. The v2 screen pairs each synthetic
dataset across nuisance candidates and baseline ladders, examines a recorded
ridge grid, and uses the development-selected two-sided threshold 0.005.
Its estimand is conditional rank covariance. MBE predictive gain remains a
separate quantity.

## Smoke Test

```bash
python experiments/22_orthogonal_score_development/run_development.py \
  --output-dir experiments/22_orthogonal_score_development/out_smoke \
  --workers 1 \
  --smoke
```

## Bounded Development Screen

```bash
python experiments/22_orthogonal_score_development/run_development.py \
  --output-dir experiments/22_orthogonal_score_development/out_development_v2_10 \
  --workers 8 \
  --repetitions 10 \
  --wild-draws 999
```

Development outputs are diagnostic. They cannot unlock the protected image or
text associations. A candidate must first be frozen and rerun on untouched
confirmation seeds under a separate preregistration.

The complete v1 source that produced `out_development_10` is retained inside
that output directory. V1 used rowwise products, ridge 0.001, unpaired
candidate simulations, and threshold 0.05; it failed calibration.

The completed development record is summarized in
[V2_HUNDRED_REPETITION_RESULTS.md](V2_HUNDRED_REPETITION_RESULTS.md),
[SAMPLE_SIZE_FRONTIER_RESULTS.md](SAMPLE_SIZE_FRONTIER_RESULTS.md), and
[STABILITY_RESULTS.md](STABILITY_RESULTS.md). No 24/48-configuration candidate
earned a protected-data opening.
