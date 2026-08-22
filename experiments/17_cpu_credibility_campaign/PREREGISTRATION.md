# CPU Credibility Campaign

Frozen before execution on 2026-07-29.

This campaign extends known-truth calibration and method comparison after the
observed-design power study. It does not add trained models and must not be
reported as additional model-scale evidence.

## A. Full-Refit Inference Stress

Eight independent shards, each with:

- 25 repetitions per cell, giving 200 pooled repetitions;
- sample sizes `72, 100, 150, 200, 300`;
- null metric, nonlinear proxy, heteroskedastic null, clustered null, and
  genuine increment scenarios;
- degree-6 polynomial ridge and polynomial ridge with interactions;
- 199 full-refit bootstrap draws and 199 residual permutations;
- 250 block-null repetitions per shard and 999 permutations, giving 2,000
  pooled repetitions for each block structure.

The primary summaries are predictive full-refit support and strict joint
support by scenario, nuisance family, and sample size. Residual-permutation
rejection is a secondary diagnostic. No unfavorable nuisance family may be
removed.

## B. Shared Method Comparison

Four independent 50-repetition shards, pooled to 200 repetitions, with five
seeds per factorial configuration, 999 permutations, and 999 bootstrap draws.
Every frozen scenario and every implemented comparator is retained.

## C. Generic Monte Carlo Calibration

Three parallel nuisance-family runs:

- polynomial ridge;
- polynomial ridge with interactions;
- Extra Trees.

Each uses sample sizes `100, 200, 400, 800`, degrees `2, 6`, 100 repetitions,
499 permutations, and 499 bootstrap draws. Degree is an inert label for the
Extra Trees learner but remains in the complete grid for direct output-shape
comparison.

## D. Public-Ledger Reproduction And Packaging

After one method-comparison lane completes, reproduce the Dziugaite et al.
source statistic, rerun the complementary MBE audit on the prepared public
ledger, and regenerate the source-versus-MBE comparison. A separate lane runs
the independent-replication dry run, package build, and test suite.

## Claim Boundary

These are protocol-calibration, software-reproduction, and comparator results.
They can identify false-positive behavior, power limitations, implementation
failures, and method disagreement in the specified designs. They cannot prove
universal calibration, metric invalidity, or cross-task generalization.

## Execution Amendment: 2026-07-29

The first eight inference-stress shards exited before simulation because
`make_calibration_ledger` enforces a minimum of 100 rows and the frozen grid
included `n=72`. No inference-stress result was produced or inspected. The
rerun removes only the invalid `n=72` cell and retains sample sizes
`100, 150, 200, 300`, all seeds, repetition counts, nuisance families, refit
draws, and permutation counts unchanged. The failed logs and exit statuses are
retained as provenance.
