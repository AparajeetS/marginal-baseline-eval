# Repeated MBE Calibration

This is a repeated-simulation calibration of the compact polynomial-ridge MBE reference implementation. Conditional-null rows report empirical false-positive behavior; conditional-signal rows report power. The joint decision requires both a residual permutation rejection and a 95% out-of-fold Delta-MSE interval entirely above zero.

| Scenario | Signal expected | Nuisance | n | Degree | Repetitions | Legacy reject | Cross-fit reject [95% CI] | Joint decision [95% CI] | Median Delta MSE |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| `genuine_increment` | true | extra_trees | 150 | 1 | 50 | 1.000 | 1.000 [0.929, 1.000] | 1.000 [0.929, 1.000] | 0.0415 |
| `genuine_increment` | true | extra_trees | 300 | 1 | 50 | 1.000 | 1.000 [0.929, 1.000] | 1.000 [0.929, 1.000] | 0.0449 |
| `linear_proxy` | false | extra_trees | 150 | 1 | 50 | 0.060 | 0.960 [0.865, 0.989] | 0.960 [0.865, 0.989] | 0.0135 |
| `linear_proxy` | false | extra_trees | 300 | 1 | 50 | 0.080 | 1.000 [0.929, 1.000] | 1.000 [0.929, 1.000] | 0.0114 |
| `nonlinear_proxy` | false | extra_trees | 150 | 1 | 50 | 1.000 | 0.860 [0.738, 0.930] | 0.860 [0.738, 0.930] | 0.0051 |
| `nonlinear_proxy` | false | extra_trees | 300 | 1 | 50 | 1.000 | 0.640 [0.501, 0.759] | 0.520 [0.385, 0.652] | 0.0015 |
| `null_metric` | false | extra_trees | 150 | 1 | 50 | 0.060 | 0.020 [0.004, 0.105] | 0.020 [0.004, 0.105] | 0.0109 |
| `null_metric` | false | extra_trees | 300 | 1 | 50 | 0.060 | 0.060 [0.021, 0.162] | 0.060 [0.021, 0.162] | 0.0087 |
| `post_treatment_control` | false | extra_trees | 150 | 1 | 50 | 0.100 | 0.460 [0.330, 0.596] | 0.460 [0.330, 0.596] | 0.0043 |
| `post_treatment_control` | false | extra_trees | 300 | 1 | 50 | 0.080 | 0.500 [0.366, 0.634] | 0.500 [0.366, 0.634] | 0.0020 |
| `simpson_increment` | true | extra_trees | 150 | 1 | 50 | 1.000 | 1.000 [0.929, 1.000] | 1.000 [0.929, 1.000] | 0.0150 |
| `simpson_increment` | true | extra_trees | 300 | 1 | 50 | 1.000 | 1.000 [0.929, 1.000] | 1.000 [0.929, 1.000] | 0.0159 |

## Reading The Table

The nominal residual-test level is 0.050. A low null rejection rate supports calibration only for the simulated nuisance structures; it does not prove conditional independence testing is universally valid. Power must be interpreted together with sample size and nuisance degree.

Across the displayed grid, conditional-null cross-fit rejection ranges from 0.020 to 1.000; conditional-signal joint detection ranges from 1.000 to 1.000.

The post-treatment scenario is a conditional null for the direct-information estimand after controlling the mediator. Its raw association is real; loss of conditional signal is not a causal verdict.

This report calibrates one reference nuisance model. Submission evidence must add alternative nuisance learners, semi-synthetic real-design tests, and held-out task-family prediction.
