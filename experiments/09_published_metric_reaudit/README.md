# Published Metric Reaudit

This directory contains a manifest-driven framework for retrospectively
auditing published metric claims. It does not scrape papers, silently infer
controls, or treat unavailable artifacts as negative results.

Each study must provide:

- a source citation and immutable study identifier;
- a local CSV with unique row IDs;
- the target and metric columns;
- an ordered baseline ladder;
- configuration groups and environment columns where available;
- implementation and provenance notes.

Copy `study_manifest.example.json`, freeze the filled manifest in version
control, then run:

```bash
python experiments/09_published_metric_reaudit/run_reaudit.py \
  path/to/study_manifest.json \
  --output-prefix path/to/results/study_reaudit
```

Missing manifest columns and duplicate row IDs are fatal errors. The generated
report presents raw correlation, linear partial rank correlation, grouped
cross-fitted residual association, configuration-bootstrap intervals,
false-discovery-rate-adjusted permutation tests, and out-of-fold predictive
improvement at every declared baseline level. It does not select whichever
level gives the most favorable conclusion.

`CANDIDATE_STUDIES.md` is an intake queue, not a claim that any listed paper has
failed MBE.

## Frozen Studies

- `studies/dziugaite2020`: all 32 complexity measures from the official
  10,000-model CIFAR-10/SVHN ledger, with source-specific preparation and a
  grouped cross-fitted baseline ladder.
