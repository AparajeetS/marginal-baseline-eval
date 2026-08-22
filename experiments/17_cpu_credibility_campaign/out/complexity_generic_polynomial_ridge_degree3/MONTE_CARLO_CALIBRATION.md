# Repeated MBE Calibration

This is a repeated-simulation calibration of the compact polynomial-ridge MBE reference implementation. Conditional-null rows report empirical false-positive behavior; conditional-signal rows report power. The joint decision requires both a residual permutation rejection and a 95% out-of-fold Delta-MSE interval entirely above zero.

| Scenario | Signal expected | Nuisance | n | Degree | Repetitions | Legacy reject | Cross-fit reject [95% CI] | Joint decision [95% CI] | Median Delta MSE |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| `clustered_null` | false | polynomial_ridge | 100 | 3 | 100 | 0.400 | 0.110 [0.063, 0.186] | 0.000 [0.000, 0.037] | -0.0040 |
| `clustered_null` | false | polynomial_ridge | 200 | 3 | 100 | 0.360 | 0.110 [0.063, 0.186] | 0.000 [0.000, 0.037] | -0.0011 |
| `clustered_null` | false | polynomial_ridge | 400 | 3 | 100 | 0.340 | 0.040 [0.016, 0.098] | 0.000 [0.000, 0.037] | -0.0007 |
| `clustered_null` | false | polynomial_ridge | 800 | 3 | 100 | 0.350 | 0.030 [0.010, 0.085] | 0.000 [0.000, 0.037] | -0.0003 |
| `genuine_increment` | true | polynomial_ridge | 100 | 3 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0418 |
| `genuine_increment` | true | polynomial_ridge | 200 | 3 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0421 |
| `genuine_increment` | true | polynomial_ridge | 400 | 3 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0413 |
| `genuine_increment` | true | polynomial_ridge | 800 | 3 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0411 |
| `heteroskedastic_null` | false | polynomial_ridge | 100 | 3 | 100 | 0.200 | 0.060 [0.028, 0.125] | 0.000 [0.000, 0.037] | -0.0002 |
| `heteroskedastic_null` | false | polynomial_ridge | 200 | 3 | 100 | 0.230 | 0.050 [0.022, 0.112] | 0.000 [0.000, 0.037] | 0.0003 |
| `heteroskedastic_null` | false | polynomial_ridge | 400 | 3 | 100 | 0.360 | 0.020 [0.006, 0.070] | 0.000 [0.000, 0.037] | 0.0003 |
| `heteroskedastic_null` | false | polynomial_ridge | 800 | 3 | 100 | 0.560 | 0.160 [0.101, 0.244] | 0.140 [0.085, 0.221] | 0.0004 |
| `linear_proxy` | false | polynomial_ridge | 100 | 3 | 100 | 0.110 | 0.100 [0.055, 0.174] | 0.000 [0.000, 0.037] | -0.0006 |
| `linear_proxy` | false | polynomial_ridge | 200 | 3 | 100 | 0.050 | 0.030 [0.010, 0.085] | 0.000 [0.000, 0.037] | -0.0003 |
| `linear_proxy` | false | polynomial_ridge | 400 | 3 | 100 | 0.100 | 0.050 [0.022, 0.112] | 0.000 [0.000, 0.037] | -0.0002 |
| `linear_proxy` | false | polynomial_ridge | 800 | 3 | 100 | 0.060 | 0.040 [0.016, 0.098] | 0.000 [0.000, 0.037] | -0.0001 |
| `nonlinear_proxy` | false | polynomial_ridge | 100 | 3 | 100 | 1.000 | 0.500 [0.404, 0.596] | 0.430 [0.337, 0.528] | 0.0024 |
| `nonlinear_proxy` | false | polynomial_ridge | 200 | 3 | 100 | 1.000 | 0.740 [0.646, 0.816] | 0.740 [0.646, 0.816] | 0.0026 |
| `nonlinear_proxy` | false | polynomial_ridge | 400 | 3 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0026 |
| `nonlinear_proxy` | false | polynomial_ridge | 800 | 3 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0028 |
| `null_metric` | false | polynomial_ridge | 100 | 3 | 100 | 0.080 | 0.040 [0.016, 0.098] | 0.000 [0.000, 0.037] | -0.0008 |
| `null_metric` | false | polynomial_ridge | 200 | 3 | 100 | 0.110 | 0.070 [0.034, 0.137] | 0.000 [0.000, 0.037] | -0.0004 |
| `null_metric` | false | polynomial_ridge | 400 | 3 | 100 | 0.060 | 0.050 [0.022, 0.112] | 0.000 [0.000, 0.037] | -0.0002 |
| `null_metric` | false | polynomial_ridge | 800 | 3 | 100 | 0.050 | 0.050 [0.022, 0.112] | 0.000 [0.000, 0.037] | -0.0001 |
| `post_treatment_control` | false | polynomial_ridge | 100 | 3 | 100 | 0.050 | 0.070 [0.034, 0.137] | 0.000 [0.000, 0.037] | -0.0006 |
| `post_treatment_control` | false | polynomial_ridge | 200 | 3 | 100 | 0.100 | 0.070 [0.034, 0.137] | 0.000 [0.000, 0.037] | -0.0002 |
| `post_treatment_control` | false | polynomial_ridge | 400 | 3 | 100 | 0.060 | 0.060 [0.028, 0.125] | 0.000 [0.000, 0.037] | -0.0001 |
| `post_treatment_control` | false | polynomial_ridge | 800 | 3 | 100 | 0.050 | 0.030 [0.010, 0.085] | 0.000 [0.000, 0.037] | -0.0001 |
| `simpson_increment` | true | polynomial_ridge | 100 | 3 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0170 |
| `simpson_increment` | true | polynomial_ridge | 200 | 3 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0167 |
| `simpson_increment` | true | polynomial_ridge | 400 | 3 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0169 |
| `simpson_increment` | true | polynomial_ridge | 800 | 3 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0167 |

## Reading The Table

The nominal residual-test level is 0.050. A low null rejection rate supports calibration only for the simulated nuisance structures; it does not prove conditional independence testing is universally valid. Power must be interpreted together with sample size and nuisance degree.

Across the displayed grid, conditional-null cross-fit rejection ranges from 0.020 to 1.000; conditional-signal joint detection ranges from 1.000 to 1.000.

The post-treatment scenario is a conditional null for the direct-information estimand after controlling the mediator. Its raw association is real; loss of conditional signal is not a causal verdict.

This report calibrates one reference nuisance model. Submission evidence must add alternative nuisance learners, semi-synthetic real-design tests, and held-out task-family prediction.
