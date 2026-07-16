# Repeated MBE Calibration

This is a repeated-simulation calibration of the compact polynomial-ridge MBE reference implementation. Conditional-null rows report empirical false-positive behavior; conditional-signal rows report power. The joint decision requires both a residual permutation rejection and a 95% out-of-fold Delta-MSE interval entirely above zero.

| Scenario | Signal expected | Nuisance | n | Degree | Repetitions | Legacy reject | Cross-fit reject [95% CI] | Joint decision [95% CI] | Median Delta MSE |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| `clustered_null` | false | polynomial_ridge | 150 | 2 | 100 | 0.360 | 0.160 [0.101, 0.244] | 0.010 [0.002, 0.054] | -0.0009 |
| `clustered_null` | false | polynomial_ridge | 150 | 4 | 100 | 0.290 | 0.120 [0.070, 0.198] | 0.020 [0.006, 0.070] | -0.0030 |
| `clustered_null` | false | polynomial_ridge | 150 | 6 | 100 | 0.370 | 0.170 [0.109, 0.255] | 0.000 [0.000, 0.037] | -0.0110 |
| `clustered_null` | false | polynomial_ridge | 300 | 2 | 100 | 0.330 | 0.180 [0.117, 0.267] | 0.000 [0.000, 0.037] | -0.0006 |
| `clustered_null` | false | polynomial_ridge | 300 | 4 | 100 | 0.390 | 0.040 [0.016, 0.098] | 0.000 [0.000, 0.037] | -0.0012 |
| `clustered_null` | false | polynomial_ridge | 300 | 6 | 100 | 0.330 | 0.090 [0.048, 0.162] | 0.000 [0.000, 0.037] | -0.0019 |
| `clustered_null` | false | polynomial_ridge | 600 | 2 | 100 | 0.460 | 0.320 [0.237, 0.417] | 0.010 [0.002, 0.054] | -0.0003 |
| `clustered_null` | false | polynomial_ridge | 600 | 4 | 100 | 0.440 | 0.080 [0.041, 0.150] | 0.000 [0.000, 0.037] | -0.0005 |
| `clustered_null` | false | polynomial_ridge | 600 | 6 | 100 | 0.370 | 0.060 [0.028, 0.125] | 0.000 [0.000, 0.037] | -0.0010 |
| `genuine_increment` | true | polynomial_ridge | 150 | 2 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0399 |
| `genuine_increment` | true | polynomial_ridge | 150 | 4 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0420 |
| `genuine_increment` | true | polynomial_ridge | 150 | 6 | 100 | 1.000 | 1.000 [0.963, 1.000] | 0.890 [0.814, 0.937] | 0.0467 |
| `genuine_increment` | true | polynomial_ridge | 300 | 2 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0411 |
| `genuine_increment` | true | polynomial_ridge | 300 | 4 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0421 |
| `genuine_increment` | true | polynomial_ridge | 300 | 6 | 100 | 1.000 | 1.000 [0.963, 1.000] | 0.980 [0.930, 0.994] | 0.0422 |
| `genuine_increment` | true | polynomial_ridge | 600 | 2 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0402 |
| `genuine_increment` | true | polynomial_ridge | 600 | 4 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0411 |
| `genuine_increment` | true | polynomial_ridge | 600 | 6 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0417 |
| `heteroskedastic_null` | false | polynomial_ridge | 150 | 2 | 100 | 0.210 | 0.070 [0.034, 0.137] | 0.030 [0.010, 0.085] | 0.0002 |
| `heteroskedastic_null` | false | polynomial_ridge | 150 | 4 | 100 | 0.190 | 0.070 [0.034, 0.137] | 0.000 [0.000, 0.037] | -0.0003 |
| `heteroskedastic_null` | false | polynomial_ridge | 150 | 6 | 100 | 0.230 | 0.060 [0.028, 0.125] | 0.000 [0.000, 0.037] | -0.0004 |
| `heteroskedastic_null` | false | polynomial_ridge | 300 | 2 | 100 | 0.350 | 0.090 [0.048, 0.162] | 0.020 [0.006, 0.070] | 0.0004 |
| `heteroskedastic_null` | false | polynomial_ridge | 300 | 4 | 100 | 0.320 | 0.060 [0.028, 0.125] | 0.000 [0.000, 0.037] | -0.0001 |
| `heteroskedastic_null` | false | polynomial_ridge | 300 | 6 | 100 | 0.320 | 0.030 [0.010, 0.085] | 0.000 [0.000, 0.037] | -0.0002 |
| `heteroskedastic_null` | false | polynomial_ridge | 600 | 2 | 100 | 0.370 | 0.050 [0.022, 0.112] | 0.030 [0.010, 0.085] | 0.0004 |
| `heteroskedastic_null` | false | polynomial_ridge | 600 | 4 | 100 | 0.490 | 0.080 [0.041, 0.150] | 0.000 [0.000, 0.037] | -0.0001 |
| `heteroskedastic_null` | false | polynomial_ridge | 600 | 6 | 100 | 0.470 | 0.030 [0.010, 0.085] | 0.000 [0.000, 0.037] | -0.0001 |
| `linear_proxy` | false | polynomial_ridge | 150 | 2 | 100 | 0.090 | 0.280 [0.201, 0.375] | 0.080 [0.041, 0.150] | 0.0008 |
| `linear_proxy` | false | polynomial_ridge | 150 | 4 | 100 | 0.050 | 0.080 [0.041, 0.150] | 0.000 [0.000, 0.037] | -0.0005 |
| `linear_proxy` | false | polynomial_ridge | 150 | 6 | 100 | 0.100 | 0.040 [0.016, 0.098] | 0.000 [0.000, 0.037] | -0.0012 |
| `linear_proxy` | false | polynomial_ridge | 300 | 2 | 100 | 0.090 | 0.430 [0.337, 0.528] | 0.290 [0.210, 0.385] | 0.0009 |
| `linear_proxy` | false | polynomial_ridge | 300 | 4 | 100 | 0.050 | 0.040 [0.016, 0.098] | 0.000 [0.000, 0.037] | -0.0003 |
| `linear_proxy` | false | polynomial_ridge | 300 | 6 | 100 | 0.040 | 0.090 [0.048, 0.162] | 0.000 [0.000, 0.037] | -0.0005 |
| `linear_proxy` | false | polynomial_ridge | 600 | 2 | 100 | 0.050 | 0.760 [0.668, 0.833] | 0.700 [0.604, 0.781] | 0.0011 |
| `linear_proxy` | false | polynomial_ridge | 600 | 4 | 100 | 0.040 | 0.070 [0.034, 0.137] | 0.010 [0.002, 0.054] | -0.0000 |
| `linear_proxy` | false | polynomial_ridge | 600 | 6 | 100 | 0.060 | 0.050 [0.022, 0.112] | 0.000 [0.000, 0.037] | -0.0002 |
| `nonlinear_proxy` | false | polynomial_ridge | 150 | 2 | 100 | 1.000 | 0.660 [0.563, 0.745] | 0.640 [0.542, 0.727] | 0.0021 |
| `nonlinear_proxy` | false | polynomial_ridge | 150 | 4 | 100 | 1.000 | 0.040 [0.016, 0.098] | 0.000 [0.000, 0.037] | -0.0000 |
| `nonlinear_proxy` | false | polynomial_ridge | 150 | 6 | 100 | 1.000 | 0.050 [0.022, 0.112] | 0.000 [0.000, 0.037] | -0.0003 |
| `nonlinear_proxy` | false | polynomial_ridge | 300 | 2 | 100 | 1.000 | 0.920 [0.850, 0.959] | 0.920 [0.850, 0.959] | 0.0024 |
| `nonlinear_proxy` | false | polynomial_ridge | 300 | 4 | 100 | 1.000 | 0.130 [0.078, 0.210] | 0.030 [0.010, 0.085] | 0.0001 |
| `nonlinear_proxy` | false | polynomial_ridge | 300 | 6 | 100 | 1.000 | 0.050 [0.022, 0.112] | 0.000 [0.000, 0.037] | -0.0001 |
| `nonlinear_proxy` | false | polynomial_ridge | 600 | 2 | 100 | 1.000 | 0.990 [0.946, 0.998] | 0.990 [0.946, 0.998] | 0.0023 |
| `nonlinear_proxy` | false | polynomial_ridge | 600 | 4 | 100 | 1.000 | 0.210 [0.142, 0.300] | 0.080 [0.041, 0.150] | 0.0001 |
| `nonlinear_proxy` | false | polynomial_ridge | 600 | 6 | 100 | 1.000 | 0.060 [0.028, 0.125] | 0.000 [0.000, 0.037] | -0.0001 |
| `null_metric` | false | polynomial_ridge | 150 | 2 | 100 | 0.060 | 0.070 [0.034, 0.137] | 0.000 [0.000, 0.037] | -0.0004 |
| `null_metric` | false | polynomial_ridge | 150 | 4 | 100 | 0.040 | 0.070 [0.034, 0.137] | 0.000 [0.000, 0.037] | -0.0008 |
| `null_metric` | false | polynomial_ridge | 150 | 6 | 100 | 0.020 | 0.080 [0.041, 0.150] | 0.000 [0.000, 0.037] | -0.0014 |
| `null_metric` | false | polynomial_ridge | 300 | 2 | 100 | 0.100 | 0.090 [0.048, 0.162] | 0.000 [0.000, 0.037] | -0.0002 |
| `null_metric` | false | polynomial_ridge | 300 | 4 | 100 | 0.100 | 0.090 [0.048, 0.162] | 0.000 [0.000, 0.037] | -0.0004 |
| `null_metric` | false | polynomial_ridge | 300 | 6 | 100 | 0.060 | 0.070 [0.034, 0.137] | 0.000 [0.000, 0.037] | -0.0006 |
| `null_metric` | false | polynomial_ridge | 600 | 2 | 100 | 0.060 | 0.000 [0.000, 0.037] | 0.000 [0.000, 0.037] | -0.0001 |
| `null_metric` | false | polynomial_ridge | 600 | 4 | 100 | 0.060 | 0.090 [0.048, 0.162] | 0.000 [0.000, 0.037] | -0.0002 |
| `null_metric` | false | polynomial_ridge | 600 | 6 | 100 | 0.060 | 0.050 [0.022, 0.112] | 0.000 [0.000, 0.037] | -0.0002 |
| `post_treatment_control` | false | polynomial_ridge | 150 | 2 | 100 | 0.080 | 0.290 [0.210, 0.385] | 0.090 [0.048, 0.162] | 0.0010 |
| `post_treatment_control` | false | polynomial_ridge | 150 | 4 | 100 | 0.090 | 0.080 [0.041, 0.150] | 0.000 [0.000, 0.037] | -0.0004 |
| `post_treatment_control` | false | polynomial_ridge | 150 | 6 | 100 | 0.100 | 0.070 [0.034, 0.137] | 0.000 [0.000, 0.037] | -0.0006 |
| `post_treatment_control` | false | polynomial_ridge | 300 | 2 | 100 | 0.040 | 0.610 [0.512, 0.700] | 0.390 [0.300, 0.488] | 0.0009 |
| `post_treatment_control` | false | polynomial_ridge | 300 | 4 | 100 | 0.040 | 0.040 [0.016, 0.098] | 0.000 [0.000, 0.037] | -0.0001 |
| `post_treatment_control` | false | polynomial_ridge | 300 | 6 | 100 | 0.070 | 0.090 [0.048, 0.162] | 0.000 [0.000, 0.037] | -0.0004 |
| `post_treatment_control` | false | polynomial_ridge | 600 | 2 | 100 | 0.060 | 0.830 [0.745, 0.891] | 0.790 [0.700, 0.858] | 0.0010 |
| `post_treatment_control` | false | polynomial_ridge | 600 | 4 | 100 | 0.050 | 0.040 [0.016, 0.098] | 0.010 [0.002, 0.054] | 0.0000 |
| `post_treatment_control` | false | polynomial_ridge | 600 | 6 | 100 | 0.110 | 0.070 [0.034, 0.137] | 0.000 [0.000, 0.037] | -0.0001 |
| `simpson_increment` | true | polynomial_ridge | 150 | 2 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0161 |
| `simpson_increment` | true | polynomial_ridge | 150 | 4 | 100 | 1.000 | 1.000 [0.963, 1.000] | 0.990 [0.946, 0.998] | 0.0174 |
| `simpson_increment` | true | polynomial_ridge | 150 | 6 | 100 | 1.000 | 1.000 [0.963, 1.000] | 0.930 [0.863, 0.966] | 0.0196 |
| `simpson_increment` | true | polynomial_ridge | 300 | 2 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0162 |
| `simpson_increment` | true | polynomial_ridge | 300 | 4 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0170 |
| `simpson_increment` | true | polynomial_ridge | 300 | 6 | 100 | 1.000 | 1.000 [0.963, 1.000] | 0.990 [0.946, 0.998] | 0.0179 |
| `simpson_increment` | true | polynomial_ridge | 600 | 2 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0161 |
| `simpson_increment` | true | polynomial_ridge | 600 | 4 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0169 |
| `simpson_increment` | true | polynomial_ridge | 600 | 6 | 100 | 1.000 | 1.000 [0.963, 1.000] | 0.990 [0.946, 0.998] | 0.0170 |

## Reading The Table

The nominal residual-test level is 0.050. A low null rejection rate supports calibration only for the simulated nuisance structures; it does not prove conditional independence testing is universally valid. Power must be interpreted together with sample size and nuisance degree.

Across the displayed grid, conditional-null cross-fit rejection ranges from 0.000 to 0.990; conditional-signal joint detection ranges from 0.890 to 1.000.

The post-treatment scenario is a conditional null for the direct-information estimand after controlling the mediator. Its raw association is real; loss of conditional signal is not a causal verdict.

This report calibrates one reference nuisance model. Submission evidence must add alternative nuisance learners, semi-synthetic real-design tests, and held-out task-family prediction.
