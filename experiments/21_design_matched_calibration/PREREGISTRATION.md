# Design-Matched Calibration Preregistration

Frozen on 2026-08-11 before any target-metric association from experiments 19
or 20 was computed or inspected.

## Purpose

This experiment selects nuisance learners using known-truth data with the exact
sample sizes, independent-unit structure, factor balance, baseline ladders,
and permutation blocks of the completed image and text artifacts. It is an
analysis-eligibility gate. It is not empirical evidence about any real metric.

The runner constructs both designs from their frozen grids. It has no input
for, and does not read, either protected result CSV.

## Frozen Designs

- Image: 96 rows, 48 configuration groups, two seeds, with architecture as the
  permutation block.
- Text: 48 rows, 24 configuration groups, two seeds, with model size as the
  permutation block. The three protected corpora have this same geometry and
  use the same selected family in separate environment-specific analyses.
- Baselines: design only; design plus final training-batch loss; and design,
  final training-batch loss, plus validation loss.

Synthetic training-state and validation variables are generated before the
target. A separate configuration-level latent variable controls the genuine
increment. Null scenarios set that increment to zero.

## Known-Truth Grid

Reliability levels are ICC 0.30 and 0.80. Null scenarios are independent,
additive proxy, nonlinear proxy, interaction proxy, and heteroskedastic proxy.
The positive scenario uses the interaction surface with standardized effects
0.20, 0.35, and 0.50. Every condition has 100 Monte Carlo repetitions.

Candidate learners were restricted using the prior generic complexity study:

- additive polynomial ridge at degrees 4 and 6;
- polynomial ridge with interactions at degrees 4 and 6;
- Extra Trees as a flexible comparator.

Degrees 1-3 are excluded because the completed generic proxy campaign found
severe false support in at least one nonlinear-proxy cell. This exclusion was
made before the protected GPU associations were opened.

## Stage 1: Screen

Screening uses grouped five-fold cross-fitting and 199 block permutations.
Point predictive support means positive out-of-fold Delta-MSE. Joint support
also requires a residual permutation p-value at or below 0.05.

A candidate advances within a design and baseline only when:

1. minimum estimability is at least 98%;
2. the largest null joint-support Wilson upper bound is at most 10%; and
3. minimum joint power at effect 0.50 is at least 20%.

At most two candidates advance. They are ranked by worst-case effect-0.50
joint power, then by the frozen complexity order shown in the script. Empty
selection means abstention; no candidate may be added manually.

## Stage 2: Confirm

Confirmation reruns every finalist with 199 grouped full-refit bootstrap draws
and 199 block permutations. A candidate is eligible only when:

1. minimum estimability is at least 95%;
2. the largest null predictive-support Wilson upper bound is at most 10%;
3. the largest null joint-support Wilson upper bound is at most 10%; and
4. the smallest effect-0.50 predictive-power Wilson lower bound is at least
   50%.

Among eligible candidates, the primary learner maximizes worst-case predictive
power at effect 0.35, with frozen complexity rank as the tie-breaker. All other
eligible learners are sensitivity analyses. If none is eligible, that design
and baseline abstains.

## Opening Rule

Protected associations may be opened for a design-baseline pair only after its
`FINAL_ELIGIBILITY.json` exists, passes structural validation, and is hashed.
The selected learner and every abstention are binding. Real metric results may
not be used to alter the scenarios, thresholds, candidate set, or ranking.

The later protected analysis must control multiplicity across metrics, retain
the random negative control, report all baseline levels, and keep image and
text environment claims separate. This calibration establishes learner
eligibility only; it does not establish causal identification or universal
error control.
