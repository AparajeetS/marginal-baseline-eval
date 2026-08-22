# MBE Credibility Ledger

Status: active adversarial evidence ledger, updated 2026-08-11.

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
| Repeated Monte Carlo calibration | Conditional pass | degrees 1-3 reached 100% false support in at least one generic proxy cell; degree 4 reduced the maxima to 17% additive and 5% interaction, while degree 6 reduced them to 0% and 3% | freeze design-specific learner eligibility and add independent simulation implementations |
| Full-refit inference stress | Conditional pass | across 6,400 null/proxy rows, predictive false support was 0.25% and joint false support was 0.125%; all 1,600 signal rows had predictive support | external implementation and broader effect-size/coverage grid |
| Real-design semi-synthetic calibration | Failed current consensus; components informative | all degrees controlled the independent null, additive large-effect power was 98.2%-100%, but interaction large-effect power was only 1.0%-4.6% at 36 configurations | replace universal consensus with a prospectively frozen calibration gate and validate it before protected use |
| Refit-draw convergence | Passed in named designs | 499 draws agreed with the paired 999-draw reference in all 1,000 comparisons; 199 draws had up to 3% disagreement in one proxy cell | use 499 near publication decisions and test more designs |
| Cross-fit leakage isolation | Fixed and tested | rank transforms are now fitted within each training fold; configurations never split across folds | external review and regression tests |
| Corrected causal-LM pipeline | Passed as implementation gate | 24/24 WikiText-2 pilot rows completed; causal future-token perturbation changed prefix logits by 0.0 while the unmasked negative control changed them | retain compact completion record; this is not metric evidence |
| Corrected causal-text factorial v1 | Completed with inference abstention | 100/100 rows, three metric batches per run, causal test passed; only 20 configuration units and the random control is invalid after configuration aggregation | do not issue metric verdicts; retain failure and run the separately reported 36-configuration replication |
| Causal-text sequential replication | Completed; no frozen increment support | 180/180 valid rows, 36 configuration units, causal test passed, full-run-ID random control valid, and 199-draw grouped full-refit analysis run across all frozen metric/baseline/sensitivity cells; no metric passed the joint lower-interval rule | retain as an underpowered abstention case; do not infer universal metric unreliability |
| Corrected image factorial | Artifact complete; analysis locked | 96/96 valid CIFAR-10 rows, 48 independent configurations, two seeds each, three balanced architectures, zero errors or duplicates, matching frozen hashes, and a passing completion gate | calibration selected no eligible rule; keep associations sealed pending a newly confirmed method |
| Multi-corpus causal-LM atlas | Artifact complete; analysis locked | 144/144 valid rows, 72 independent configurations, two seeds each, 24 complete configurations in each of WikiText-2, PTB, and Tiny Shakespeare, zero errors or duplicates, and passing causal and structural gates | calibration selected no eligible rule; keep within-corpus and transport associations sealed pending a newly confirmed method |
| GPU follow-up design-matched calibration | Completed negative gate | the 48,000-row screen selected no eligible candidate; a later pooled-PGDL rule failed null control, and its disjoint revision controlled all null cells but missed the B3 power gate by Wilson lower bound 0.4920 versus 0.5000 | retain every failure and near miss; develop only on new known-truth data and require another frozen confirmation before protected use |
| Repeated-split stability development | Completed negative gate | fresh 24/48-configuration geometries produced 10,080 fully estimable rows; no 3- or 5-split intersection candidate met both the 5% worst-null/proxy and 50% weakest effect-0.50 raw development floors | retain the rejected family; use fresh known-truth development for any materially different estimator or sample-size-aware abstention policy |
| Published statistic reproduction | Partial pass | Dziugaite et al. source environments and ranking reproduced exactly; its MBE reaudit was regenerated after the fold-rank fix | add more studies with genuine run-level artifacts |
| Method comparison | Completed finite benchmark | 9,600 paired known-truth datasets produced 153,600 rows for raw and residual ranks, GCM, WGCM.est, KCI, orthogonal score, MBE, and principled CRT abstention; no method combined strict worst-cell calibration with useful worst-cell power at 24/48 configurations | add independent implementations, larger independent-unit counts, and design-matched conditional samplers; do not claim method superiority |
| PGDL development atlas | Not run | 24-specification metadata floor and 48-model implementation pilot only | complete metric battery on all Tasks 1-2 models |
| PGDL validation | Protected | Tasks 4-5 labels exist but checkpoint metrics are unopened | freeze implementation and analysis first |
| PGDL transfer holdout | Protected; opening denied | Tasks 6-9 comprise 240 independent models and checkpoint metrics remain unopened; the frozen pooled calibration sequence did not pass every gate | keep sealed unless a newly developed rule earns eligibility on disjoint known-truth confirmation, or replace it with a genuinely external holdout |
| Prospective selection | Not run | evaluation utilities implemented | freeze a recommendation, then generate new outcomes |
| Independent replication | Packet prepared; not independent | packet v2 validates frozen inputs, generated hashes, exact row counts, duplicate keys, sealed decisions, and tests; an internal dry run passed | independent executor, conflict disclosure, discrepancies, and signed conclusion |

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

