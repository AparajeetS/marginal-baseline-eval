# MBE 2.0 Research Program

Status: active design specification, amended 2026-07-16 by the
[`Conditional Metric Reliability Protocol`](CONDITIONAL_METRIC_RELIABILITY_PROTOCOL.md).

This document supersedes the v1 protocol for all future experiments. The v1
results remain useful as pilot evidence and as examples of evaluation failure,
but they are not submission-grade evidence.

## Working Title

> Which Metric Should You Trust Here? Conditional Reliability Across ML Tasks

## Research Objective

The project studies what evidence is required before a scalar quantity computed
from a trained model can be treated as a useful training, performance, or
generalization metric.

The central claim is not that a particular metric is universally invalid. It is:

> A metric verdict is relative to a declared target, baseline information set,
> deployment environment, and intervention family. Raw pooled correlation alone
> does not establish incremental utility or transportability.

Marginal Baseline Evaluation (MBE 2.0) is the audit engine for making those
dependencies explicit. The program now tests whether those audits can support
a reliability atlas and an abstaining, task-conditional metric selector. A
selector is a gated contribution, not an assumed success.

## Contribution Hierarchy

### Primary contribution

A unified empirical protocol and conditional reliability representation that
separate five questions commonly collapsed into one correlation coefficient:

1. unconditional predictive association;
2. incremental predictive utility beyond available baselines;
3. transport to unseen environments;
4. consistency under controlled interventions;
5. measurement reliability and operational cost.

The primary scientific object is a metric-target-environment reliability
profile, not a global metric leaderboard. Metrics aimed at different targets
are not ranked against one another until a common decision estimand is declared.

### Novelty boundary

MBE does not claim priority for conditioning on hyperparameters, partial
correlation, cross-fitting, or environment holdout evaluation individually.
Its proposed contribution is the auditable combination of:

- an explicit ladder of information available before training, during
  training, and on an independent validation set;
- five separate estimands for association, incremental utility, transport,
  intervention consistency, and measurement reliability;
- synthetic negative, positive, oracle, and deliberately deceptive controls
  that calibrate the audit before real metric families are ranked;
- configuration-blocked uncertainty and environment-level transport tests;
- a scoped metric claim card that records what target a metric predicts,
  beyond which baseline, in which environments, at what cost.

This is a provisional methodological contribution. Gate WP2 must show that the
combined protocol reveals a stable, interpretable distinction not already
provided by prior conditional or robust evaluation methods. If it does not,
the project will publish the benchmark and narrow or withdraw the novelty
claim.

### Secondary contribution

A calibrated benchmark of published metric families, proxy controls, and
deliberately deceptive metrics across public model corpora and new factorial
experiments.

### Gated systems contribution

An abstaining selector that recommends a metric or Pareto set for a declared
task, target, baseline information set, and measurement budget. It becomes a
primary contribution only if leave-one-task-family-out evaluation improves
decision regret over frozen global and raw-correlation selectors. Eight PGDL
tasks alone cannot support a broad learned-router claim.

### Motivating case study

FIM effective rank, previously called `FIM_norm`, is retained as a good-faith
self-falsification case study. It must be described precisely as normalized
effective rank of a true-label empirical-gradient Gram matrix, not as a generic
Fisher information norm.

### Exploratory appendix

CEI-R remains an audit-guided metric-design experiment. It is not a primary
claim and may only be evaluated on environments that were not used to design
its components or weights.

## Non-Claims

MBE 2.0 will not claim:

- that conditional association identifies a causal effect of a metric;
- that one baseline set reveals a metric's intrinsic or true value;
- that all geometric, sharpness, Fisher, or representation metrics fail;
- that a metric is useless whenever it is redundant with available metadata;
- that pooled image and language accuracy values are directly comparable;
- that a large number of scalar columns is equivalent to broad metric coverage.
- that metrics addressing different targets admit a universal ranking;
- that a new task can receive a validated recommendation without target-task
  evidence or calibrated transport evidence;
- that model-level sample size substitutes for independent task families.

## Evaluation Estimands

Every result must identify one estimand from this table.

| ID | Question | Primary quantity | Intended interpretation |
|---|---|---|---|
| E0 | Does the metric associate with the target without metadata? | raw rank association and out-of-sample concordance | unconditional prediction |
| E1 | Does the metric improve prediction beyond baseline set B? | cross-validated delta in loss/concordance | incremental utility given B |
| E2 | Does that improvement transfer to unseen environments? | leave-one-environment-out delta | transportability |
| E3 | Does the metric predict direction under a matched intervention? | paired sign error and effect calibration | intervention consistency |
| E4 | Can the metric be measured reliably and affordably? | repeatability, batch sensitivity, runtime, memory | operational utility |

No result may be described as causal unless the metric itself is intervened on
or a separate identification argument is supplied.

## Targets

The project must keep these targets separate:

- final held-out performance, such as accuracy or negative log likelihood;
- generalization gap, defined from matched train and test risks;
- calibration error;
- robustness or out-of-distribution performance;
- early prediction of a later target.

