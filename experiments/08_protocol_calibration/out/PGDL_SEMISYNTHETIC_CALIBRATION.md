# PGDL Semi-Synthetic Calibration

This experiment preserves the real Tasks 1-2 sample sizes and hyperparameter geometry while injecting metrics whose role is known by construction. It uses no protected PGDL metric outputs.

| Scope | Case | Expected signal | Nuisance | Degree | n | Repetitions | Joint decision [95% CI] | Sign correct | Median residual rho | Median Delta MSE |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| balanced_pool | `opposite_sign_task_specialists` | heterogeneous | polynomial_ridge | 2 | 108 | 100 | 0.000 [0.000, 0.037] | 1.000 | -0.004 | -0.0041 |
| task1 | `injected_increment` | True | polynomial_ridge | 2 | 96 | 100 | 1.000 [0.963, 1.000] | 1.000 | 0.781 | 0.0284 |
| task1 | `real_design_proxy` | False | polynomial_ridge | 2 | 96 | 100 | 0.030 [0.010, 0.085] | 1.000 | 0.179 | -0.0001 |
| task1 | `real_structure_null` | False | polynomial_ridge | 2 | 96 | 100 | 0.000 [0.000, 0.037] | 1.000 | 0.006 | -0.0004 |
| task1 | `task_specialist` | True | polynomial_ridge | 2 | 96 | 100 | 1.000 [0.963, 1.000] | 1.000 | 0.910 | 0.0616 |
| task2 | `injected_increment` | True | polynomial_ridge | 2 | 54 | 100 | 1.000 [0.963, 1.000] | 1.000 | 0.832 | 0.0296 |
| task2 | `real_design_proxy` | False | polynomial_ridge | 2 | 54 | 100 | 0.070 [0.034, 0.137] | 1.000 | 0.222 | 0.0001 |
| task2 | `real_structure_null` | False | polynomial_ridge | 2 | 54 | 100 | 0.000 [0.000, 0.037] | 1.000 | 0.023 | -0.0007 |
| task2 | `task_specialist` | True | polynomial_ridge | 2 | 54 | 100 | 1.000 [0.963, 1.000] | 1.000 | -0.902 | 0.0698 |
| balanced_pool | `opposite_sign_task_specialists` | heterogeneous | polynomial_ridge | 4 | 108 | 100 | 0.000 [0.000, 0.037] | 1.000 | -0.001 | -0.0070 |
| task1 | `injected_increment` | True | polynomial_ridge | 4 | 96 | 100 | 1.000 [0.963, 1.000] | 1.000 | 0.791 | 0.0287 |
| task1 | `real_design_proxy` | False | polynomial_ridge | 4 | 96 | 100 | 0.020 [0.006, 0.070] | 1.000 | 0.202 | 0.0004 |
| task1 | `real_structure_null` | False | polynomial_ridge | 4 | 96 | 100 | 0.000 [0.000, 0.037] | 1.000 | 0.018 | -0.0007 |
| task1 | `task_specialist` | True | polynomial_ridge | 4 | 96 | 100 | 1.000 [0.963, 1.000] | 1.000 | 0.907 | 0.0634 |
| task2 | `injected_increment` | True | polynomial_ridge | 4 | 54 | 100 | 0.980 [0.930, 0.994] | 1.000 | 0.843 | 0.0313 |
| task2 | `real_design_proxy` | False | polynomial_ridge | 4 | 54 | 100 | 0.020 [0.006, 0.070] | 1.000 | 0.195 | -0.0004 |
| task2 | `real_structure_null` | False | polynomial_ridge | 4 | 54 | 100 | 0.000 [0.000, 0.037] | 1.000 | -0.007 | -0.0009 |
| task2 | `task_specialist` | True | polynomial_ridge | 4 | 54 | 100 | 1.000 [0.963, 1.000] | 1.000 | -0.905 | 0.0670 |
| balanced_pool | `opposite_sign_task_specialists` | heterogeneous | polynomial_ridge | 6 | 108 | 100 | 0.000 [0.000, 0.037] | 1.000 | -0.017 | -0.0090 |
| task1 | `injected_increment` | True | polynomial_ridge | 6 | 96 | 100 | 1.000 [0.963, 1.000] | 1.000 | 0.786 | 0.0263 |
| task1 | `real_design_proxy` | False | polynomial_ridge | 6 | 96 | 100 | 0.030 [0.010, 0.085] | 1.000 | 0.194 | -0.0001 |
| task1 | `real_structure_null` | False | polynomial_ridge | 6 | 96 | 100 | 0.000 [0.000, 0.037] | 1.000 | 0.006 | -0.0013 |
| task1 | `task_specialist` | True | polynomial_ridge | 6 | 96 | 100 | 1.000 [0.963, 1.000] | 1.000 | 0.908 | 0.0625 |
| task2 | `injected_increment` | True | polynomial_ridge | 6 | 54 | 100 | 1.000 [0.963, 1.000] | 1.000 | 0.842 | 0.0296 |
| task2 | `real_design_proxy` | False | polynomial_ridge | 6 | 54 | 100 | 0.020 [0.006, 0.070] | 1.000 | 0.206 | -0.0016 |
| task2 | `real_structure_null` | False | polynomial_ridge | 6 | 54 | 100 | 0.000 [0.000, 0.037] | 1.000 | 0.005 | -0.0014 |
| task2 | `task_specialist` | True | polynomial_ridge | 6 | 54 | 100 | 1.000 [0.963, 1.000] | 1.000 | -0.901 | 0.0675 |

The joint decision requires a residual permutation p-value at or below 0.050 and a 95% out-of-fold Delta-MSE interval entirely above zero. The balanced pooled specialist case deliberately combines opposite task-specific directions; it is a heterogeneity diagnostic, not a conditional-null false-positive test.

These results validate behavior on the observed design distribution, not on unseen checkpoint metrics. They cannot substitute for Tasks 4-5 validation or Tasks 6-9 protected transfer.
