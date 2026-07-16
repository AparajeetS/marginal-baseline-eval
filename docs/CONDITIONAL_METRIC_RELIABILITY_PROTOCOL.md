# Conditional Metric Reliability Protocol

Status: frozen research-direction amendment, 2026-07-16.

This document narrows and extends the MBE 2.0 program before full PGDL metric
extraction. It supersedes any language that treats a metric as universally
good, bad, surviving, or washed out without naming its target and environment.
The existing synthetic calibration, published-study reaudit, and 48-model PGDL
pilot motivated this amendment. Pilot correlations may motivate hypotheses but
cannot set selector thresholds or support confirmatory claims.

## Central Hypothesis

Metric reliability is conditional on a declared estimand, baseline information
set, environment, intervention family, and measurement protocol. A useful
system should therefore estimate where a metric is informative and abstain
when available evidence does not support a task-specific recommendation.

MBE remains the audit engine. The new research outputs are:

1. a metric reliability atlas across targets and environments;
2. a conditional selector that recommends a metric or small metric set;
3. an explicit abstention result when transport or sample evidence is weak.

The project does not assume that one scalar metric should dominate every task.

## Scope Before Comparison

Metrics enter the same comparison only when they address the same estimand.
The primary estimand groups are:

| Group | Example target | Example use |
|---|---|---|
| Generalization | train-test risk gap | compare fitted models with matched training fit |
| Final performance | held-out loss or accuracy | early model or configuration selection |
| Robustness | performance under a declared shift or perturbation | select models for a known deployment shift |
| Calibration | proper score or calibration error | assess confidence quality |
| Optimization | convergence, instability, or later training loss | monitor training dynamics |

A metric intended for robustness is not ranked against a generalization metric
unless both are evaluated against the same declared decision target. Direction
is specified separately for every metric-target pair.

## Reliability Profile

MBE produces a vector rather than a universal score. For metric `m`, target
`y`, baseline level `B`, and environment `e`, the profile records:

- incremental out-of-sample utility beyond `B`;
- residual association and uncertainty;
- expected direction and observed sign stability;
- transport performance in held-out environments;
- intervention consistency where matched interventions exist;
- repeatability across metric batches and seeds;
- coverage, runtime, memory, and required data access;
- implementation and provenance status.

The public atlas reports this vector. Any scalar used for operational selection
must declare a utility function and cost constraint; it is not presented as an
intrinsic metric quality score.

## Recommendation Levels

Every recommendation is assigned one evidence level.

| Level | Available evidence | Allowed output |
|---|---|---|
| L0 | no task outcomes and no validated related environments | abstain |
| L1 | transport evidence from related held-out task families | provisional recommendation with transfer uncertainty |
| L2 | sufficient historical runs from the target task | task-calibrated recommendation |
| L3 | target-task evidence plus independent temporal or external replication | validated operational recommendation |

The system must never silently describe an L1 transfer recommendation as L2 or
L3 evidence. For a new task with no outcomes, abstention is the default unless
the transport model is calibrated on held-out task families.

## Selector Inputs And Outputs

Required inputs:

- a target and estimand declaration;
- environment metadata available at decision time;
- a versioned metric battery and metric cards;
- baseline information available at the chosen decision point;
- historical run outcomes for L2/L3 recommendations;
- measurement-cost or access constraints when relevant.

Primary outputs:

- recommended metric or Pareto set;
- evidence level and compatible use case;
- incremental-utility interval at each baseline level;
- sign and transport stability;
- cost, coverage, and implementation warnings;
- abstention reason when no recommendation is supported.

## Frozen Selector Evaluation

The selector is evaluated by nested leave-one-task-family-out validation. All
models from the held-out dataset/task family remain outside selector fitting,
threshold selection, and calibration. Random model-level splitting is not a
valid transport test.

Primary decision metrics are:

1. selection regret relative to the task-specific oracle metric;
2. top-1 and top-k utility recovery;
3. sign-error rate on the held-out task family;
4. coverage-risk and coverage-regret curves for abstention;
5. calibration of predicted utility intervals;
6. added metric-computation cost at a fixed regret target.

Comparators are frozen as:

- globally best metric on training task families;
- metric selected by pooled raw correlation;
- metric selected by within-task raw correlation when target-task history is
  available;
- baseline-only prediction with no candidate metric;
- all eligible metrics with regularized stacking;
- task-specific oracle, used only as an upper bound;
- MBE reliability selector without abstention;
- MBE reliability selector with abstention.

Hyperparameters and abstention thresholds are selected inside the outer
training fold. Holdout task families cannot tune any component.

## Sample-Size Boundary

The unit of transport evidence is the task family, not the trained model. The
eight PGDL tasks are sufficient for a first reliability atlas and a limited
leave-one-task analysis, but not for claiming a generally learned metric
router. A broad selector claim requires at least 12 task families for a pilot
and preferably 20 or more for the primary analysis, spanning multiple datasets,
architectures, targets, and shift conditions.

Environments derived from one dataset are reported as correlated subgroups and
cannot be counted as fully independent task families.

## PGDL Execution Boundary

The PGDL sequence remains:

1. implement metrics on the frozen Tasks 1-2 pilot;
2. run all Tasks 1-2 development models;
3. freeze metric implementations, selector features, thresholds, and plots;
4. evaluate Tasks 4-5 once as validation;
5. evaluate Tasks 6-9 once as protected transfer holdout.

PGDL primary targets remain generalization-gap accuracy and the declared
secondary targets in `experiments/09_published_metric_reaudit/studies/pgdl2020/metric_plan.json`.
It cannot establish claims about robustness or calibration without additional
target-specific environments.

## Claim Rules

Allowed after suitable evidence:

- metric utility varies across environments and baseline information sets;
- MBE estimates conditional reliability for a declared target;
- a selector reduces held-out task-family regret relative to frozen baselines;
- abstention reduces decision risk at a stated coverage level.

Not allowed:

- a metric is universally good, bad, honest, or misleading;
- metric utility transfers merely because models share a broad modality;
- a recommendation from public-corpus transfer is validated for a customer's
  task without target-task evidence;
- a higher reliability score establishes causality;
- model-level sample size substitutes for task-family sample size.

## Decision Gate

The selector becomes a primary paper contribution only if it improves
leave-one-task-family-out regret over the globally best metric and pooled raw
correlation, while its abstention intervals are reasonably calibrated. If it
does not, the paper reports the reliability atlas and MBE audit protocol without
claiming successful automated metric selection.
