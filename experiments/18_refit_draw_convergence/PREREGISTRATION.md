# Paired Refit-Draw Convergence

Frozen before execution on 2026-07-29.

## Question

How stable are MBE full-refit interval decisions at 99, 199, and 499 bootstrap
draws relative to a paired 999-draw reference?

This is a Monte Carlo precision study. The 999-draw result is not ground truth,
and the study does not establish confidence-interval coverage outside the
named simulations.

## Frozen Design

- simulation source: `make_calibration_ledger`;
- sample size: 150;
- repetitions: 100;
- scenarios: null metric, nonlinear proxy, heteroskedastic null, clustered
  null, and genuine increment;
- nuisance families: polynomial ridge and polynomial ridge with interactions;
- refit draws: 99, 199, 499, and 999;
- residual permutations: 199;
- degree: 6;
- seed: `20260731`.

Each repetition, scenario, and nuisance family uses the same simulated data
and analysis seed at every draw count. This makes draw-count comparisons
paired. No setting may be dropped because it is unfavorable.

## Outputs

Primary summaries are:

1. predictive-support and joint-support rates by draw count;
2. paired predictive-decision agreement with the 999-draw reference;
3. positive-to-negative and negative-to-positive flip rates;
4. absolute movement in the refit lower confidence bound.

The choice of a package default must consider stability, null behavior, power,
and runtime. It may not be chosen solely to maximize positive findings.
