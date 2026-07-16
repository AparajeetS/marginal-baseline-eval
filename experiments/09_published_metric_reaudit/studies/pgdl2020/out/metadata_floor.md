# PGDL Metadata Baseline Floor

This table measures final training loss beyond each task's declared hyperparameters. It contains no checkpoint-derived metric results and does not open the protected holdout metric evaluation.

| Task | Split | Nuisance | Degree | n | Hyperparameter MSE | + train-loss MSE | Delta MSE [95% CI] | Residual rho [95% CI] | Evidence |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| task1 | development | polynomial_ridge | 4 | 96 | 0.0128 | 0.0124 | 0.0004 [-0.0010, 0.0021] | 0.020 [-0.155, 0.215] | no-supported-increment |
| task1 | development | polynomial_ridge | 6 | 96 | 0.0157 | 0.0156 | 0.0001 [-0.0017, 0.0021] | 0.068 [-0.096, 0.254] | no-supported-increment |
| task1 | development | polynomial_ridge_interactions | 6 | 96 | 0.0090 | 0.0086 | 0.0004 [-0.0021, 0.0026] | 0.407 [0.237, 0.554] | residual-dependence-only |
| task2 | development | polynomial_ridge | 4 | 54 | 0.0074 | 0.0080 | -0.0006 [-0.0019, 0.0005] | 0.145 [-0.140, 0.400] | no-supported-increment |
| task2 | development | polynomial_ridge | 6 | 54 | 0.0073 | 0.0085 | -0.0012 [-0.0025, 0.0003] | 0.138 [-0.136, 0.396] | no-supported-increment |
| task2 | development | polynomial_ridge_interactions | 6 | 54 | 0.0092 | 0.0083 | 0.0009 [-0.0012, 0.0035] | -0.004 [-0.260, 0.284] | no-supported-increment |
| task4 | validation | polynomial_ridge | 4 | 96 | 0.0185 | 0.0194 | -0.0009 [-0.0036, 0.0014] | 0.103 [-0.117, 0.285] | no-supported-increment |
| task4 | validation | polynomial_ridge | 6 | 96 | 0.0200 | 0.0206 | -0.0006 [-0.0040, 0.0027] | 0.134 [-0.069, 0.312] | no-supported-increment |
| task4 | validation | polynomial_ridge_interactions | 6 | 96 | 0.0177 | 0.0156 | 0.0020 [-0.0018, 0.0054] | 0.125 [-0.065, 0.321] | no-supported-increment |
| task5 | validation | polynomial_ridge | 4 | 64 | 0.0812 | 0.0839 | -0.0027 [-0.0161, 0.0108] | 0.079 [-0.141, 0.301] | no-supported-increment |
| task5 | validation | polynomial_ridge | 6 | 64 | 0.0731 | 0.0714 | 0.0017 [-0.0129, 0.0135] | 0.056 [-0.181, 0.286] | no-supported-increment |
| task5 | validation | polynomial_ridge_interactions | 6 | 64 | 0.0635 | 0.0775 | -0.0140 [-0.0366, 0.0094] | 0.195 [-0.038, 0.443] | no-supported-increment |
| task6 | holdout | polynomial_ridge | 4 | 96 | 0.0122 | 0.0122 | 0.0000 [-0.0017, 0.0017] | -0.110 [-0.292, 0.067] | no-supported-increment |
| task6 | holdout | polynomial_ridge | 6 | 96 | 0.0146 | 0.0138 | 0.0008 [-0.0015, 0.0035] | -0.164 [-0.338, -0.001] | no-supported-increment |
| task6 | holdout | polynomial_ridge_interactions | 6 | 96 | 0.0070 | 0.0079 | -0.0009 [-0.0021, 0.0000] | 0.099 [-0.058, 0.283] | no-supported-increment |
| task7 | holdout | polynomial_ridge | 4 | 48 | 0.0463 | 0.0472 | -0.0009 [-0.0080, 0.0058] | 0.297 [0.011, 0.517] | residual-dependence-only |
| task7 | holdout | polynomial_ridge | 6 | 48 | 0.0511 | 0.0504 | 0.0007 [-0.0083, 0.0106] | 0.435 [0.176, 0.639] | residual-dependence-only |
| task7 | holdout | polynomial_ridge_interactions | 6 | 48 | 0.0462 | 0.0726 | -0.0264 [-0.0551, -0.0005] | 0.502 [0.304, 0.684] | residual-dependence-only |
| task8 | holdout | polynomial_ridge | 4 | 64 | 0.0464 | 0.0474 | -0.0010 [-0.0076, 0.0053] | 0.223 [-0.010, 0.479] | no-supported-increment |
| task8 | holdout | polynomial_ridge | 6 | 64 | 0.0391 | 0.0395 | -0.0004 [-0.0080, 0.0074] | 0.241 [0.011, 0.489] | residual-dependence-only |
| task8 | holdout | polynomial_ridge_interactions | 6 | 64 | 0.0492 | 0.0574 | -0.0082 [-0.0245, 0.0067] | 0.387 [0.166, 0.598] | residual-dependence-only |
| task9 | holdout | polynomial_ridge | 4 | 32 | 0.0157 | 0.0203 | -0.0046 [-0.0112, 0.0010] | 0.199 [-0.147, 0.600] | no-supported-increment |
| task9 | holdout | polynomial_ridge | 6 | 32 | 0.0144 | 0.0155 | -0.0011 [-0.0054, 0.0035] | 0.166 [-0.148, 0.507] | no-supported-increment |
| task9 | holdout | polynomial_ridge_interactions | 6 | 32 | 0.0144 | 0.0245 | -0.0101 [-0.0212, -0.0003] | 0.087 [-0.229, 0.404] | no-supported-increment |

Training accuracy is not tested as a candidate because it is part of the accuracy-gap target. Hyperparameter MSE is an out-of-fold rank-target error, so it is a benchmark floor rather than an estimate in original accuracy units.
