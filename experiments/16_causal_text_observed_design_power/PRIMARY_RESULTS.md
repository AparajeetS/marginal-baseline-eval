# Observed-Design Power: Primary Results

The frozen degree-6 study completed all 4,500 simulation cells: three observed
metric-reliability tiers, three baseline levels, five injected effect sizes,
and 100 repetitions. Both nuisance families were estimable in every cell.

## Main Result

The strict two-family consensus rule has near-zero power at the current
36-configuration geometry. This is not because the injected signal is
undetectable by every MBE specification. The additive polynomial-ridge family
recovers moderate and large effects, while the interaction family almost never
produces a positive full-refit lower bound and therefore vetoes consensus.

| Injected effect | Additive predictive support | Interaction predictive support | Strict consensus |
|---:|---:|---:|---:|
| 0.0 | 0% in every cell | 0% in every cell | 0% in every cell |
| 0.2 | 10%-74% | 0% | 0% |
| 0.3 | 53%-93% | 0%-1% | 0%-1% |
| 0.5 | 97%-100% | 0%-6% | 0%-6% |

Ranges span reliability tiers and B1/B2/B3 baselines. Full cell-level rates,
Wilson intervals, Delta-MSE values, and residual-permutation results are in
[`out_primary/power_summary.csv`](out_primary/power_summary.csv) and
[`out_primary/power_ledger.csv`](out_primary/power_ledger.csv).

## Interpretation

1. Null behavior is conservative in this semi-synthetic design: no
   specification falsely supported a null increment.
2. The additive learner has a sensible power curve and high power for the
   largest injected effects.
3. Degree-6 interaction adjustment is too unstable for a mandatory veto at 36
   independent configurations. Its median Delta-MSE is often positive, but
   its full-refit lower bound remains strongly negative.
4. Therefore, the completed real-metric abstention cannot be interpreted as
   evidence that the metrics contain no incremental information. It is
   compatible with a consensus rule that lacks power at this sample size.
5. Choosing the additive learner after seeing this result would be
   post-selection. The primary result remains the failed power of the frozen
   consensus rule. A complete degree-2 grid is being run as an explicitly
   labeled sensitivity analysis.

This result strengthens MBE as an audit of analysis specifications, but weakens
any narrative that treats the current 36-configuration metric washout as a
substantive null finding.