The completed degrees 1-6 map found that degrees 1-3 could reject at least one
conditional-null proxy in 100% of generic cells. Degree 4 reduced the worst
joint false support to 17% for additive ridge and 5% for interaction ridge.
Degree 6 reduced those maxima to 0% and 3%. Larger samples exposed
misspecification rather than repairing it.

The observed causal-text geometry exposed the opposite failure mode. Additive
large-effect power was 98.2%-100%, but interaction-family power was only
1.0%-4.6% at every tested degree. No degree made the universal two-family
consensus both proxy-safe and adequately powered at 36 configurations.

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

This means MBE cannot treat either one additive learner or one
interaction-capable learner as a universal default. Future primary results
require outcome-blind calibration of candidate families in the target design,
full-refit predictive uncertainty, agreement among families that actually pass
the frozen calibration gate, and abstention when none pass.

### Weak preliminary decision rule

The first repeated report called an increment when the residual permutation
test rejected and the Delta-MSE point estimate was positive. That rule was
deliberately permissive and produced excess proxy decisions. The active rule
requires the lower 95% Delta-MSE interval to exceed zero as well as residual
test rejection. The repeated generic and PGDL semi-synthetic reports have been
regenerated under that stricter rule.

### Repeated-seed random negative control

The first corrected causal-text factorial generated `random_metric` from the
repeated seed ID. Because the same five seeds occur in every configuration, its
configuration mean is constant and it cannot act as a configuration-level
negative control. The 100 trained models, causal mask, and all non-random
metric measurements remain valid, but the factorial is not eligible to
validate MBE's negative-control behavior or to issue metric verdicts. The
sequential replication derives the control from the full `run_id` and is
reported separately rather than repairing the completed artifact in place.

### Prospective pooled-PGDL gate

The first frozen 240-model pooled-PGDL rule retained useful simulated power but
failed null control, with a worst raw false-support rate of 18% in a
heteroskedastic proxy cell. A revised degree-two interaction ridge was chosen
from a separate development surface and confirmed on disjoint seeds. It
controlled every frozen null cell, but the B3 low-reliability effect-0.50 cell
had 59/100 support and a Wilson lower bound of 0.4920 against the prespecified
0.5000 threshold. The global gate therefore failed and the protected
target-metric associations remain unopened.

### Conditional comparator calibration

The known-truth comparator benchmark retained 9,600 paired datasets and
153,600 method rows. Raw Spearman, residual Spearman, GCM, WGCM.est, and KCI
showed higher apparent power than the conservative MBE and orthogonal rules,
but each had substantial false support in at least one nuisance or negative-
control cell. MBE and the orthogonal score had lower absolute false support but
poor worst-cell effect-0.50 power. These results establish a finite-sample
calibration-power frontier across different estimands; they do not establish
that MBE dominates conditional-independence tests.

### Repeated-split stability intersection

Experiment 29 tested whether a positive conditional-rank decision that survives
three or five independently shuffled, configuration-blocked cross-fit splits
would resolve the small-design tradeoff. It did not. The conservative degree-4,
three-split, alpha-0.01 candidate reached the 5% raw null ceiling but had only
5% minimum effect-0.50 support; more powerful variants reached 10-25% worst
null/proxy support. The family is retained as a negative development result and
does not earn a confirmation or protected-outcome opening.

## Remaining Statistical Risks

### Nuisance-model uncertainty

The package now includes a refit bootstrap that resamples independent groups,
rebuilds fold assignments, and refits every nuisance model. In the expanded
four-sample-size stress matrix, its predictive interval made 16 false supports
across 6,400 null/proxy rows (0.25%) and recovered all 1,600 injected-signal
rows. It is the primary uncertainty path for prospectively calibrated nuisance
families; this finite matrix is not a universal coverage guarantee.

Operational Delta MSE is relative to a fitted baseline learner. A metric can
improve a weak learner by compressing information already present in baseline
variables. That is genuine learner-relative utility but not proof of new
conditional information. MBE reports nuisance-learner sensitivity precisely to
keep those interpretations separate.

### Permutation exchangeability

Permuting residuals is exact only under appropriate exchangeability. Task,
configuration, and heteroskedastic structures can violate that assumption.
The expanded calibration includes homoskedastic, heteroskedastic,
unequal-block, and clustered nulls. Rejection rates were 7.05%, 5.30%, 7.25%,
and 6.95%, respectively, over 2,000 repetitions per structure. Three Wilson
intervals excluded nominal 5%. Residual permutation is retained as a
diagnostic, not a primary increment gate.

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
- nuisance complexity must be calibrated against both known proxies and power
  in the target design;
- the current mandatory two-family consensus is underpowered at 36
  configurations and cannot support substantive null conclusions;
- no tested comparator in the 24/48-configuration known-truth benchmark was
  both strictly calibrated in every null cell and usefully powered in every
  effect-0.50 cell;
- repeated agreement across grouped cross-fit splits alone does not resolve
  that 24/48-configuration calibration-power frontier;
- the prospectively frozen pooled-PGDL analysis correctly abstained after a
  binding near miss, leaving all protected associations sealed;
- metric behavior can be task-specific, motivating a reliability atlas.

Not currently supportable:

- MBE has validated nominal error across realistic nuisance structures;
- MBE is superior to all existing metric-evaluation procedures;
- a higher apparent-power comparator is reliable when its known-null support
  is uncontrolled in the same design;
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
