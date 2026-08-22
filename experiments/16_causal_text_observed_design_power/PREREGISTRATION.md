# Observed-Design Power Calibration

Frozen before execution on 2026-07-29.

## Question

Given the exact sample structure of the corrected causal-text replication, how
often can the strict MBE decision recover a known configuration-level increment,
and how often does it falsely support an increment under a known null?

This is a semi-synthetic calibration of the analysis protocol. It is not new
language-model evidence and cannot establish that any observed metric is valid
or invalid.

## Fixed Design

- Source ledger: the 180 valid rows and 36 independent configurations in
  `experiments/15_causal_text_factorial_replication/kaggle_downloads/v1/`.
- Independence unit: `config_id`; five seed rows remain nested in each unit.
- Outcome/control geometry: observed `test_loss` and the frozen B1/B2/B3
  controls are retained.
- Metric reliability tiers: low, median, and high ICC tiers selected
  deterministically from the 13 non-random observed metrics. The observed
  metric values are used only to estimate reliability; every simulated metric
  is newly generated.
- Synthetic metric: a standard-normal configuration component plus independent
  seed noise, mixed to match the tier ICC.
- Synthetic outcome: standardized observed test loss plus `beta` times the
  synthetic configuration component.

Under `beta = 0`, the generated metric is independent of the fixed outcome and
controls by construction. Positive `beta` values create a known stable
configuration-level increment.

## Frozen Grid

- Effect sizes `beta`: `0.0, 0.1, 0.2, 0.3, 0.5` outcome standard deviations.
- Repetitions: 100 per tier, effect, and baseline cell.
- Baselines: B1 design, B2 training state, B3 validation.
- Nuisance families: degree-6 polynomial ridge and degree-6 polynomial ridge
  with interactions.
- Cross-fitting: five folds grouped by configuration.
- Refit bootstrap: 199 configuration resamples.
- Residual permutations: 99, blocked by model size.
- Seed root: `20260729`.

## Primary Decisions

The primary strict decision is positive only when the 95% full-refit
Delta-MSE lower bound is above zero for both nuisance families. Nuisance-family
disagreement is an abstention. The residual-permutation joint decision is
reported separately because its clustered-null calibration is provisional.

Primary summaries are:

1. strict false-support rate at `beta = 0`;
2. strict power at each positive effect;
3. Wilson 95% intervals for each rate;
4. results separated by baseline and metric-reliability tier.

No cell may be removed because its result is unfavorable. Failed estimation
must be reported. A pilot may use fewer repetitions or refits only for runtime
validation and must be labeled non-primary.

## Post-Primary Sensitivity: 2026-07-29

The primary degree-6 grid completed before this sensitivity was specified.
Additive polynomial ridge recovered moderate and large injected effects, while
polynomial ridge with interactions almost never produced a positive full-refit
lower bound and therefore vetoed nearly every strict consensus decision. Null
false support remained zero.

To test the specific hypothesis that nuisance flexibility is excessive for 36
independent configurations, the complete 4,500-cell grid is repeated at degree
2 with all other settings, seeds, metrics, baselines, nuisance families, and
decision rules unchanged. This is a labeled sensitivity analysis and cannot
replace the primary degree-6 result.
