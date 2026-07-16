# Paper Skeleton

Working title:

> Which Metric Should You Trust Here? Conditional Reliability Across ML Tasks

Status: revised scaffold, 2026-07-16. This is not final prose. The selector is
a gated contribution and must be removed from the headline if it does not beat
the frozen baselines on held-out task families.

## Abstract

Problem:

Machine-learning metrics are commonly compared as if predictive value were an
intrinsic property. In practice, a metric may target generalization,
robustness, calibration, optimization, or final performance, and its apparent
utility can change with the task, available baseline information, and
evaluation environment.

Proposed contribution:

Marginal Baseline Evaluation (MBE) estimates a conditional reliability profile
for a metric-target-environment tuple. The profile separates unconditional
association, incremental predictive utility, transport, intervention
consistency, repeatability, and measurement cost. We use these profiles to
construct a metric reliability atlas and test an abstaining selector that
recommends metrics only when its evidence is calibrated for the requested task.

Evidence required for the final abstract:

- synthetic null, proxy, confounding, and transport calibration;
- exact reproduction and reaudit of published metric evaluations;
- PGDL development, validation, and protected-task results;
- corrected image/text task families;
- leave-one-task-family-out selection regret and coverage-regret;
- one locked external holdout.

No numerical selector claim enters the abstract before the protected analysis.

## 1. Introduction

Central claim:

> Metric utility is conditional on what is being predicted, what information
> is already available, and where the metric will be used.

Motivation:

- metrics aimed at different targets are often discussed on one informal
  good-to-bad axis;
- pooled correlation can reward task identity, architecture, hyperparameters,
  or training state;
- conditioning can reveal redundancy without proving that the measured
  quantity is meaningless;
- a metric useful in one task may weaken or reverse in another;
- users need scoped recommendations and honest abstention, not another
  universal leaderboard.

Contributions, in priority order:

1. MBE as an estimand-explicit audit protocol;
2. a target- and environment-specific metric reliability atlas;
3. a gated conditional selector with calibrated abstention;
4. FIM effective rank as a good-faith self-falsification case study;
5. open metric cards, ledgers, protocols, and reproduction software.

## 2. Related Work

Required groups:

- generalization-measure evaluation and PGDL;
- conditional mutual information and granulated rank evaluation;
- robust environment sign error and worst-case comparisons;
- algorithm selection, meta-learning, and learning to rank;
- selective prediction, abstention, and uncertainty calibration;
- multi-objective and cost-aware model selection;
- sharpness, PAC-Bayes, Fisher, gradient, margin, representation, calibration,
  and robustness metric families.

Novelty boundary:

MBE does not claim that conditioning, cross-fitting, algorithm selection, or
abstention is individually new. The contribution must be the calibrated
combination of explicit estimands, baseline ladders, environment transport,
deceptive controls, reliability profiles, and selection evaluation.

## 3. Problem Definition

Define:

- target or estimand `y`;
- candidate metric `m`;
- baseline information set `B`;
- environment `e`;
- decision-time measurement cost `c(m)`;
- metric eligibility and expected direction for each target;
- task family as the outer unit of transport.

Targets remain separate:

- generalization gap;
- final held-out performance;
- robustness under a declared shift;
- calibration under a proper score;
- optimization or early-training prediction.

The project does not define an intrinsic scalar quality for a metric.

## 4. MBE Reliability Profiles

### 4.1 Baseline ladder

- B0: task base rate;
- B1: pre-training design metadata;
- B2: training-state information;
- B3: independent validation information.

### 4.2 Estimands

- E0: unconditional association;
- E1: incremental out-of-sample utility;
- E2: transport to held-out environments;
- E3: matched-intervention consistency;
- E4: repeatability and operational cost.

### 4.3 Estimation

- grouped cross-fitting;
- nonlinear nuisance adjustment;
- paired predictive-loss and ranking deltas;
- within-environment permutation;
- configuration/task-family bootstrap;
- multiplicity control within target and baseline level;
- missingness and measurement-cost reporting.

Output is a reliability vector with uncertainty, not `good` or `bad`.

## 5. Conditional Metric Selection

### 5.1 Evidence levels

- L0: no defensible evidence, abstain;
- L1: calibrated transfer evidence from related task families;
- L2: target-task historical evidence;
- L3: target-task evidence plus independent replication.

### 5.2 Selector

The selector receives a declared target, environment metadata, baseline level,
eligible metrics, reliability profiles, and optional cost constraints. It
returns one metric, a Pareto set, or abstention with a reason.

Start with a transparent reliability rule. Learned routing is secondary and
must demonstrate that it is not memorizing dataset or architecture identity.

### 5.3 Evaluation

Use nested leave-one-task-family-out validation. Report:

- selection regret against the task-specific oracle upper bound;
- top-k utility recovery;
- sign error;
- predictive-interval calibration;
- coverage-risk and coverage-regret under abstention;
- metric cost at a fixed regret target.

