# Statistical Estimand And Inference

Status: calibration-amended MBE 2.0 statistical specification, 2026-07-29.

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

## Historical Frozen Decision Rule

The 2026-07-16 rule called a metric-target-baseline cell
`increment-supported` only when:

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

This rule remains the immutable analysis rule for experiments already frozen
under it. It is not eligible for new confirmatory experiments without
amendment. In the 36-configuration observed-design calibration, the
interaction family had only 1.0%-4.6% power at the largest injected effect
across degrees 1-6. Mandatory agreement therefore had at most 4.6% power even
though the additive family recovered 98.2%-100% of the same large effects.
Reducing degree did not repair the interaction veto.

## Prospective Calibration-Gated Rule

Before any new protected outcome is inspected:

1. candidate nuisance families and complexity grids are frozen;
2. each family is tested on named null/proxy controls and injected signals
   matched to the target design and independence structure;
3. eligibility thresholds for false support, power, estimability, and
   practical effect size are frozen from those known-truth simulations;
4. real-metric inference is run only for eligible families;
5. `increment-supported` requires a full-refit 95% interval for `Delta_L`
   above zero, direction agreement, and agreement among all eligible frozen
   families;
6. if no family is eligible, or eligible families disagree, MBE abstains.

This amendment removes the circular requirement that an empirically
underpowered family must veto every conclusion. It does not permit choosing a
family because it favors a real metric. The exact eligibility thresholds must
be preregistered before the next protected experiment.

## Residual Dependence

Cross-fitted residual rank dependence and its within-environment permutation
p-value are secondary diagnostics. They can reveal remaining dependence that
does not improve the chosen learner, but they are not required for the primary
increment decision.

This demotion is evidence-driven. In the expanded 2,000-repetition block-null
study, residual permutation rejected 6.95% of clustered nulls, 5.30% of
heteroskedastic nulls, 7.05% of homoskedastic nulls, and 7.25% of
unequal-block nulls. Three Wilson intervals excluded the nominal 5% level.

The separate full-refit stress matrix contained 6,400 null/proxy rows and
1,600 genuine-increment rows across sample sizes 100-300. Predictive false
support was 0.25%, joint false support was 0.125%, and predictive recovery was
100%. These finite results support the predictive interval for the named
designs but are not a universal coverage guarantee.

## Uncertainty And Multiplicity

- Bootstrap independent configurations and refit folds and nuisance models in
  every draw.
- Report intervals separately for every eligible nuisance family before
  applying the agreement rule.
- Use at least 499 full-refit draws for publication-quality decisions near
  zero. A paired convergence study found 499/499 decisions agreed with a
  999-draw reference, while 199 draws had up to 3% disagreement in one
  borderline proxy cell.
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
