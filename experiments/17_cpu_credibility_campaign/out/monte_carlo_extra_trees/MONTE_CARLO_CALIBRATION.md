# Repeated MBE Calibration

This is a repeated-simulation calibration of the compact polynomial-ridge MBE reference implementation. Conditional-null rows report empirical false-positive behavior; conditional-signal rows report power. The joint decision requires both a residual permutation rejection and a 95% out-of-fold Delta-MSE interval entirely above zero.

| Scenario | Signal expected | Nuisance | n | Degree | Repetitions | Legacy reject | Cross-fit reject [95% CI] | Joint decision [95% CI] | Median Delta MSE |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| `clustered_null` | false | extra_trees | 100 | 2 | 100 | 0.340 | 0.130 [0.078, 0.210] | 0.030 [0.010, 0.085] | 0.0015 |
| `clustered_null` | false | extra_trees | 100 | 6 | 100 | 0.390 | 0.190 [0.125, 0.278] | 0.070 [0.034, 0.137] | 0.0011 |
| `clustered_null` | false | extra_trees | 200 | 2 | 100 | 0.340 | 0.170 [0.109, 0.255] | 0.070 [0.034, 0.137] | 0.0022 |
| `clustered_null` | false | extra_trees | 200 | 6 | 100 | 0.310 | 0.100 [0.055, 0.174] | 0.040 [0.016, 0.098] | 0.0029 |
| `clustered_null` | false | extra_trees | 400 | 2 | 100 | 0.340 | 0.180 [0.117, 0.267] | 0.130 [0.078, 0.210] | 0.0034 |
| `clustered_null` | false | extra_trees | 400 | 6 | 100 | 0.400 | 0.190 [0.125, 0.278] | 0.100 [0.055, 0.174] | 0.0028 |
| `clustered_null` | false | extra_trees | 800 | 2 | 100 | 0.300 | 0.130 [0.078, 0.210] | 0.100 [0.055, 0.174] | 0.0038 |
| `clustered_null` | false | extra_trees | 800 | 6 | 100 | 0.360 | 0.120 [0.070, 0.198] | 0.110 [0.063, 0.186] | 0.0036 |
| `genuine_increment` | true | extra_trees | 100 | 2 | 100 | 1.000 | 0.990 [0.946, 0.998] | 0.990 [0.946, 0.998] | 0.0379 |
| `genuine_increment` | true | extra_trees | 100 | 6 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0368 |
| `genuine_increment` | true | extra_trees | 200 | 2 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0413 |
| `genuine_increment` | true | extra_trees | 200 | 6 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0406 |
| `genuine_increment` | true | extra_trees | 400 | 2 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0428 |
| `genuine_increment` | true | extra_trees | 400 | 6 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0422 |
| `genuine_increment` | true | extra_trees | 800 | 2 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0431 |
| `genuine_increment` | true | extra_trees | 800 | 6 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0436 |
| `heteroskedastic_null` | false | extra_trees | 100 | 2 | 100 | 0.110 | 0.050 [0.022, 0.112] | 0.050 [0.022, 0.112] | 0.0046 |
| `heteroskedastic_null` | false | extra_trees | 100 | 6 | 100 | 0.110 | 0.060 [0.028, 0.125] | 0.060 [0.028, 0.125] | 0.0044 |
| `heteroskedastic_null` | false | extra_trees | 200 | 2 | 100 | 0.240 | 0.050 [0.022, 0.112] | 0.050 [0.022, 0.112] | 0.0023 |
| `heteroskedastic_null` | false | extra_trees | 200 | 6 | 100 | 0.230 | 0.060 [0.028, 0.125] | 0.060 [0.028, 0.125] | 0.0023 |
| `heteroskedastic_null` | false | extra_trees | 400 | 2 | 100 | 0.330 | 0.030 [0.010, 0.085] | 0.020 [0.006, 0.070] | 0.0008 |
| `heteroskedastic_null` | false | extra_trees | 400 | 6 | 100 | 0.300 | 0.060 [0.028, 0.125] | 0.060 [0.028, 0.125] | 0.0007 |
| `heteroskedastic_null` | false | extra_trees | 800 | 2 | 100 | 0.560 | 0.050 [0.022, 0.112] | 0.030 [0.010, 0.085] | 0.0002 |
| `heteroskedastic_null` | false | extra_trees | 800 | 6 | 100 | 0.630 | 0.050 [0.022, 0.112] | 0.040 [0.016, 0.098] | 0.0002 |
| `linear_proxy` | false | extra_trees | 100 | 2 | 100 | 0.060 | 0.260 [0.184, 0.354] | 0.200 [0.133, 0.289] | 0.0024 |
| `linear_proxy` | false | extra_trees | 100 | 6 | 100 | 0.060 | 0.140 [0.085, 0.221] | 0.090 [0.048, 0.162] | 0.0023 |
| `linear_proxy` | false | extra_trees | 200 | 2 | 100 | 0.080 | 0.220 [0.150, 0.311] | 0.040 [0.016, 0.098] | 0.0007 |
| `linear_proxy` | false | extra_trees | 200 | 6 | 100 | 0.050 | 0.100 [0.055, 0.174] | 0.020 [0.006, 0.070] | 0.0005 |
| `linear_proxy` | false | extra_trees | 400 | 2 | 100 | 0.050 | 0.060 [0.028, 0.125] | 0.000 [0.000, 0.037] | 0.0000 |
| `linear_proxy` | false | extra_trees | 400 | 6 | 100 | 0.060 | 0.060 [0.028, 0.125] | 0.000 [0.000, 0.037] | -0.0000 |
| `linear_proxy` | false | extra_trees | 800 | 2 | 100 | 0.160 | 0.050 [0.022, 0.112] | 0.000 [0.000, 0.037] | -0.0001 |
| `linear_proxy` | false | extra_trees | 800 | 6 | 100 | 0.060 | 0.070 [0.034, 0.137] | 0.000 [0.000, 0.037] | -0.0001 |
| `nonlinear_proxy` | false | extra_trees | 100 | 2 | 100 | 1.000 | 0.940 [0.875, 0.972] | 0.940 [0.875, 0.972] | 0.0104 |
| `nonlinear_proxy` | false | extra_trees | 100 | 6 | 100 | 1.000 | 0.940 [0.875, 0.972] | 0.940 [0.875, 0.972] | 0.0103 |
| `nonlinear_proxy` | false | extra_trees | 200 | 2 | 100 | 1.000 | 0.900 [0.826, 0.945] | 0.900 [0.826, 0.945] | 0.0032 |
| `nonlinear_proxy` | false | extra_trees | 200 | 6 | 100 | 1.000 | 0.870 [0.790, 0.922] | 0.870 [0.790, 0.922] | 0.0033 |
| `nonlinear_proxy` | false | extra_trees | 400 | 2 | 100 | 1.000 | 0.620 [0.522, 0.709] | 0.320 [0.237, 0.417] | 0.0006 |
| `nonlinear_proxy` | false | extra_trees | 400 | 6 | 100 | 1.000 | 0.650 [0.553, 0.736] | 0.330 [0.246, 0.427] | 0.0006 |
| `nonlinear_proxy` | false | extra_trees | 800 | 2 | 100 | 1.000 | 0.240 [0.167, 0.332] | 0.000 [0.000, 0.037] | -0.0001 |
| `nonlinear_proxy` | false | extra_trees | 800 | 6 | 100 | 1.000 | 0.180 [0.117, 0.267] | 0.000 [0.000, 0.037] | -0.0001 |
| `null_metric` | false | extra_trees | 100 | 2 | 100 | 0.100 | 0.100 [0.055, 0.174] | 0.080 [0.041, 0.150] | 0.0019 |
| `null_metric` | false | extra_trees | 100 | 6 | 100 | 0.050 | 0.050 [0.022, 0.112] | 0.010 [0.002, 0.054] | 0.0019 |
| `null_metric` | false | extra_trees | 200 | 2 | 100 | 0.090 | 0.020 [0.006, 0.070] | 0.010 [0.002, 0.054] | 0.0005 |
| `null_metric` | false | extra_trees | 200 | 6 | 100 | 0.070 | 0.090 [0.048, 0.162] | 0.040 [0.016, 0.098] | 0.0005 |
| `null_metric` | false | extra_trees | 400 | 2 | 100 | 0.090 | 0.030 [0.010, 0.085] | 0.000 [0.000, 0.037] | -0.0001 |
| `null_metric` | false | extra_trees | 400 | 6 | 100 | 0.090 | 0.020 [0.006, 0.070] | 0.000 [0.000, 0.037] | -0.0001 |
| `null_metric` | false | extra_trees | 800 | 2 | 100 | 0.030 | 0.030 [0.010, 0.085] | 0.000 [0.000, 0.037] | -0.0003 |
| `null_metric` | false | extra_trees | 800 | 6 | 100 | 0.030 | 0.060 [0.028, 0.125] | 0.000 [0.000, 0.037] | -0.0004 |
| `post_treatment_control` | false | extra_trees | 100 | 2 | 100 | 0.080 | 0.060 [0.028, 0.125] | 0.000 [0.000, 0.037] | 0.0001 |
| `post_treatment_control` | false | extra_trees | 100 | 6 | 100 | 0.090 | 0.130 [0.078, 0.210] | 0.010 [0.002, 0.054] | 0.0001 |
| `post_treatment_control` | false | extra_trees | 200 | 2 | 100 | 0.180 | 0.040 [0.016, 0.098] | 0.000 [0.000, 0.037] | -0.0002 |
| `post_treatment_control` | false | extra_trees | 200 | 6 | 100 | 0.080 | 0.050 [0.022, 0.112] | 0.000 [0.000, 0.037] | -0.0003 |
| `post_treatment_control` | false | extra_trees | 400 | 2 | 100 | 0.090 | 0.030 [0.010, 0.085] | 0.000 [0.000, 0.037] | -0.0002 |
| `post_treatment_control` | false | extra_trees | 400 | 6 | 100 | 0.060 | 0.030 [0.010, 0.085] | 0.010 [0.002, 0.054] | -0.0001 |
| `post_treatment_control` | false | extra_trees | 800 | 2 | 100 | 0.090 | 0.060 [0.028, 0.125] | 0.000 [0.000, 0.037] | -0.0000 |
| `post_treatment_control` | false | extra_trees | 800 | 6 | 100 | 0.130 | 0.070 [0.034, 0.137] | 0.000 [0.000, 0.037] | -0.0000 |
| `simpson_increment` | true | extra_trees | 100 | 2 | 100 | 1.000 | 0.980 [0.930, 0.994] | 0.980 [0.930, 0.994] | 0.0142 |
| `simpson_increment` | true | extra_trees | 100 | 6 | 100 | 1.000 | 0.990 [0.946, 0.998] | 0.990 [0.946, 0.998] | 0.0147 |
| `simpson_increment` | true | extra_trees | 200 | 2 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0162 |
| `simpson_increment` | true | extra_trees | 200 | 6 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0164 |
| `simpson_increment` | true | extra_trees | 400 | 2 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0169 |
| `simpson_increment` | true | extra_trees | 400 | 6 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0168 |
| `simpson_increment` | true | extra_trees | 800 | 2 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0171 |
| `simpson_increment` | true | extra_trees | 800 | 6 | 100 | 1.000 | 1.000 [0.963, 1.000] | 1.000 [0.963, 1.000] | 0.0171 |

## Reading The Table

The nominal residual-test level is 0.050. A low null rejection rate supports calibration only for the simulated nuisance structures; it does not prove conditional independence testing is universally valid. Power must be interpreted together with sample size and nuisance degree.

Across the displayed grid, conditional-null cross-fit rejection ranges from 0.020 to 0.940; conditional-signal joint detection ranges from 0.980 to 1.000.

The post-treatment scenario is a conditional null for the direct-information estimand after controlling the mediator. Its raw association is real; loss of conditional signal is not a causal verdict.

This report calibrates one reference nuisance model. Submission evidence must add alternative nuisance learners, semi-synthetic real-design tests, and held-out task-family prediction.
