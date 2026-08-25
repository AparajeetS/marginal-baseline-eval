# Oracle Feasibility and Sample-Size Frontier

Status: frozen before simulation outcomes are inspected. This experiment uses
known-truth synthetic data only and does not authorize opening any protected
image, text, or PGDL metric-target association.

## Question

When MBE-style conditional metric tests fail at 24--48 independent
configurations, is the limiting factor (a) insufficient information in the
design, or (b) nuisance estimation? We separate those explanations by comparing
an optimistic latent-signal ceiling, an exact-nuisance observable oracle, and
learned nuisance estimators on the same generated datasets.

The oracle is not a deployable method and is not called a universal upper
bound. It is a design-specific diagnostic for the conditional covariance
estimand defined below.

## Estimand and Inference Unit

The estimand is the mean product of metric and target residuals after
conditioning on a declared baseline. Residuals are averaged within
configuration before multiplication. The independent inference unit is the
configuration, not the repeated row/seed.

All methods use a two-sided Student test of the configuration-level score and
require a positive score mean for positive support. Results are recorded at
both alpha 0.05 and alpha 0.001. The latter matches the strict threshold used
by the current prospective rule, but the asymptotic test here is a diagnostic,
not a replacement for its frozen wild-bootstrap inference.

## Frozen Design

- geometries: `image_like` and `text_like`;
- independent configurations: 24, 48, 96, and 192;
- repeated rows per configuration: 2;
- baseline ladders: `B1_design`, `B2_training_state`, and `B3_validation`;
- metric reliability levels: 0.30 and 0.80;
- known-null scenarios: independent, additive proxy, nonlinear proxy,
  interaction proxy, and heteroskedastic proxy;
- genuine shared-signal effects: 0.25 and 0.50;
- repetitions: 500 at 24 and 48 configurations, 250 at 96 and 192;
- fresh deterministic seeds, paired across baselines and methods;
- five grouped cross-fit folds for learned nuisance models.

The two geometries use different categorical factor supports and coefficients.
Factor combinations are deterministically balanced, then shuffled independently
within each repetition. The data generator exposes exact conditional means and
the latent shared signal. No protected empirical artifact is read.

## Methods

1. `latent_ceiling`: the true latent signal is observed and paired with the
   exact target residual. This is an optimistic information ceiling.
2. `observable_oracle`: exact conditional means are used for the observed noisy
   metric and target.
3. `learned_raw_d2`: raw outcomes are residualized by five-fold grouped
   cross-fitting with degree-2 pairwise-interaction ridge regression (ridge
   0.10).
4. `learned_rank_d2`: the existing MBE orthogonal rank-score implementation
   with the same nuisance family. Its Student p-value is used here so the full
   frontier is computationally feasible; previously frozen wild-bootstrap
   claims are unchanged.

## Frozen Gates

For every method, geometry, baseline, sample size, reliability, scenario, and
effect cell, report estimability, positive-support rate, and Wilson 95% interval.

A method/sample-size combination is **strictly calibrated** only if:

- estimability is at least 98% in every cell; and
- the maximum upper Wilson bound across all known-null cells is at most 7.5%
  at alpha 0.05.

It has **useful effect-0.50 power** only if the minimum lower Wilson bound across
all effect-0.50 cells is at least 50% at alpha 0.05.

Interpretation is frozen as follows:

- if the observable oracle lacks useful power while calibrated, the studied
  design/sample size is information-limited for this estimand;
- if the observable oracle passes but learned methods fail, nuisance estimation
  is a demonstrated bottleneck;
- if the latent ceiling passes but the observable oracle fails, measurement
  reliability/noise is a demonstrated bottleneck;
- no result authorizes opening protected associations or establishes general
  conditional independence.

