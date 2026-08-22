# MBE Calibration Evidence Summary

Status: known-ground-truth and semi-synthetic evidence only. This does not validate real checkpoint metrics or unseen-task transport.

## Main Findings

- Degree-2 polynomial nuisance adjustment fails the generic proxy stress tests: joint false-decision rates span 0.000-1.000 across conditional-null cells.
- Degree-6 polynomial adjustment reduces the same conditional-null joint-decision range to 0.000-0.010 while conditional-signal power spans 1.000-1.000.
- On PGDL Tasks 1-2 real design geometry, null/proxy joint decisions span 0.000-0.070 and injected/task-specialist recovery spans 0.980-1.000.
- Opposite-sign task specialists are recovered within each task and rejected as one stable metric in the balanced pool, supporting task-specific reliability reporting.

## Nuisance Sensitivity

| Source | Nuisance | Conditional-null joint decisions | Signal joint decisions |
|---|---|---:|---:|
| Generic simulation | polynomial degree 2 | 0.000-1.000 | 1.000-1.000 |
| Generic simulation | polynomial degree 6 | 0.000-0.010 | 1.000-1.000 |
| PGDL semi-synthetic | polynomial degrees 2/4/6 | 0.000-0.070 | 0.980-1.000 |

## Refit-Aware Inference

Across 6400 null/proxy rows, the maximum cell-level predictive-interval support rate was 3.0% and the maximum joint support rate was 2.5%. Predictive support recovered 1600/1600 injected-signal rows and joint support recovered 1597/1600. Residual-permutation rejection was 7.05% for the ordinary null and 6.95% for the clustered null. The full-refit predictive interval is the primary uncertainty path for prospectively calibrated nuisance families; residual permutation is diagnostic.

## Nuisance-Complexity And Power

Across degrees 1-3, at least one generic null/proxy cell reached 100.0% false support. Degree 6 reduced the worst generic rates to 0.0%-3.0%, but interaction-family power at beta=0.5 was only 1.0%-4.6% in the 36-configuration observed design. The original mandatory consensus is therefore underpowered in that geometry and cannot support substantive null conclusions.

## What This Changes

Low-degree polynomial fits, the tested Extra Trees configuration, anti-conservative residual permutation, and the underpowered universal consensus are documented failure controls. Future real-metric reporting must calibrate nuisance-family eligibility before protected outcomes, use repeated cross-fitting and full-refit interval-supported predictive improvement, and keep residual dependence separate. Learner disagreement is a result, not permission to select the favorable model.

## Remaining Gates

- extend full-refit calibration to more effect sizes and task-like dependence structures;
- expand the shared CMI/granulated benchmark and add a formally calibrated conditional-independence comparator;
- complete PGDL Tasks 1-2 real metric extraction;
- freeze and execute Tasks 4-5 validation and Tasks 6-9 transfer once;
- run prospective selection and independent replication.
