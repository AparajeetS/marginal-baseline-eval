# Repeated MBE Calibration

This is a repeated-simulation calibration of the compact polynomial-ridge MBE reference implementation. Conditional-null rows report empirical false-positive behavior; conditional-signal rows report power. The joint decision requires both a residual permutation rejection and a 95% out-of-fold Delta-MSE interval entirely above zero.

| Scenario | Signal expected | Nuisance | n | Degree | Repetitions | Legacy reject | Cross-fit reject [95% CI] | Joint decision [95% CI] | Median Delta MSE |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| `clustered_null` | false | polynomial_ridge | 100 | 4 | 100 | 0.380 | 0.090 [0.048, 0.162] | 0.000 [0.000, 0.037] | -0.0050 |
| `clustered_null` | false | polynomial_ridge | 200 | 4 | 100 | 0.420 | 0.150 [0.093, 0.233] | 0.010 [0.002, 0.054] | -0.0015 |
| `clustered_null` | false | polynomial_ridge | 400 | 4 | 100 | 0.410 | 0.130 [0.078, 0.210] | 0.000 [0.000, 0.037] | -0.0010 |
| `clustered_null` | false | polynomial_ridge | 800 | 4 | 100 | 0.390 | 0.060 [0.028, 0.125] | 0.000 [0.000, 0.037] | -0.0004 |
| `genuine_increment` | true | polynomial_ridge | 100 | 4 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0422 |
| `genuine_increment` | true | polynomial_ridge | 200 | 4 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0423 |
| `genuine_increment` | true | polynomial_ridge | 400 | 4 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0423 |
| `genuine_increment` | true | polynomial_ridge | 800 | 4 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0415 |
| `heteroskedastic_null` | false | polynomial_ridge | 100 | 4 | 100 | 0.200 | 0.060 [0.028, 0.125] | 0.000 [0.000, 0.037] | -0.0005 |
| `heteroskedastic_null` | false | polynomial_ridge | 200 | 4 | 100 | 0.280 | 0.070 [0.034, 0.137] | 0.000 [0.000, 0.037] | -0.0002 |
| `heteroskedastic_null` | false | polynomial_ridge | 400 | 4 | 100 | 0.350 | 0.050 [0.022, 0.112] | 0.000 [0.000, 0.037] | -0.0001 |
| `heteroskedastic_null` | false | polynomial_ridge | 800 | 4 | 100 | 0.590 | 0.060 [0.028, 0.125] | 0.000 [0.000, 0.037] | -0.0000 |
| `linear_proxy` | false | polynomial_ridge | 100 | 4 | 100 | 0.100 | 0.080 [0.041, 0.150] | 0.000 [0.000, 0.037] | -0.0008 |
| `linear_proxy` | false | polynomial_ridge | 200 | 4 | 100 | 0.090 | 0.070 [0.034, 0.137] | 0.000 [0.000, 0.037] | -0.0005 |
| `linear_proxy` | false | polynomial_ridge | 400 | 4 | 100 | 0.110 | 0.050 [0.022, 0.112] | 0.000 [0.000, 0.037] | -0.0002 |
| `linear_proxy` | false | polynomial_ridge | 800 | 4 | 100 | 0.110 | 0.060 [0.028, 0.125] | 0.000 [0.000, 0.037] | -0.0001 |
| `nonlinear_proxy` | false | polynomial_ridge | 100 | 4 | 100 | 1.000 | 0.160 [0.101, 0.244] | 0.030 [0.010, 0.085] | 0.0002 |
| `nonlinear_proxy` | false | polynomial_ridge | 200 | 4 | 100 | 1.000 | 0.210 [0.142, 0.300] | 0.040 [0.016, 0.098] | 0.0001 |
| `nonlinear_proxy` | false | polynomial_ridge | 400 | 4 | 100 | 1.000 | 0.170 [0.109, 0.255] | 0.070 [0.034, 0.137] | 0.0001 |
| `nonlinear_proxy` | false | polynomial_ridge | 800 | 4 | 100 | 1.000 | 0.300 [0.219, 0.396] | 0.170 [0.109, 0.255] | 0.0002 |
| `null_metric` | false | polynomial_ridge | 100 | 4 | 100 | 0.030 | 0.090 [0.048, 0.162] | 0.000 [0.000, 0.037] | -0.0012 |
| `null_metric` | false | polynomial_ridge | 200 | 4 | 100 | 0.050 | 0.050 [0.022, 0.112] | 0.000 [0.000, 0.037] | -0.0006 |
| `null_metric` | false | polynomial_ridge | 400 | 4 | 100 | 0.040 | 0.050 [0.022, 0.112] | 0.000 [0.000, 0.037] | -0.0003 |
| `null_metric` | false | polynomial_ridge | 800 | 4 | 100 | 0.050 | 0.030 [0.010, 0.085] | 0.000 [0.000, 0.037] | -0.0001 |
| `post_treatment_control` | false | polynomial_ridge | 100 | 4 | 100 | 0.110 | 0.120 [0.070, 0.198] | 0.000 [0.000, 0.037] | -0.0005 |
| `post_treatment_control` | false | polynomial_ridge | 200 | 4 | 100 | 0.090 | 0.050 [0.022, 0.112] | 0.000 [0.000, 0.037] | -0.0002 |
| `post_treatment_control` | false | polynomial_ridge | 400 | 4 | 100 | 0.070 | 0.050 [0.022, 0.112] | 0.000 [0.000, 0.037] | -0.0001 |
| `post_treatment_control` | false | polynomial_ridge | 800 | 4 | 100 | 0.070 | 0.040 [0.016, 0.098] | 0.000 [0.000, 0.037] | -0.0001 |
| `simpson_increment` | true | polynomial_ridge | 100 | 4 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0174 |
| `simpson_increment` | true | polynomial_ridge | 200 | 4 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0166 |
| `simpson_increment` | true | polynomial_ridge | 400 | 4 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0169 |
| `simpson_increment` | true | polynomial_ridge | 800 | 4 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0168 |

## Reading The Table

The nominal residual-test level is 0.050. A low null rejection rate supports calibration only for the simulated nuisance structures; it does not prove conditional independence testing is universally valid. Power must be interpreted together with sample size and nuisance degree.

Across the displayed grid, conditional-null cross-fit rejection ranges from 0.030 to 0.300; conditional-signal joint detection ranges from 1.000 to 1.000.

The post-treatment scenario is a conditional null for the direct-information estimand after controlling the mediator. Its raw association is real; loss of conditional signal is not a causal verdict.

This report calibrates one reference nuisance model. Submission evidence must add alternative nuisance learners, semi-synthetic real-design tests, and held-out task-family prediction.
