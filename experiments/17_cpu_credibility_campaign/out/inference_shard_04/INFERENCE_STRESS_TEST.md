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
| 100 | nonlinear_proxy | polynomial_ridge_interactions | 0.000 | 0.040 |
| 100 | null_metric | polynomial_ridge | 0.000 | 0.000 |
| 100 | null_metric | polynomial_ridge_interactions | 0.000 | 0.000 |
| 150 | clustered_null | polynomial_ridge | 0.000 | 0.000 |
| 150 | clustered_null | polynomial_ridge_interactions | 0.000 | 0.000 |
| 150 | genuine_increment | polynomial_ridge | 1.000 | 1.000 |
| 150 | genuine_increment | polynomial_ridge_interactions | 1.000 | 1.000 |
| 150 | heteroskedastic_null | polynomial_ridge | 0.000 | 0.000 |
| 150 | heteroskedastic_null | polynomial_ridge_interactions | 0.000 | 0.000 |
| 150 | nonlinear_proxy | polynomial_ridge | 0.000 | 0.000 |
| 150 | nonlinear_proxy | polynomial_ridge_interactions | 0.000 | 0.000 |
| 150 | null_metric | polynomial_ridge | 0.000 | 0.000 |
| 150 | null_metric | polynomial_ridge_interactions | 0.000 | 0.000 |
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
| 300 | clustered_null | polynomial_ridge | 0.000 | 0.000 |
| 300 | clustered_null | polynomial_ridge_interactions | 0.000 | 0.000 |
| 300 | genuine_increment | polynomial_ridge | 1.000 | 1.000 |
| 300 | genuine_increment | polynomial_ridge_interactions | 1.000 | 1.000 |
| 300 | heteroskedastic_null | polynomial_ridge | 0.000 | 0.000 |
| 300 | heteroskedastic_null | polynomial_ridge_interactions | 0.000 | 0.000 |
| 300 | nonlinear_proxy | polynomial_ridge | 0.000 | 0.000 |
| 300 | nonlinear_proxy | polynomial_ridge_interactions | 0.000 | 0.000 |
| 300 | null_metric | polynomial_ridge | 0.000 | 0.000 |
| 300 | null_metric | polynomial_ridge_interactions | 0.000 | 0.000 |

## Residual-Permutation Nulls

| Structure | Rejections | Rate | Wilson 95% interval |
|---|---:|---:|---:|
| clustered | 20/250 | 0.080 | [0.052, 0.120] |
| heteroskedastic | 11/250 | 0.044 | [0.025, 0.077] |
| homoskedastic | 20/250 | 0.080 | [0.052, 0.120] |
| unequal_blocks | 18/250 | 0.072 | [0.046, 0.111] |

Residual permutation is retained as a diagnostic unless all relevant known-null structures are compatible with nominal error. The primary MBE decision is learner-relative predictive improvement under full refitting and preregistered nuisance-family agreement.
