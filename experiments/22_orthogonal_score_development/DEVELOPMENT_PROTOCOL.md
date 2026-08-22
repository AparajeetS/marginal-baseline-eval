# Development Protocol: Conditional Rank Score

Status: iterative development protocol. V1 was recorded on 2026-08-11 before
its output and failed. V2 was recorded after that diagnostic and before V2
output. Neither version is an opening gate for protected associations.

## Motivation

Experiment 21 completed 48,000 known-truth cells and selected zero finalists.
High-power nuisance learners over-supported several nulls, especially the
heteroskedastic proxy null. Interaction-rich learners reduced false support but
lost useful power at 24 and 48 independent configurations. That abstention is
binding and remains part of the scientific record.

The replacement separates two questions:

1. Is there nonzero conditional rank covariance after cross-fitted adjustment?
2. Does a prespecified learner gain out-of-sample predictive accuracy from the
   metric?

This experiment addresses only the first question. It cannot establish causal
effect, arbitrary conditional independence, or universal metric usefulness.

## Designs And Truth Grid

The simulator and factor grids are imported unchanged from experiment 21 and
their source hash is recorded. Image uses 48 configurations with two seeds;
text uses 24 configurations with two seeds. All three baseline ladders, two ICC
levels, five null scenarios, and signal effects 0.20, 0.35, and 0.50 are kept.

V2 candidate nuisance models are additive polynomial ridge at degrees 4 and 6,
degree-4 polynomial ridge with pairwise interactions, and Extra Trees. Ridge
penalties 0.1, 1, and 10 are examined where specified in the runner. Five-fold
assignment is grouped by configuration. Inference multiplies the two
configuration-mean residuals and uses a two-sided studentized Rademacher
multiplier bootstrap. Synthetic seeds are paired across candidates and
baselines. The development decision threshold is 0.005, selected after V1 and
recorded before V2.

## Development Diagnostic

For each scope, baseline, and candidate:

- minimum estimability must be at least 98%;
- the largest null-support Wilson 95% upper bound must be at most 10%;
- the smallest positive-power Wilson 95% lower bound at effect 0.50 must be at
  least 50%.

These thresholds describe a candidate worth confirming. They do not confer
eligibility because candidate choice occurs after seeing development output.

## Confirmation Boundary

After development, any candidate taken forward must be named in a new frozen
confirmation preregistration. That document must fix untouched seeds, 100
repetitions per cell, bootstrap draws, all thresholds, comparators, and the
opening rule before confirmation starts. Failure or abstention is retained.
Protected associations remain closed until that independent confirmation
passes and its complete artifacts and hashes exist.