The primary generalization-measure target is the generalization gap. Final
performance is a separate practical target. Models should either be trained to
a matched training-loss criterion or training fit must be included in the
baseline ladder.

## Baseline Ladder

Each metric is audited against all applicable levels. Results are not collapsed
into one universal pass/fail label.

| Level | Information available | Examples |
|---|---|---|
| B0 | task base rate only | dataset and evaluation target |
| B1 | pre-training design metadata | train size, architecture, parameter count, optimizer, log LR, log WD, dropout, compute budget |
| B2 | training-state baselines | train loss, train accuracy, elapsed steps, update norm |
| B3 | independent validation baselines | validation loss or accuracy on data disjoint from the final test set |

Seed identifiers are never treated as ordered numeric covariates. The design
uses repeated seeds within configurations; seed is a blocking/random-effect
variable for uncertainty and paired comparisons.

## Primary Statistical Method

### Cross-fitted nuisance adjustment

For target Y, metric M, and baseline information B:

1. split data by configuration or environment blocks;
2. fit a nonlinear model for E[Y | B] on training folds;
3. fit a nonlinear model for E[M | B] on training folds;
4. produce out-of-fold residuals for Y and M;
5. test residual dependence and report uncertainty;
6. separately compare out-of-sample prediction using B versus B plus M.

The default nuisance models will include spline/ridge and tree-based learners.
The selected ensemble and tuning grid must be frozen before the locked runs.
Linear partial rank correlation remains a descriptive baseline, not the primary
test.

### Primary outcomes

- change in leave-block-out concordance or pairwise ranking accuracy;
- change in cross-validated predictive loss;
- cross-fitted residual dependence with a permutation-calibrated p-value;
- paired sign error under controlled interventions;
- 95% block-bootstrap confidence intervals.

### Multiplicity

- metric-family hypotheses are primary;
- individual metric tests are secondary;
- false-discovery rate is controlled within each target and baseline level;
- exploratory analyses are labeled and never promoted after seeing holdout data.

### Practical significance

Thresholds will be defined on predictive improvement, not correlation alone.
The minimum relevant improvement will be frozen after pilot variance is known.
Point-estimate classes such as `survives` and `washout` may be retained for
visual summaries only when their confidence intervals support the label.

## Environment Definition

An environment is a declared combination of:

- dataset and split;
- task and target;
- architecture family;
- optimizer family;
- training-budget or stopping rule;
- augmentation regime;
- hyperparameter region.

Primary transport evaluation leaves out entire environments, not random rows.
Raw correlations are never pooled across incomparable target scales. Cross-task
summaries use within-environment ranks, standardized effect estimates, or
hierarchical models.

## Control Metrics

Every benchmark includes the following controls.

### Negative controls

- independent random metric;
- target-permuted metric within environment;
- metric from a randomly initialized model;
- noise added to a real metric at several signal-to-noise ratios.

### Deliberately deceptive controls

- hyperparameter-only nonlinear proxy;
- task-identity proxy;
- architecture-identity proxy;
- training-loss proxy;
- pooled-scale proxy designed to induce Simpson reversal;
- suppressor/collider simulation.

These controls provide ground truth about why a metric appears predictive and
allow direct comparison of audit protocols.

### Positive and oracle controls

- training loss and training accuracy;
- independent validation loss and validation accuracy;
- test loss, labeled explicitly as an oracle and never used as an ordinary
  deployable baseline.

## Metric Battery

The main table should contain approximately 12 to 18 mechanism-distinct metrics,
not dozens of monotonic variants.

Required families:

- task-proximal output and margin measures;
- parameter and path/distance measures;
- sharpness and adaptive sharpness;
- gradient magnitude and gradient-noise measures;
- empirical-Fisher magnitude and spectrum measures;
- Hessian curvature estimates;
- representation geometry;
- calibration/confidence diagnostics;
- FIM effective rank as the motivating case study.

Each metric requires a metric card recording:

- exact mathematical definition;
- source paper and implementation provenance;
- intended target and expected direction;
- required data and labels;
- checkpoint and batch protocol;
- invariances and known failure modes;
- runtime, peak memory, and missing-result rate;
- equivalence or monotonic duplication with other metrics.

Where practical, official author code is wrapped rather than reimplemented.
Approximate implementations are labeled and validated against the reference on
small models.

## Experimental Work Packages

### WP0: Legacy evidence audit

Purpose: convert v1 failures into documented motivation.

Deliverables:

- deduplicated configuration ledger;
- explicit exclusion of the leaky text experiment;
- corrected image analyses with train-loss baselines;
- flexible-control reanalysis of the 1,000-model MLP grid;
- a claim ledger separating valid pilot observations from withdrawn claims.

No v1 result is used as confirmatory evidence.

### WP1: Synthetic protocol calibration

Construct data-generating processes for:

- linear and nonlinear confounding;
- interactions and U-shaped effects;
- Simpson reversal;
- post-treatment control and suppression;
- null metrics, proxy metrics, and genuinely incremental metrics;
- environment-specific and transportable metrics.

Compare:

