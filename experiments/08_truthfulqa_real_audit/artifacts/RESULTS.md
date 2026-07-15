# TruthfulQA Reference-Difference Pilot Results

**Predeclared test outcome:** `supports-claim-under-declared-tests`

The candidate crossed the predeclared E1 and aggregate E2 thresholds in these data while the supplied controls did not. This is conditional evidence, not certification or construct validity.

## Audited Cohort

The main cohort contains 7,920 unique, nonconflicting, non-reference answer pairs from 541 questions in 15 sufficiently represented categories.

## Frozen Estimands

| Estimand | Threshold state | Relative out-of-fold MSE improvement | 95% CI for absolute MSE improvement |
|---|---|---:|---:|
| E1, increment beyond declared proxies | meets-declared-threshold | +0.1233 | [+0.0059, +0.0084] |
| E2, aggregate category holdout | meets-declared-threshold | +0.1101 | [+0.0045, +0.0089] |

The practical threshold was fixed at 1% for each estimand before the score was computed. E0 is descriptive only. E3 and E4 were not run.

## Interpretation Boundary

This is a method demonstration on released TruthfulQA v0 human judgments after explicit leakage exclusions. It tests incremental prediction under the frozen proxies, question grouping, and category holdouts. It is not a fresh validation set, a model-family or capability-controlled audit, a causal or construct-validity result, an exact reproduction of TruthfulQA's T5 ROUGE metric, or certification of a benchmark or model.

The governing amended protocol was committed before analysis at `827e192729b1b26dd8c470ae70f028214c942090`. See `claim_card.md`, `cohort_manifest.json`, and `category_summary.csv` for the controls, exclusions, and limitations.
