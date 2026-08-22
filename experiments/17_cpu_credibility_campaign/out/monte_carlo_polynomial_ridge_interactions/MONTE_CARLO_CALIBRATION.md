# Repeated MBE Calibration

This is a repeated-simulation calibration of the compact polynomial-ridge MBE reference implementation. Conditional-null rows report empirical false-positive behavior; conditional-signal rows report power. The joint decision requires both a residual permutation rejection and a 95% out-of-fold Delta-MSE interval entirely above zero.

| Scenario | Signal expected | Nuisance | n | Degree | Repetitions | Legacy reject | Cross-fit reject [95% CI] | Joint decision [95% CI] | Median Delta MSE |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| `clustered_null` | false | polynomial_ridge_interactions | 100 | 2 | 100 | 0.340 | 0.050 [0.022, 0.112] | 0.000 [0.000, 0.037] | -0.0024 |
| `clustered_null` | false | polynomial_ridge_interactions | 100 | 6 | 100 | 0.390 | 0.140 [0.085, 0.221] | 0.030 [0.010, 0.085] | -0.0035 |
| `clustered_null` | false | polynomial_ridge_interactions | 200 | 2 | 100 | 0.340 | 0.090 [0.048, 0.162] | 0.010 [0.002, 0.054] | -0.0010 |
| `clustered_null` | false | polynomial_ridge_interactions | 200 | 6 | 100 | 0.310 | 0.070 [0.034, 0.137] | 0.000 [0.000, 0.037] | -0.0014 |
| `clustered_null` | false | polynomial_ridge_interactions | 400 | 2 | 100 | 0.340 | 0.050 [0.022, 0.112] | 0.010 [0.002, 0.054] | -0.0004 |
| `clustered_null` | false | polynomial_ridge_interactions | 400 | 6 | 100 | 0.400 | 0.120 [0.070, 0.198] | 0.000 [0.000, 0.037] | -0.0004 |
| `clustered_null` | false | polynomial_ridge_interactions | 800 | 2 | 100 | 0.300 | 0.040 [0.016, 0.098] | 0.010 [0.002, 0.054] | -0.0002 |
| `clustered_null` | false | polynomial_ridge_interactions | 800 | 6 | 100 | 0.360 | 0.070 [0.034, 0.137] | 0.000 [0.000, 0.037] | -0.0002 |
| `genuine_increment` | true | polynomial_ridge_interactions | 100 | 2 | 100 | 1.000 | 0.990 [0.946, 0.998] | 0.990 [0.946, 0.998] | 0.0413 |
| `genuine_increment` | true | polynomial_ridge_interactions | 100 | 6 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0418 |
| `genuine_increment` | true | polynomial_ridge_interactions | 200 | 2 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0413 |
| `genuine_increment` | true | polynomial_ridge_interactions | 200 | 6 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0419 |
| `genuine_increment` | true | polynomial_ridge_interactions | 400 | 2 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0407 |
| `genuine_increment` | true | polynomial_ridge_interactions | 400 | 6 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0408 |
| `genuine_increment` | true | polynomial_ridge_interactions | 800 | 2 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0403 |
| `genuine_increment` | true | polynomial_ridge_interactions | 800 | 6 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0412 |
| `heteroskedastic_null` | false | polynomial_ridge_interactions | 100 | 2 | 100 | 0.110 | 0.060 [0.028, 0.125] | 0.020 [0.006, 0.070] | 0.0005 |
| `heteroskedastic_null` | false | polynomial_ridge_interactions | 100 | 6 | 100 | 0.110 | 0.070 [0.034, 0.137] | 0.010 [0.002, 0.054] | -0.0002 |
| `heteroskedastic_null` | false | polynomial_ridge_interactions | 200 | 2 | 100 | 0.240 | 0.130 [0.078, 0.210] | 0.030 [0.010, 0.085] | 0.0005 |
| `heteroskedastic_null` | false | polynomial_ridge_interactions | 200 | 6 | 100 | 0.230 | 0.050 [0.022, 0.112] | 0.000 [0.000, 0.037] | -0.0001 |
| `heteroskedastic_null` | false | polynomial_ridge_interactions | 400 | 2 | 100 | 0.330 | 0.120 [0.070, 0.198] | 0.110 [0.063, 0.186] | 0.0006 |
| `heteroskedastic_null` | false | polynomial_ridge_interactions | 400 | 6 | 100 | 0.300 | 0.040 [0.016, 0.098] | 0.000 [0.000, 0.037] | -0.0000 |
| `heteroskedastic_null` | false | polynomial_ridge_interactions | 800 | 2 | 100 | 0.560 | 0.220 [0.150, 0.311] | 0.220 [0.150, 0.311] | 0.0006 |
| `heteroskedastic_null` | false | polynomial_ridge_interactions | 800 | 6 | 100 | 0.630 | 0.070 [0.034, 0.137] | 0.000 [0.000, 0.037] | -0.0000 |
| `linear_proxy` | false | polynomial_ridge_interactions | 100 | 2 | 100 | 0.060 | 0.040 [0.016, 0.098] | 0.000 [0.000, 0.037] | -0.0004 |
| `linear_proxy` | false | polynomial_ridge_interactions | 100 | 6 | 100 | 0.060 | 0.040 [0.016, 0.098] | 0.000 [0.000, 0.037] | -0.0006 |
| `linear_proxy` | false | polynomial_ridge_interactions | 200 | 2 | 100 | 0.080 | 0.100 [0.055, 0.174] | 0.000 [0.000, 0.037] | -0.0002 |
| `linear_proxy` | false | polynomial_ridge_interactions | 200 | 6 | 100 | 0.050 | 0.020 [0.006, 0.070] | 0.000 [0.000, 0.037] | -0.0002 |
| `linear_proxy` | false | polynomial_ridge_interactions | 400 | 2 | 100 | 0.050 | 0.070 [0.034, 0.137] | 0.000 [0.000, 0.037] | -0.0001 |
| `linear_proxy` | false | polynomial_ridge_interactions | 400 | 6 | 100 | 0.060 | 0.090 [0.048, 0.162] | 0.000 [0.000, 0.037] | -0.0001 |
| `linear_proxy` | false | polynomial_ridge_interactions | 800 | 2 | 100 | 0.160 | 0.050 [0.022, 0.112] | 0.000 [0.000, 0.037] | -0.0000 |
| `linear_proxy` | false | polynomial_ridge_interactions | 800 | 6 | 100 | 0.060 | 0.040 [0.016, 0.098] | 0.000 [0.000, 0.037] | -0.0001 |
| `nonlinear_proxy` | false | polynomial_ridge_interactions | 100 | 2 | 100 | 1.000 | 0.600 [0.502, 0.691] | 0.490 [0.394, 0.587] | 0.0028 |
| `nonlinear_proxy` | false | polynomial_ridge_interactions | 100 | 6 | 100 | 1.000 | 0.040 [0.016, 0.098] | 0.000 [0.000, 0.037] | -0.0001 |
| `nonlinear_proxy` | false | polynomial_ridge_interactions | 200 | 2 | 100 | 1.000 | 0.870 [0.790, 0.922] | 0.860 [0.779, 0.915] | 0.0024 |
| `nonlinear_proxy` | false | polynomial_ridge_interactions | 200 | 6 | 100 | 1.000 | 0.120 [0.070, 0.198] | 0.000 [0.000, 0.037] | -0.0000 |
| `nonlinear_proxy` | false | polynomial_ridge_interactions | 400 | 2 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0023 |
| `nonlinear_proxy` | false | polynomial_ridge_interactions | 400 | 6 | 100 | 1.000 | 0.080 [0.041, 0.150] | 0.000 [0.000, 0.037] | -0.0000 |
| `nonlinear_proxy` | false | polynomial_ridge_interactions | 800 | 2 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0021 |
| `nonlinear_proxy` | false | polynomial_ridge_interactions | 800 | 6 | 100 | 1.000 | 0.020 [0.006, 0.070] | 0.000 [0.000, 0.037] | -0.0000 |
| `null_metric` | false | polynomial_ridge_interactions | 100 | 2 | 100 | 0.100 | 0.090 [0.048, 0.162] | 0.000 [0.000, 0.037] | -0.0005 |
| `null_metric` | false | polynomial_ridge_interactions | 100 | 6 | 100 | 0.050 | 0.040 [0.016, 0.098] | 0.000 [0.000, 0.037] | -0.0006 |
| `null_metric` | false | polynomial_ridge_interactions | 200 | 2 | 100 | 0.090 | 0.030 [0.010, 0.085] | 0.000 [0.000, 0.037] | -0.0002 |
| `null_metric` | false | polynomial_ridge_interactions | 200 | 6 | 100 | 0.070 | 0.080 [0.041, 0.150] | 0.000 [0.000, 0.037] | -0.0002 |
| `null_metric` | false | polynomial_ridge_interactions | 400 | 2 | 100 | 0.090 | 0.050 [0.022, 0.112] | 0.000 [0.000, 0.037] | -0.0001 |
| `null_metric` | false | polynomial_ridge_interactions | 400 | 6 | 100 | 0.090 | 0.030 [0.010, 0.085] | 0.000 [0.000, 0.037] | -0.0001 |
| `null_metric` | false | polynomial_ridge_interactions | 800 | 2 | 100 | 0.030 | 0.010 [0.002, 0.054] | 0.000 [0.000, 0.037] | -0.0001 |
| `null_metric` | false | polynomial_ridge_interactions | 800 | 6 | 100 | 0.030 | 0.060 [0.028, 0.125] | 0.000 [0.000, 0.037] | -0.0001 |
| `post_treatment_control` | false | polynomial_ridge_interactions | 100 | 2 | 100 | 0.080 | 0.060 [0.028, 0.125] | 0.000 [0.000, 0.037] | -0.0006 |
| `post_treatment_control` | false | polynomial_ridge_interactions | 100 | 6 | 100 | 0.090 | 0.080 [0.041, 0.150] | 0.000 [0.000, 0.037] | -0.0005 |
| `post_treatment_control` | false | polynomial_ridge_interactions | 200 | 2 | 100 | 0.180 | 0.050 [0.022, 0.112] | 0.000 [0.000, 0.037] | -0.0003 |
| `post_treatment_control` | false | polynomial_ridge_interactions | 200 | 6 | 100 | 0.080 | 0.050 [0.022, 0.112] | 0.000 [0.000, 0.037] | -0.0003 |
| `post_treatment_control` | false | polynomial_ridge_interactions | 400 | 2 | 100 | 0.090 | 0.040 [0.016, 0.098] | 0.000 [0.000, 0.037] | -0.0001 |
| `post_treatment_control` | false | polynomial_ridge_interactions | 400 | 6 | 100 | 0.060 | 0.030 [0.010, 0.085] | 0.000 [0.000, 0.037] | -0.0002 |
| `post_treatment_control` | false | polynomial_ridge_interactions | 800 | 2 | 100 | 0.090 | 0.030 [0.010, 0.085] | 0.000 [0.000, 0.037] | -0.0001 |
| `post_treatment_control` | false | polynomial_ridge_interactions | 800 | 6 | 100 | 0.130 | 0.080 [0.041, 0.150] | 0.000 [0.000, 0.037] | -0.0001 |
| `simpson_increment` | true | polynomial_ridge_interactions | 100 | 2 | 100 | 1.000 | 0.980 [0.930, 0.994] | 0.980 [0.930, 0.994] | 0.0162 |
| `simpson_increment` | true | polynomial_ridge_interactions | 100 | 6 | 100 | 1.000 | 0.990 [0.946, 0.998] | 0.990 [0.946, 0.998] | 0.0174 |
| `simpson_increment` | true | polynomial_ridge_interactions | 200 | 2 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0162 |
| `simpson_increment` | true | polynomial_ridge_interactions | 200 | 6 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0164 |
| `simpson_increment` | true | polynomial_ridge_interactions | 400 | 2 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0161 |
| `simpson_increment` | true | polynomial_ridge_interactions | 400 | 6 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0161 |
| `simpson_increment` | true | polynomial_ridge_interactions | 800 | 2 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0160 |
| `simpson_increment` | true | polynomial_ridge_interactions | 800 | 6 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0161 |

## Reading The Table

The nominal residual-test level is 0.050. A low null rejection rate supports calibration only for the simulated nuisance structures; it does not prove conditional independence testing is universally valid. Power must be interpreted together with sample size and nuisance degree.

Across the displayed grid, conditional-null cross-fit rejection ranges from 0.010 to 1.000; conditional-signal joint detection ranges from 0.980 to 1.000.

The post-treatment scenario is a conditional null for the direct-information estimand after controlling the mediator. Its raw association is real; loss of conditional signal is not a causal verdict.

This report calibrates one reference nuisance model. Submission evidence must add alternative nuisance learners, semi-synthetic real-design tests, and held-out task-family prediction.
