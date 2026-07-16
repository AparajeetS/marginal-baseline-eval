# PGDL Semi-Synthetic Calibration

This experiment preserves the real Tasks 1-2 sample sizes and hyperparameter geometry while injecting metrics whose role is known by construction. It uses no protected PGDL metric outputs.

| Scope | Case | Expected signal | Nuisance | Degree | n | Repetitions | Joint decision [95% CI] | Sign correct | Median residual rho | Median Delta MSE |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| balanced_pool | `opposite_sign_task_specialists` | heterogeneous | extra_trees | 1 | 108 | 50 | 0.020 [0.004, 0.105] | 1.000 | -0.010 | 0.0518 |
| task1 | `injected_increment` | True | extra_trees | 1 | 96 | 50 | 1.000 [0.929, 1.000] | 1.000 | 0.734 | 0.0242 |
| task1 | `real_design_proxy` | False | extra_trees | 1 | 96 | 50 | 1.000 [0.929, 1.000] | 1.000 | 0.460 | 0.0236 |
| task1 | `real_structure_null` | False | extra_trees | 1 | 96 | 50 | 0.020 [0.004, 0.105] | 1.000 | -0.023 | 0.0000 |
| task1 | `task_specialist` | True | extra_trees | 1 | 96 | 50 | 1.000 [0.929, 1.000] | 1.000 | 0.813 | 0.0702 |
| task2 | `injected_increment` | True | extra_trees | 1 | 54 | 50 | 1.000 [0.929, 1.000] | 1.000 | 0.799 | 0.0212 |
| task2 | `real_design_proxy` | False | extra_trees | 1 | 54 | 50 | 1.000 [0.929, 1.000] | 1.000 | 0.644 | 0.0195 |
| task2 | `real_structure_null` | False | extra_trees | 1 | 54 | 50 | 0.020 [0.004, 0.105] | 1.000 | 0.004 | 0.0000 |
| task2 | `task_specialist` | True | extra_trees | 1 | 54 | 50 | 1.000 [0.929, 1.000] | 1.000 | -0.856 | 0.0600 |

The joint decision requires a residual permutation p-value at or below 0.050 and a 95% out-of-fold Delta-MSE interval entirely above zero. The balanced pooled specialist case deliberately combines opposite task-specific directions; it is a heterogeneity diagnostic, not a conditional-null false-positive test.

These results validate behavior on the observed design distribution, not on unseen checkpoint metrics. They cannot substitute for Tasks 4-5 validation or Tasks 6-9 protected transfer.