Frozen comparisons:

- globally best metric;
- pooled raw-correlation selector;
- within-task raw correlation where target history is available;
- baseline-only prediction;
- regularized stacking of all eligible metrics;
- selector without abstention;
- selector with abstention.

## 6. Protocol Calibration

Use synthetic cases with known answers:

- null metric;
- hyperparameter proxy;
- genuine incremental signal;
- nonlinear confounding;
- Simpson reversal;
- post-treatment or suppressor control;
- environment-specific signal;
- transportable signal;
- misleading selector confidence and required abstention.

Compare MBE with raw rank association, linear partial rank correlation,
conditional mutual information, granulated Kendall measures, and robust sign
error. Explain which estimand each method answers rather than declaring one
universal winner.

Current artifact:

- `experiments/08_protocol_calibration/out/CALIBRATION_REPORT.md`.

## 7. Published-Study Reaudit

### 7.1 Dziugaite et al.

Reproduce the source statistic over all 9,242 directed environments and its
published environment counts. Compare source robust sign error with MBE
incremental utility.

Interpretation boundary:

Worst-case sign robustness and average incremental prediction are distinct
properties. Disagreement is not evidence that one calculation is wrong.

### 7.2 Artifact availability

Document unavailable run-level data, including the Jiang et al. intake, without
reconstructing pseudo-runs from rounded paper tables or treating unavailable
artifacts as negative scientific results.

## 8. Public Reliability Atlas

Primary public corpus: PGDL, 550 models across eight tasks.

- Tasks 1-2: development;
- Tasks 4-5: validation;
- Tasks 6-9: protected transfer holdout.

Primary target: accuracy generalization gap. Secondary targets remain separate.

Required outputs:

- task-by-metric reliability profiles;
- baseline-ladder ablation;
- sign and rank stability;
- transport and missingness;
- runtime and memory;
- source-style pairwise comparisons;
- uncertainty and multiplicity correction.

The frozen 48-model pilot is implementation QA only. Its correlations may not
define thresholds or headline results.

## 9. New Task Families

Add corrected image and causal-text environments, then robustness and
calibration targets where resources permit. Dataset/architecture subgroups are
correlated environments, not automatically independent task families.

Broad routing claims require at least 12 task families for a pilot and
preferably 20 or more for the primary analysis. Cross-modality transfer should
often produce abstention; it is not assumed to work.

## 10. Motivating Case Study: FIM Effective Rank

Tell the self-falsification story precisely:

1. FIM effective rank passed ordinary metric checks;
2. MBE exposed dependence on task, pooling, and baseline choice;
3. the result motivated conditional reliability rather than a universal metric
   verdict;
4. the same audit is applied to established metrics without privileging the
   proposed measure.

CEI-R remains exploratory and cannot set audit thresholds or selector design.

## 11. Results And Decision Gates

The selector is a primary result only if it:

- beats the globally best metric and pooled-correlation selector on held-out
  task-family regret;
- provides reasonably calibrated utility intervals;
- reduces regret as it abstains more;
- survives simple-feature and task-identity ablations;
- transfers to the locked holdout without threshold changes.

Otherwise, report the negative selector result and retain MBE plus the atlas as
the contribution.

## 12. Limitations

State plainly:

- conditional prediction is not causality;
- task families, not model rows, determine transport sample size;
- reliability depends on the declared metric implementation and measurement
  protocol;
- a recommendation requires historical outcomes or validated transfer;
- robustness and calibration claims require their own targets;
- the atlas cannot cover every architecture, dataset, or deployment shift;
- a paid audit cannot certify safety or future performance.

## 13. Reproducibility And Governance

Release:

- raw ledgers and hashes where licensing permits;
- metric cards and implementation provenance;
- frozen split and environment manifests;
- selector configurations and abstention rules;
- one-command table regeneration;
- package, notebook, and archival snapshot;
- all deviations and negative results.

Commercial services must not receive access to protected research holdouts or
change public benchmark thresholds. Private customer data remain outside the
public research evidence unless separately consented, de-identified, and
preregistered.

## 14. Conclusion

The desired conclusion is not that metrics lie. It is that metric evidence has
a scope. MBE makes that scope measurable, the atlas makes it inspectable, and
the selector tests whether scoped evidence can improve real metric choices
without pretending uncertainty has disappeared.

## Immediate Tasks

1. Finish PGDL data-dependent metric implementations on the frozen pilot.
2. Freeze every metric card and development analysis command.
3. Run all Tasks 1-2 development checkpoints.
4. Implement selector baselines and abstention calibration without protected
   task outputs.
5. Run Tasks 4-5 validation once.
6. Expand independent task-family coverage before broad selector claims.
7. Timestamp the final protocol before Tasks 6-9 metric extraction.
