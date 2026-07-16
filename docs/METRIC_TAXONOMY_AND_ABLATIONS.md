# Metric Taxonomy And Frozen Ablations

Status: paper-facing analysis plan, frozen before protected PGDL outcomes.

## Taxonomy

Metrics are grouped by mechanism and intended target, not by whether their pilot
result looked favorable.

| Family | Examples | Primary intended target | Mandatory warnings |
|---|---|---|---|
| Task-proximal | margin, confidence, entropy | final performance, calibration | may approximate validation performance |
| Optimization state | train loss, update norm, gradient noise | convergence, early prediction | often unavailable before training |
| Parameter geometry | weight norm, distance from initialization, path norm | generalization gap | parameterization sensitivity |
| Curvature and sharpness | Hessian trace, spectral estimates, adaptive sharpness | generalization gap, robustness | perturbation scale and normalization matter |
| Fisher and gradients | empirical-Fisher trace, effective rank, gradient norm | generalization gap, optimization | label choice and batch protocol matter |
| Representation geometry | feature rank, class separation, collapse measures | final performance, transfer | layer and data dependence |
| Calibration | ECE, Brier components, logit scale | calibration | cannot be ranked as generalization measures without a shared target |
| Robustness and shift | stability, domain discrepancy, perturbation response | declared shifted performance | shift-specific by construction |
| Controls | random, task ID, architecture ID, training-loss proxy | known null or deceptive case | never presented as candidate metrics |

Every metric card must name one primary target, expected direction, required
data, baseline availability, implementation source, invariances, cost, and
known failure modes.

## Primary Ablation Table

The paper reports the following rows for every major benchmark. No row may be
removed because it weakens the preferred narrative.

| ID | Analysis | Purpose |
|---|---|---|
| A0 | pooled raw Spearman/Kendall | reproduce ordinary metric evaluation |
| A1 | within-environment raw association | remove pooling artifacts |
| A2 | linear partial rank with design metadata | match a common conditional baseline |
| A3 | cross-fitted additive MBE with B1 metadata | test learner-relative increment |
| A4 | cross-fitted interaction MBE with B1 metadata | expose nuisance misspecification |
| A5 | A3/A4 plus B2 training-state controls | measure redundancy with cheap training signals |
| A6 | A3/A4 plus B3 independent validation controls | measure value beyond task-proximal validation |
| A7 | full-refit interval versus conditional-on-fit interval | quantify nuisance-fit uncertainty |
| A8 | row bootstrap versus configuration bootstrap | expose pseudoreplication |
| A9 | pooled versus leave-environment-out evaluation | test transport |
| A10 | all rows versus complete-case/common-coverage rows | test missingness effects |
| A11 | point estimate versus practical-significance gate | separate detectable from useful effects |

## Required Sensitivities

- fold count and repeated split seeds;
- nuisance regularization inside a frozen grid;
- rank-MSE and concordance targets;
- metric batch and checkpoint repeatability;
- architecture and dataset leave-one-family-out results;
- metric implementation provenance or official-code agreement;
- with and without each baseline-ladder level.

The primary result is the complete profile across these rows, not a count of
metrics declared alive or dead.
