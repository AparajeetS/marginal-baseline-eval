# Dziugaite et al. (2020) MBE Results

## Status

Completed retrospective audit of all 32 published `complexity.*` columns. The
frozen source preparation retained 9,700 runs from 1,000 hyperparameter
configurations. Results use 199 permutation replicates, 499 configuration
bootstrap replicates, and seed 2026.

This is a complementary marginal-baseline analysis, not a reproduction of the
paper's distributionally robust sign-error analysis. It answers a different
question: does a measure retain information about generalization gap after an
additive, nonlinear baseline over the experimental design variables?

The source statistic has now also been independently reconstructed. It exactly
matches Figure 1's 9,242 environments, all five hyperparameter-specific counts,
the complete 24-measure ordering, and the reported maximum sign error of 1.0
for every measure. See `out/SOURCE_REPRODUCTION.md`.

## Source Statistic Versus MBE

The source mean sign-error ranking correlates strongly with raw association
(`rho = -0.747`), moderately with B1 cross-fitted residual association
(`-0.424`), and essentially not at all with out-of-fold Delta MSE (`-0.004`) or
relative MSE improvement (`0.015`). Lower source sign error is better, hence
the negative correlations with stronger associations.

This is not a contradiction. The source statistic tests directional robustness
under individual hyperparameter interventions. MBE tests information beyond a
marginal baseline across a population of configurations. A measure can be
incrementally informative while failing completely in one environment, and a
measure with good average directional error need not add useful out-of-sample
prediction beyond cheap controls.

## Primary Result: B1 Design Baseline

The baseline contains dataset, learning rate, model depth, model width, and
training-set size. Folds are grouped by the source `experiment_id`; residual
inference and uncertainty use the 1,000 configuration means.

- Frozen legacy MBE classification: 16 survive, 9 sign-invert, 2
  reverse-invert, 2 wash out, and 3 are weak or mixed.
- Configuration-level permutation tests: 31 of 32 are significant after
  Benjamini-Hochberg correction within the 32-measure family.
- Configuration bootstrap: the same 31 residual-association intervals exclude
  zero.
- Predictive increment: 29 of 32 have a positive 95% interval for out-of-fold
  Delta MSE; one is negative and two include zero.
- Cross-dataset stability: 19 measures have residual `|rho| >= 0.20` in both
  CIFAR-10 and SVHN. Only the two Frobenius-over-spectral ratios change sign,
  and both are close to zero within each dataset.

The strongest pooled residual associations are PAC-Bayes initialization
(`rho = 0.641`), PAC-Bayes magnitude flatness (`0.631`), Frobenius distance
(`0.590`), PAC-Bayes origin (`0.588`), and PAC-Bayes flatness (`0.580`).

`complexity.params` is the clear negative control: residual `rho = 0.038`,
BH-adjusted `q = 0.240`, and Delta MSE is negative with a 95% interval entirely
below zero. This is expected because depth and width already encode parameter
count.

Inverse margin is a practical washout despite a small detectable residual:
raw `rho = 0.616`, legacy partial `rho = 0.056`, configuration residual
`rho = 0.092`, and its Delta MSE interval includes zero. PAC-Bayes magnitude
origin also receives the legacy washout label, but its cross-fitted residual
and predictive increment remain positive; this disagreement is evidence that
the audit estimator matters.

## Direction Changes

Nine spectral/product measures have a negative pooled raw association but a
positive association after the B1 controls. These are not null results. They
show that pooled direction can be misleading when a measure and target both
vary strongly with the experimental design.

The two Frobenius-over-spectral ratios move from positive raw association to a
small negative conditional association. Their within-dataset residuals are
near zero; only the FFT variant changes sign across datasets. The pooled
reversal should therefore be treated as baseline sensitivity, not evidence of
a robust harmful direction.

## B2 Sensitivity

B2 adds cross-entropy, training accuracy, and epoch. It is deliberately strict:
training accuracy is part of the definition of generalization gap, so B2 is not
a causal adjustment set. Large B1-to-B2 changes demonstrate estimand
sensitivity and must not be used to select whichever result is most favorable.

## What This Study Supports

The result does not support a broad claim that established generalization
measures contain no incremental information. Most measures retain detectable
and often substantial information beyond the marginal design baseline.

It does support a narrower and more useful MBE claim: raw metric rankings can
hide washout, direction reversal, and dependence on the chosen baseline. A
metric paper should therefore disclose a frozen baseline ladder, grouped
out-of-sample increment, uncertainty at the independent unit, and environment
stability alongside raw association.

The synthetic calibration's joint heuristic (`|rho| >= 0.15` and
`Delta MSE >= 0.01`) is included only as a sensitivity lens because it was not
preregistered for this study. Under that stringent lens, only spectral
distance from initialization clears both cutoffs. The relative-improvement and
confidence columns in `out/reaudit.csv` should be used instead of turning that
post hoc observation into a universal threshold.

## Files

- Frozen protocol: `manifest.json`
- Full machine-readable results: `out/reaudit.csv`
- Full rendered table: `out/reaudit.md`
- Source preparation and provenance: `README.md` and
  `../../prepare_dziugaite2020.py`
