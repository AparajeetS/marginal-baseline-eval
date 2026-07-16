# PGDL Checkpoint Pilot QA

The frozen, outcome-blind pilot contains 24 models from Task 1 and 24 from Task 2. All 48 initialization/final checkpoint pairs aligned by tensor role and shape, and every extracted metric is finite.

Spectral norms use exact singular-value decomposition. Product-style measures are sums of log squared layer norms; biases enter whole-model norms but not layer products or sums.

| Task | Metric | Unique | Min | Median | Max | Descriptive rho |
|---|---|---:|---:|---:|---:|---:|
| task1 | `parameter_count` | 8 | 1.671e+06 | 7.315e+06 | 1.917e+07 | 0.537 |
| task1 | `parameter_l2` | 24 | 17.97 | 31.8 | 69.04 | -0.507 |
| task1 | `initial_parameter_l2` | 24 | 23.14 | 30.8 | 42.6 | -0.751 |
| task1 | `distance_from_initialization_l2` | 24 | 9.439 | 22.85 | 57.6 | -0.710 |
| task1 | `relative_distance_from_initialization` | 24 | 0.2888 | 0.7425 | 1.967 | -0.534 |
| task1 | `update_to_weight_ratio` | 24 | 0.2746 | 0.748 | 1.662 | -0.388 |
| task1 | `frobenius_sum_sq` | 24 | 312 | 1014 | 4732 | -0.492 |
| task1 | `log_frobenius_product_sq` | 24 | 17.74 | 27.37 | 51.99 | -0.721 |
| task1 | `spectral_sum_sq` | 24 | 23.93 | 45.7 | 305.4 | -0.766 |
| task1 | `log_spectral_product_sq` | 24 | 7.059 | 11.31 | 28.16 | -0.851 |
| task2 | `parameter_count` | 3 | 3.43e+06 | 6.315e+06 | 9.2e+06 | -0.904 |
| task2 | `parameter_l2` | 24 | 72.07 | 108.9 | 138.4 | 0.268 |
| task2 | `initial_parameter_l2` | 24 | 50.78 | 64.16 | 75.19 | -0.820 |
| task2 | `distance_from_initialization_l2` | 24 | 57.1 | 72.33 | 152.5 | 0.293 |
| task2 | `relative_distance_from_initialization` | 24 | 0.8307 | 1.028 | 2.392 | 0.544 |
| task2 | `update_to_weight_ratio` | 24 | 0.5454 | 0.7576 | 1.171 | 0.099 |
| task2 | `frobenius_sum_sq` | 24 | 2758 | 1.001e+04 | 1.597e+04 | 0.529 |
| task2 | `log_frobenius_product_sq` | 24 | 43.35 | 62.16 | 85.35 | -0.697 |
| task2 | `spectral_sum_sq` | 24 | 151.9 | 299.5 | 1297 | 0.565 |
| task2 | `log_spectral_product_sq` | 24 | 23.1 | 25.62 | 30.44 | -0.039 |

The correlations are implementation smoke checks, not effect estimates: the pilot has only 24 observations per task and intentionally performs no p-value, confidence-interval, survival, or washout classification. Development inference must use all Tasks 1-2 models after every primary metric implementation is frozen.
