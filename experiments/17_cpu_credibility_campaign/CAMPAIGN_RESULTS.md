# CPU Credibility Campaign: Completed Results

This report covers the completed comparator, generic Monte Carlo, package,
public-ledger, and amended full-refit inference-stress lanes.

## Shared Factorial Comparison

Four independent shards pooled to 200 repetitions per scenario.

| Scenario | Stable global increment | Additive MBE support | Interaction MBE support |
|---|---:|---:|---:|
| Independent null | no | 0.0% | 1.0% |
| Design proxy | no | 67.5% | 5.5% |
| Interaction proxy | no | 89.5% | 2.0% |
| Axis-specialist proxy | no | 0.5% | 0.5% |
| Genuine increment | yes | 94.5% | 93.0% |
| Sign-flip increment | no stable pooled direction | 0.5% | 13.0% |

The compact, non-refit additive specification is badly fooled by two known
factorial proxies. Interaction adjustment removes most of those false
decisions while retaining high genuine-signal power. This is evidence against
presenting one nuisance specification as universally valid and supports the
full-refit, calibration-gated workflow.

## Generic Monte Carlo Calibration

The pooled ledger contains 19,200 runs: 100 repetitions for every scenario,
sample-size, degree, and nuisance-family cell.

At degree 6:

- polynomial ridge had 0% joint false support across all tested null/proxy
  cells and 99%-100% power on signal cells;
- polynomial ridge with interactions had at most 3% joint false support and
  99%-100% power;
- Extra Trees retained 99%-100% signal power but falsely supported the
  nonlinear proxy in as many as 94% of repetitions.

At degree 2, both polynomial learners failed the nonlinear-proxy control,
reaching 100% joint false support at larger sample sizes. Larger samples expose
misspecification rather than repairing it. These results make nuisance-model
calibration a prerequisite for MBE inference, not an optional robustness
check.

## Corrected Inference Stress

All eight amended shards completed with exact pooled counts: 8,000 full-refit
rows and 8,000 block-null rows. Across 6,400 null/proxy rows, predictive false
support was 0.25% and joint false support was 0.125%; the maximum cell-level
rates were 3.0% and 2.5%, respectively. Predictive support recovered all 1,600
genuine-increment rows, while joint support recovered 1,597 (99.81%).

The 2,000-repetition block-null results were less favorable. Residual
permutation rejected 6.95% of clustered nulls, 5.30% of heteroskedastic nulls,
7.05% of homoskedastic nulls, and 7.25% of unequal-block nulls. Three Wilson
intervals excluded the nominal 5% level. This confirms that residual
permutation must remain diagnostic, while the full-refit predictive interval
is the calibrated primary path for the named simulations. See
[`INFERENCE_STRESS_RESULTS.md`](INFERENCE_STRESS_RESULTS.md).

## Nuisance-Complexity Map

The combined degrees 1-6 map exposes a real calibration tradeoff. Degrees 1-3
had high observed-design additive power but reached 100% joint false support
in at least one generic proxy cell. Degree 4 reduced worst-case generic false
support to 17% additive and 5% interaction; degree 6 reduced it to 0% and 3%.

In the exact 36-configuration causal-text geometry, the additive family
recovered 98.2%-100% of `beta = 0.5` signals across degrees. The interaction
family recovered only 1.0%-4.6%, leaving the mandatory consensus with the same
1.0%-4.6% ceiling. There is no tested degree that makes the universal
two-family consensus both proxy-safe and adequately powered here. See
[`NUISANCE_COMPLEXITY_ABLATION.md`](NUISANCE_COMPLEXITY_ABLATION.md).

## Refit-Draw Convergence

The paired convergence ledger completed 4,000 rows. Relative to the 999-draw
reference, 499 draws agreed in all 1,000 paired decisions. The worst cell
agreement was 97% at 199 draws and 98% at 99 draws, with disagreements confined
to borderline null/proxy cases. This supports 499 draws for
publication-quality decisions near zero and 199 as a scoped exploratory
budget.

## Dziugaite Public-Ledger Reproduction

The source-statistic reconstruction passed its published environment-count,
measure-order, and robust-maximum checks. The complementary MBE audit used
9,700 runs, 1,000 independent configurations, 32 metrics, pooled and
dataset-specific scopes, and B1/B2 baselines.

Most metrics retained incremental information:

- pooled B1: 29 of 32 `increment-supported`;
- pooled B2: 24 of 32 `increment-supported`;
- CIFAR-10: 27-28 of 32 supported;
- SVHN: 29-30 of 32 supported.

Across the 24 source-comparable headline metrics, source ranking and MBE
absolute-residual ranking had Spearman correlation `0.479`. The methods are
related but not interchangeable. This directly argues against a blanket
"established metrics are lying" narrative: MBE preserves many metrics while
changing some rankings and exposing estimand dependence.

## Software Lane

The independent VM environment passed all 49 tests and built both wheel and
source distributions. The package/public-ledger lane exited successfully.

## Current Scientific Direction

The evidence favors MBE as a **calibration-gated framework for deciding which
metric conclusions survive a declared baseline and nuisance model**, not as a
universal metric elimination test. The key new finding is that metric verdicts
can be dominated by nuisance-model misspecification or excessive flexibility.
MBE should calibrate nuisance-family eligibility before protected outcomes,
report that dependence, and abstain when no frozen family demonstrates both
null/proxy control and useful power.

Pooled tables are in [`out/pooled/`](out/pooled/). Complete shard outputs,
public-ledger tables, hashes, and execution logs are retained under `out/` and
`vm_campaign_artifacts/`.
