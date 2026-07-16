# MBE Credibility Ledger

Status: active adversarial evidence ledger, 2026-07-16.

This document records what would make MBE credible, which checks have passed,
which have failed, and which claims remain blocked. A failure stays in the
ledger after it is fixed. Passing MBE means recovering independently known or
future outcomes, not producing many metric washouts.

## Evidence Standard

MBE is considered submission-credible only after all primary gates pass:

1. calibrated false-positive behavior on repeated conditional-null simulations;
2. useful power on preregistered incremental-signal simulations;
3. recovery under semi-synthetic metrics embedded in real design geometry;
4. stability across flexible nuisance learners and cross-fitting splits;
5. exact reproduction before reaudit of published studies;
6. predictions frozen on development tasks and verified on unseen tasks;
7. prospective model-selection regret measured on runs produced afterward;
8. independent execution from frozen code and artifacts.

No count of models can substitute for independent task families at the
transport gates.

## Current Gate Status

| Gate | Status | Current evidence | What remains |
|---|---|---|---|
| Legacy evidence quarantine | Passed | invalid causal-LM evidence and repeated configurations are labeled exploratory | keep public claims synchronized |
| One-shot synthetic profiles | Passed | six frozen scenarios recover their declared qualitative profiles | one seed is not inferential evidence |
| Repeated Monte Carlo calibration | Conditional pass | the strict joint rule was run for 100 repetitions across sample size, nuisance complexity, heteroskedastic, and clustered scenarios | extend to more task-like designs and effect sizes |
| Full-refit inference stress | Conditional pass | across 320 null/proxy cells there was one predictive-interval false support and zero joint supports; all 80 signal cells were recovered | external implementation and broader effect-size/coverage grid |
| Real-design semi-synthetic calibration | Conditional pass | PGDL Tasks 1-2 preserve real sample sizes and hyperparameter geometry; the interaction ridge held null/proxy decisions to 0-2% | test additional frozen real-design signals and independent implementations |
| Cross-fit leakage isolation | Fixed and tested | rank transforms are now fitted within each training fold; configurations never split across folds | external review and regression tests |
| Published statistic reproduction | Partial pass | Dziugaite et al. source environments and ranking reproduced exactly; its MBE reaudit was regenerated after the fold-rank fix | add more studies with genuine run-level artifacts |
| Method comparison | Conditional pass | robust sign error is reproduced on public data; CMI, granulated Kendall, partial ranks, and MBE share a 50-repetition known-truth factorial benchmark | add a formally calibrated conditional-independence comparator and more designs |
| PGDL development atlas | Not run | 24-specification metadata floor and 48-model implementation pilot only | complete metric battery on all Tasks 1-2 models |
| PGDL validation | Protected | Tasks 4-5 labels exist but checkpoint metrics are unopened | freeze implementation and analysis first |
| PGDL transfer holdout | Protected | Tasks 6-9 checkpoint metrics remain unopened | run once after validation freeze |
| Prospective selection | Not run | evaluation utilities implemented | freeze a recommendation, then generate new outcomes |
| Independent replication | Not run | protocol exists | independent executor and signed artifact report |

## Failures Found During Calibration

### Full-data rank transform

The first cross-fitted reference implementation ranked metric and target values
over the full dataset before splitting folds. Held-out values therefore
influenced the training-fold scale. On 2026-07-16 this was replaced by an
empirical-CDF transform fitted separately inside each training fold. Tests now
verify held-out isolation and configuration-level fold integrity. Earlier
cross-fitted outputs required regeneration before citation. The Dziugaite
reaudit and PGDL metadata floor have now been regenerated; any other output
created before this date remains exploratory until explicitly regenerated.

### Low-flexibility nuisance adjustment

The first 100-repetition Monte Carlo grid found that polynomial degree 2 could
reject conditional-null proxy cases far above the nominal level, with the
problem worsening as sample size made small misspecification easier to detect.
Degree 6 substantially improved those generic synthetic cases. The PGDL
semi-synthetic proxy then exposed interaction misspecification in real
hyperparameter geometry for lower-degree specifications.

The first interaction-capable sensitivity used Extra Trees with a frozen
configuration. It failed decisively, selecting known hyperparameter-only
proxies in 52-100% of generic cells and 100% of PGDL semi-synthetic task cells.
This failure is preserved under `out/extra_trees/`. It shows that flexible model
labels do not guarantee adequate nuisance adjustment.

A transparent degree-six ridge basis with pairwise control interactions was
then tested on the same PGDL semi-synthetic design. It held null/proxy joint
decisions to 0-2% and recovered injected signals in 97-100% of repetitions.
It is eligible for later sensitivity analysis but is not selected as primary
from real metric favorability.

### Interaction-degree implementation mismatch

