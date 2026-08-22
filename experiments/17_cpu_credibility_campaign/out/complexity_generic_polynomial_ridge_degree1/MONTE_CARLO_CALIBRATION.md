# Repeated MBE Calibration

This is a repeated-simulation calibration of the compact polynomial-ridge MBE reference implementation. Conditional-null rows report empirical false-positive behavior; conditional-signal rows report power. The joint decision requires both a residual permutation rejection and a 95% out-of-fold Delta-MSE interval entirely above zero.

| Scenario | Signal expected | Nuisance | n | Degree | Repetitions | Legacy reject | Cross-fit reject [95% CI] | Joint decision [95% CI] | Median Delta MSE |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| `clustered_null` | false | polynomial_ridge | 100 | 1 | 100 | 0.410 | 0.070 [0.034, 0.137] | 0.010 [0.002, 0.054] | -0.0011 |
| `clustered_null` | false | polynomial_ridge | 200 | 1 | 100 | 0.420 | 0.060 [0.028, 0.125] | 0.000 [0.000, 0.037] | -0.0005 |
| `clustered_null` | false | polynomial_ridge | 400 | 1 | 100 | 0.350 | 0.110 [0.063, 0.186] | 0.000 [0.000, 0.037] | -0.0003 |
| `clustered_null` | false | polynomial_ridge | 800 | 1 | 100 | 0.350 | 0.070 [0.034, 0.137] | 0.000 [0.000, 0.037] | -0.0001 |
| `genuine_increment` | true | polynomial_ridge | 100 | 1 | 100 | 1.000 | 0.990 [0.946, 0.998] | 0.990 [0.946, 0.998] | 0.0407 |
| `genuine_increment` | true | polynomial_ridge | 200 | 1 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0416 |
| `genuine_increment` | true | polynomial_ridge | 400 | 1 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0401 |
| `genuine_increment` | true | polynomial_ridge | 800 | 1 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0408 |
| `heteroskedastic_null` | false | polynomial_ridge | 100 | 1 | 100 | 0.100 | 0.040 [0.016, 0.098] | 0.000 [0.000, 0.037] | -0.0005 |
| `heteroskedastic_null` | false | polynomial_ridge | 200 | 1 | 100 | 0.180 | 0.010 [0.002, 0.054] | 0.000 [0.000, 0.037] | -0.0002 |
| `heteroskedastic_null` | false | polynomial_ridge | 400 | 1 | 100 | 0.350 | 0.130 [0.078, 0.210] | 0.000 [0.000, 0.037] | 0.0000 |
| `heteroskedastic_null` | false | polynomial_ridge | 800 | 1 | 100 | 0.570 | 0.180 [0.117, 0.267] | 0.030 [0.010, 0.085] | 0.0003 |
| `linear_proxy` | false | polynomial_ridge | 100 | 1 | 100 | 0.070 | 0.060 [0.028, 0.125] | 0.000 [0.000, 0.037] | -0.0002 |
| `linear_proxy` | false | polynomial_ridge | 200 | 1 | 100 | 0.100 | 0.070 [0.034, 0.137] | 0.000 [0.000, 0.037] | -0.0001 |
| `linear_proxy` | false | polynomial_ridge | 400 | 1 | 100 | 0.090 | 0.020 [0.006, 0.070] | 0.000 [0.000, 0.037] | -0.0000 |
| `linear_proxy` | false | polynomial_ridge | 800 | 1 | 100 | 0.090 | 0.030 [0.010, 0.085] | 0.000 [0.000, 0.037] | -0.0000 |
| `nonlinear_proxy` | false | polynomial_ridge | 100 | 1 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0778 |
| `nonlinear_proxy` | false | polynomial_ridge | 200 | 1 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0761 |
| `nonlinear_proxy` | false | polynomial_ridge | 400 | 1 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0761 |
| `nonlinear_proxy` | false | polynomial_ridge | 800 | 1 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0756 |
| `null_metric` | false | polynomial_ridge | 100 | 1 | 100 | 0.080 | 0.030 [0.010, 0.085] | 0.000 [0.000, 0.037] | -0.0002 |
| `null_metric` | false | polynomial_ridge | 200 | 1 | 100 | 0.050 | 0.040 [0.016, 0.098] | 0.000 [0.000, 0.037] | -0.0001 |
| `null_metric` | false | polynomial_ridge | 400 | 1 | 100 | 0.060 | 0.070 [0.034, 0.137] | 0.000 [0.000, 0.037] | -0.0001 |
| `null_metric` | false | polynomial_ridge | 800 | 1 | 100 | 0.020 | 0.020 [0.006, 0.070] | 0.000 [0.000, 0.037] | -0.0000 |
| `post_treatment_control` | false | polynomial_ridge | 100 | 1 | 100 | 0.060 | 0.040 [0.016, 0.098] | 0.000 [0.000, 0.037] | -0.0002 |
| `post_treatment_control` | false | polynomial_ridge | 200 | 1 | 100 | 0.090 | 0.040 [0.016, 0.098] | 0.000 [0.000, 0.037] | -0.0001 |
| `post_treatment_control` | false | polynomial_ridge | 400 | 1 | 100 | 0.080 | 0.060 [0.028, 0.125] | 0.000 [0.000, 0.037] | -0.0001 |
| `post_treatment_control` | false | polynomial_ridge | 800 | 1 | 100 | 0.080 | 0.040 [0.016, 0.098] | 0.000 [0.000, 0.037] | -0.0000 |
| `simpson_increment` | true | polynomial_ridge | 100 | 1 | 100 | 1.000 | 0.990 [0.946, 0.998] | 0.990 [0.946, 0.998] | 0.0155 |
| `simpson_increment` | true | polynomial_ridge | 200 | 1 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0159 |
| `simpson_increment` | true | polynomial_ridge | 400 | 1 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0161 |
| `simpson_increment` | true | polynomial_ridge | 800 | 1 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0160 |

## Reading The Table

The nominal residual-test level is 0.050. A low null rejection rate supports calibration only for the simulated nuisance structures; it does not prove conditional independence testing is universally valid. Power must be interpreted together with sample size and nuisance degree.

Across the displayed grid, conditional-null cross-fit rejection ranges from 0.010 to 1.000; conditional-signal joint detection ranges from 0.990 to 1.000.

The post-treatment scenario is a conditional null for the direct-information estimand after controlling the mediator. Its raw association is real; loss of conditional signal is not a causal verdict.

This report calibrates one reference nuisance model. Submission evidence must add alternative nuisance learners, semi-synthetic real-design tests, and held-out task-family prediction.
