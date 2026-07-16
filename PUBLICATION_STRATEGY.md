# Publication Strategy: Conditional Metric Reliability

Status: revised 2026-07-16. The frozen technical specification is
`docs/CONDITIONAL_METRIC_RELIABILITY_PROTOCOL.md`.

## Recommended Narrative

The strongest paper is neither "metrics are lying" nor "we found the best
metric." It is:

> Metrics measure different properties, and even metrics aimed at the same
> target can change utility across tasks and information sets. Marginal
> Baseline Evaluation estimates that scope. We build a reliability atlas and
> test whether scoped evidence can select useful metrics for held-out task
> families while abstaining when it cannot.

MBE remains the central methodological contribution. FIM effective rank is the
motivating self-falsification case. The selector is a gated constructive
extension, not a guaranteed headline result.

## Claims We Should Make

1. A metric claim must name its target, baseline information, environment, and
   measurement protocol.
2. Metrics targeting generalization, robustness, calibration, optimization,
   and final performance do not belong on one universal leaderboard.
3. Raw pooled correlation cannot establish incremental utility or transport.
4. Redundancy with a cheap baseline narrows a metric's operational use; it does
   not prove that the measured quantity is meaningless.
5. A recommendation for a new task needs target-task evidence or calibrated
   transfer evidence.
6. Abstention is a valid and necessary selector output.

## Claims We Should Avoid

1. Do not call a metric universally good, bad, honest, or misleading.
2. Do not treat model rows as independent task-family evidence.
3. Do not claim robustness or calibration from a generalization-gap target.
4. Do not call the selector validated if it only succeeds on random model
   splits or eight development-contaminated tasks.
5. Do not imply conditional association is causal.
6. Do not promote private customer results into public evidence without
   consent, preregistration, and independent validation.

## Evidence Hierarchy

### Historical motivation

The 680-row legacy pilot is provenance and software-regression evidence. Its
text component is not valid causal-language-model evidence, and repeated runs
are not IID observations. Its washout and inversion examples motivate the
protocol but cannot support confirmatory claims.

### Calibrated method evidence

- synthetic null, proxy, nonlinear-confounding, Simpson, genuine-signal, and
  post-treatment cases;
- exact reproduction of published source statistics;
- explicit comparison between robust sign error and MBE incremental utility.

### Public reliability atlas

PGDL supplies 550 checkpoints over eight tasks with frozen development,
validation, and protected transfer roles. It supports a generalization-target
atlas and selector feasibility study. The 48-model pilot is implementation QA,
not inferential evidence.

### Broad selector evidence

The effective sample is task families. A selector pilot requires at least 12,
and the primary broad claim should preferably use 20 or more across targets,
datasets, architectures, and modalities. Evaluation is nested
leave-one-task-family-out with a locked external holdout.

## Paper Contribution Ladder

The paper remains viable at three outcome levels:

1. **MBE protocol:** calibrated distinction among association, incremental
   utility, transport, intervention consistency, and measurement reliability.
2. **Reliability atlas:** evidence that metric scope varies systematically
   across targets and environments.
3. **Conditional selector:** lower held-out-family regret than global and
   raw-correlation baselines, with calibrated abstention.

Failure at level 3 must be reported and does not erase levels 1-2. Failure at
level 2 substantially narrows the JMLR case.

## Required Headline Figures

1. estimand and baseline-ladder diagram;
2. synthetic calibration profiles;
3. published source statistic versus MBE estimand comparison;
4. task-by-metric reliability atlas;
5. sign/utility transport matrix;
6. selector regret against frozen baselines;
7. coverage-regret curve for abstention;
8. metric runtime, coverage, and cost frontier.

## Working Titles

- "Which Metric Should You Trust Here? Conditional Reliability Across ML Tasks"
- "Marginal Baseline Evaluation for Conditional Metric Reliability"
- "From Metric Leaderboards to Reliability Profiles"

Current working title:

> Which Metric Should You Trust Here? Conditional Reliability Across ML Tasks

## Decision

Build the atlas first. Fit the selector only from frozen development profiles.
Let held-out task-family regret determine whether metric selection is a primary
contribution, a limited tool, or a negative result.