- raw Spearman and Kendall correlation;
- linear partial Spearman;
- Jiang-style conditional mutual information;
- granulated Kendall statistics;
- robust environment sign error;
- cross-fitted MBE 2.0.

Success requires calibrated null behavior and clear documentation of which
estimand each method answers.

### WP2: Retrospective public-corpus benchmark

Candidate sources include the PGDL corpus and released data/checkpoints from
large generalization-measure studies. Public data are preferred because they
provide independent environments and reduce new training cost.

Primary question: do metric rankings and verdicts change across E0-E3, and do
the deceptive controls expose weaknesses in existing evaluation procedures?

Outputs include a target-specific reliability atlas. PGDL Tasks 1-2 are
development, Tasks 4-5 are validation, and Tasks 6-9 are protected transfer
holdout. The selector protocol, features, and abstention rule must be frozen
before protected metric outputs are inspected.

### WP2b: Conditional selector calibration

Construct the selector from reliability profiles rather than raw pooled metric
rankings. Evaluate it with nested leave-one-task-family-out validation against
the comparators and decision outcomes frozen in
`CONDITIONAL_METRIC_RELIABILITY_PROTOCOL.md`.

This work package has two reporting modes:

- with fewer than 12 task families, report a feasibility study and atlas only;
- with at least 12 task families, report selector regret and abstention as a
  pilot, reserving broad claims for preferably 20 or more families.

Failure to outperform the globally best metric redirects the contribution to
the audit protocol and atlas; it does not justify post-hoc selector tuning on
the external holdout.

### WP3: Corrected image factorial

Minimum design:

- datasets: CIFAR-10 and CIFAR-100;
- architectures: ResNet-18, WideResNet-28-2, and ViT-Tiny or an equivalently
  reproducible small transformer;
- 8 frozen hyperparameter configurations per dataset/architecture;
- 5 seeds per configuration;
- total: 240 primary training runs.

Recommended design uses 12 configurations, for 360 runs.

Rules:

- fixed train, validation, metric, and final-test splits across runs;
- seed changes initialization and data order, not dataset membership;
- common fixed metric batches plus repeated batches for reliability;
- both fixed-budget and matched-training-loss checkpoints;
- configuration IDs, seed IDs, and run UUIDs are distinct;
- failures remain in the ledger with preregistered exclusion rules.

### WP4: Corrected causal text factorial

Minimum design:

- a causal Transformer with an explicit tested attention mask;
- a standard public language-modeling dataset such as WikiText-2;
- two model sizes;
- 10 frozen training configurations;
- 5 seeds per configuration;
- total: 100 primary runs.

Optional extension adds a text-classification environment or a third model size.
Perplexity or token negative log likelihood is primary; token accuracy is
secondary. No character-LM result from v1 is reused.

### WP5: Locked external holdout

The holdout environment is chosen and frozen before WP3/WP4 analysis is
unblinded. It must differ by dataset or task family and remain untouched during
method development.

Options:

- a public model corpus reserved in full;
- SVHN or CINIC-10 image runs;
- an independently generated text environment.

The preregistration, code commit, container digest, metric list, baseline ladder,
and primary analysis command are timestamped externally before launch.

## Reproducibility Requirements

Every run must record:

- immutable `config_id`, `seed_id`, `split_id`, `environment_id`, and `run_uuid`;
- git commit and container/environment digest;
- complete configuration and command;
- dataset and split hashes;
- metric implementation version and card ID;
- training curves and failure status;
- raw metric outputs before aggregation;
- elapsed GPU time and peak memory.

Paper tables must be regenerated from raw ledgers by one versioned command.
Missing controls must be fatal errors, not silently ignored.

## Decision Criteria

The main paper proceeds if all of the following hold:

1. MBE 2.0 is calibrated on synthetic null and proxy cases.
2. It answers a measurably different question from prior conditional and robust
   evaluation methods.
3. At least one result replicates across a new internal environment and the
   locked external holdout.
4. Negative and deceptive controls behave as preregistered.
5. Conclusions survive configuration/seed block uncertainty.
6. Metric-family findings are not driven by one implementation or missingness
   pattern.
7. Any automated-selection claim improves held-out task-family regret over the
   globally best metric and pooled raw-correlation selection.
8. Abstention quality is reported as coverage-risk or coverage-regret rather
   than a hand-picked confidence threshold.

The paper is redirected to a narrower venue if the method does not outperform
or clarify prior evaluation protocols. Negative metric results alone are not a
sufficient JMLR contribution.

## Intended Paper Structure

1. Metric utility is conditional on target, baseline, and environment.
2. Related evaluation and algorithm-selection frameworks.
3. MBE 2.0 and the conditional reliability profile.
4. Synthetic calibration and deceptive metrics.
5. Public-corpus reliability atlas.
6. Conditional selection and calibrated abstention.
7. Corrected image/text task families and locked external holdout.
8. FIM effective-rank self-falsification case study.
9. Measurement cost, reliability, missingness, and operational use.
10. Limitations, non-causal scope, and reporting recommendations.
