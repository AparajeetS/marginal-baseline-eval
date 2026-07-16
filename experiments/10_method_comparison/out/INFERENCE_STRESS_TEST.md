# Inference Stress Test

This known-truth matrix separates the refit predictive-improvement interval from the residual-permutation diagnostic.

## Refit Decisions

| n | Scenario | Nuisance | Joint support | Predictive support |
|---:|---|---|---:|---:|
| 100 | clustered_null | polynomial_ridge | 0.000 | 0.000 |
| 100 | clustered_null | polynomial_ridge_interactions | 0.000 | 0.000 |
| 100 | genuine_increment | polynomial_ridge | 1.000 | 1.000 |
| 100 | genuine_increment | polynomial_ridge_interactions | 1.000 | 1.000 |
| 100 | heteroskedastic_null | polynomial_ridge | 0.000 | 0.000 |
| 100 | heteroskedastic_null | polynomial_ridge_interactions | 0.000 | 0.000 |
| 100 | nonlinear_proxy | polynomial_ridge | 0.000 | 0.000 |
| 100 | nonlinear_proxy | polynomial_ridge_interactions | 0.000 | 0.050 |
| 100 | null_metric | polynomial_ridge | 0.000 | 0.000 |
| 100 | null_metric | polynomial_ridge_interactions | 0.000 | 0.000 |
| 200 | clustered_null | polynomial_ridge | 0.000 | 0.000 |
| 200 | clustered_null | polynomial_ridge_interactions | 0.000 | 0.000 |
| 200 | genuine_increment | polynomial_ridge | 1.000 | 1.000 |
| 200 | genuine_increment | polynomial_ridge_interactions | 1.000 | 1.000 |
| 200 | heteroskedastic_null | polynomial_ridge | 0.000 | 0.000 |
| 200 | heteroskedastic_null | polynomial_ridge_interactions | 0.000 | 0.000 |
| 200 | nonlinear_proxy | polynomial_ridge | 0.000 | 0.000 |
| 200 | nonlinear_proxy | polynomial_ridge_interactions | 0.000 | 0.000 |
| 200 | null_metric | polynomial_ridge | 0.000 | 0.000 |
| 200 | null_metric | polynomial_ridge_interactions | 0.000 | 0.000 |

## Residual-Permutation Nulls

| Structure | Rejections | Rate | Wilson 95% interval |
|---|---:|---:|---:|
| clustered | 35/500 | 0.070 | [0.051, 0.096] |
| heteroskedastic | 24/500 | 0.048 | [0.032, 0.070] |
| homoskedastic | 25/500 | 0.050 | [0.034, 0.073] |
| unequal_blocks | 29/500 | 0.058 | [0.041, 0.082] |

Residual permutation is retained as a diagnostic unless all relevant known-null structures are compatible with nominal error. The primary MBE decision is learner-relative predictive improvement under full refitting and preregistered nuisance-family agreement.
