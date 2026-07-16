# Statistical Estimand And Inference

Status: primary MBE 2.0 statistical specification, 2026-07-16.

## Estimand

For target `Y`, metric `M`, baseline information `B`, environment `E`, and a
preregistered nuisance learner class `L`, MBE estimates learner-relative
incremental predictive utility:

`Delta_L = Risk_L(Y | B) - Risk_L(Y | B, M)`.

Risk is evaluated out of fold with configurations, not rows, as the independent
split unit. Positive `Delta_L` means that the metric improves prediction for the
declared learner and baseline set. It does not establish that `M` contains
information unavailable to every possible learner, and it does not identify a
causal effect of the metric.

The primary scale is rank-target mean squared error. Pairwise concordance is a
preregistered sensitivity because a metric may improve ordering without
improving squared-error calibration.

## Primary Decision Rule

A metric-target-baseline cell is `increment-supported` only when:

1. the full-refit configuration bootstrap gives a 95% interval for `Delta_L`
   strictly above zero;
2. the result is supported by both eligible nuisance families: degree-6 bounded
   polynomial ridge and degree-6 bounded polynomial ridge with pairwise
   interactions;
3. the direction agrees with the frozen metric card;
4. at least 30 independent configurations are available; and
5. no leakage, target-proxy, missingness, or implementation gate requires
   abstention.

Disagreement between nuisance families is reported as `nuisance-sensitive`.
Failure to reject is not evidence that a metric is intrinsically useless.

## Residual Dependence

Cross-fitted residual rank dependence and its within-environment permutation
p-value are secondary diagnostics. They can reveal remaining dependence that
does not improve the chosen learner, but they are not required for the primary
increment decision.

This demotion is evidence-driven. In the frozen inference stress test, residual
permutation was compatible with nominal 5% behavior for ordinary,
heteroskedastic, and unequal-block nulls, while a clustered null rejected 7.0%
of 500 repetitions. The full-refit predictive interval made one false support
across 320 null/proxy cells and recovered all 80 injected-signal cells. These
finite results justify the current operational rule but not a universal
coverage guarantee.

## Uncertainty And Multiplicity

- Bootstrap independent configurations and refit folds and nuisance models in
  every draw.
- Report intervals separately for every nuisance family before applying the
  agreement rule.
- Control false discovery rate within each target, environment, and baseline
  level for secondary residual-dependence tests.
- Report task-family effects individually before any pooled summary.
- Use environment-level or task-family resampling for transport claims.

## Assumptions

The interpretation requires:

- the target and baseline variables are measured without target leakage;
- folds isolate the declared independent unit;
- the baseline information is available at the stated decision time;
- the nuisance families approximate relevant baseline structure sufficiently
  for the scoped learner-relative claim;
- bootstrap groups capture the material dependence;
- missing metric values are not selected using target favorability.

Violation of an assumption narrows the estimand or triggers abstention. MBE does
not infer the correct causal adjustment set automatically.

## Practical Significance

Statistical support and practical usefulness are separate. Before protected
evaluation, each target freezes a minimum relevant relative risk improvement
and a measurement-cost budget. Effects below that threshold may be statistically
supported but are labeled operationally negligible.