The first interaction sensitivity was labeled degree six but its implementation
discarded the degree argument and used first-order control terms plus pairwise
interactions. The shared factorial benchmark exposed this because the model
selected a known nonlinear design proxy. The implementation now retains the
requested univariate polynomial degree and adds pairwise first-order
interactions. The PGDL semi-synthetic and metadata-floor interaction outputs
were regenerated after this correction. The pre-correction artifacts remain in
Git history and must not be cited.

### Raw polynomial bootstrap instability

The first full-refit bootstrap exposed severe extrapolation from standardized
degree-six raw powers when resampled folds omitted parts of the control range.
One clustered-null lower Delta-MSE interval became numerically absurd and
stable-signal recovery fell to 45%. Numeric controls are now transformed by a
training-fold empirical CDF and expanded on the bounded interval `[-1, 1]`.
After regeneration, all three tested null/proxy scenarios had 0/20 strict
support and the stable increment had 20/20 support. The 500-repetition
within-block permutation null rejected 7.2%, so that inference path remains
provisional and mildly anti-conservative in the current finite experiment.

This means MBE cannot treat one additive polynomial nuisance model as a
validated default. Primary results require:

- at least one interaction-capable learner;
- sensitivity across preregistered nuisance families;
- a decision rule supported by predictive-improvement uncertainty;
- disagreement reporting rather than selection of the most favorable learner.

### Weak preliminary decision rule

The first repeated report called an increment when the residual permutation
test rejected and the Delta-MSE point estimate was positive. That rule was
deliberately permissive and produced excess proxy decisions. The active rule
requires the lower 95% Delta-MSE interval to exceed zero as well as residual
test rejection. The repeated generic and PGDL semi-synthetic reports have been
regenerated under that stricter rule.

## Remaining Statistical Risks

### Nuisance-model uncertainty

The package now includes a refit bootstrap that resamples independent groups,
rebuilds fold assignments, and refits every nuisance model. In the current
two-sample-size stress matrix, its predictive interval made one false support
across 320 null/proxy cells and recovered all 80 injected-signal cells. It is
the primary interval for the protected protocol, subject to nuisance-family
agreement and continued scoped reporting; this finite matrix is not a universal
coverage guarantee.

Operational Delta MSE is relative to a fitted baseline learner. A metric can
improve a weak learner by compressing information already present in baseline
variables. That is genuine learner-relative utility but not proof of new
conditional information. MBE reports nuisance-learner sensitivity precisely to
keep those interpretations separate.

### Permutation exchangeability

Permuting residuals is exact only under appropriate exchangeability. Task,
configuration, and heteroskedastic structures can violate that assumption.
The current calibration includes ordinary, heteroskedastic, unequal-block, and
clustered nulls. Rejection rates were 5.0%, 4.8%, 5.8%, and 7.0%, respectively,
over 500 repetitions per structure. Because the clustered-null Wilson interval
was approximately 5.1-9.6%, residual permutation is retained as a diagnostic,
not a primary increment gate.

### Control-set semantics

Conditioning changes the estimand. Post-treatment variables can remove real
total information, while insufficient controls leave proxy signal. Every
baseline level must be interpreted separately; MBE does not discover the
correct causal adjustment set automatically.

### Selector circularity

A metric selected by MBE cannot be declared successful because it scores well
under MBE. The selector is evaluated against outcomes from unseen task families
and prospective runs using regret frozen before those outcomes are inspected.

## Claim Maturity

Currently supportable:

- pooled raw correlation and conditional incremental prediction are different
  estimands;
- MBE can recover several known synthetic profiles;
- source robust sign error and MBE incremental utility can disagree without
  contradiction;
- on the current balanced-factorial benchmark, descriptive rank/CMI criteria
  can remain high for known design proxies while corrected interaction MBE
  mostly abstains;
- metric behavior can be task-specific, motivating a reliability atlas.

Not currently supportable:

- MBE has validated nominal error across realistic nuisance structures;
- MBE is superior to all existing metric-evaluation procedures;
- the metric selector improves decisions on unseen tasks;
- any metric family is universally reliable or unreliable;
- MBE identifies causal metric effects;
- the service can certify metric choice for arbitrary customer tasks.

## Primary References And Scope

- [Chernozhukov et al., Double/Debiased Machine Learning](https://arxiv.org/abs/1608.00060): cross-fitting and flexible nuisance estimation; MBE does not inherit causal guarantees from this work.
- [Jiang et al., Fantastic Generalization Measures and Where to Find Them](https://arxiv.org/abs/1912.02178): controlled evaluation of generalization measures.
- [Dziugaite et al., In Search of Robust Measures of Generalization](https://arxiv.org/abs/2010.11924): distributionally robust environment evaluation.
- [Jiang et al., PGDL Competition](https://arxiv.org/abs/2012.07976): public multi-task checkpoint benchmark.

These methods answer overlapping but nonidentical questions. Credibility
requires direct comparison under shared data-generating processes, not novelty
by relabeling their components.
