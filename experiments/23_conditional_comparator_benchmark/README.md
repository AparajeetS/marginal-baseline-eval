# Conditional Comparator Benchmark

This known-truth benchmark compares MBE with strong conditional-dependence and
rank-based references at the 24- and 48-configuration sizes used by the sealed
text and image artifacts. No protected target-metric association is loaded.

## Result

The completed campaign contains 9,600 paired synthetic datasets and 153,600
method rows. No tested method combined strict worst-cell null calibration with
useful worst-cell effect-0.50 power. MBE and the orthogonal score were the most
conservative but underpowered; several higher-apparent-power comparators were
anti-conservative in at least one nuisance or negative-control cell.

This is a calibration-power frontier, not a declaration that one statistical
estimand dominates another. See [COMPARATOR_RESULTS.md](COMPARATOR_RESULTS.md)
for the table and scoped interpretation.

## Reproduce

Install the project with its flexible dependencies and the pinned comparator
requirements, then run:

```bash
python experiments/23_conditional_comparator_benchmark/run_benchmark.py \
  --output-dir experiments/23_conditional_comparator_benchmark/out \
  --workers 16
```

The frozen protocol is [PREREGISTRATION.md](PREREGISTRATION.md). The output
directory retains the canonical method ledger, compact summary, manifest, and
SHA-256 checks. Development drafts and partial ledgers are not evidence.
