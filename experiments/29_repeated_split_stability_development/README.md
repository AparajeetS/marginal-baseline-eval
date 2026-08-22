# Repeated-Split Stability Development

This development-only experiment tests a conservative split-stability candidate
on fresh 24/48-configuration known-truth simulations. It never reads protected
image, text, or PGDL metric-target associations.

Run a non-scientific smoke check:

```bash
python experiments/29_repeated_split_stability_development/run_development.py \
  --output-dir experiments/29_repeated_split_stability_development/out_smoke \
  --workers 1 --smoke
```

Run the frozen development screen:

```bash
python experiments/29_repeated_split_stability_development/run_development.py \
  --output-dir experiments/29_repeated_split_stability_development/out \
  --workers 16
```

The result can select at most one candidate for a separately frozen
confirmation. It cannot authorize protected analyses.
