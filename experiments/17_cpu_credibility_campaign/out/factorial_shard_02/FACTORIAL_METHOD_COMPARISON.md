# Shared Method Comparison

This benchmark uses known-truth balanced factorial ledgers. Scores answer different questions; CMI and rank coefficients are descriptive and are not thresholded as hypothesis tests.

| Scenario | True stable increment | Raw rho | Partial rho | Granulated tau | Jiang CMI | Additive MBE support | Interaction MBE support |
|---|---:|---:|---:|---:|---:|---:|---:|
| independent_null | false | -0.064 | 0.012 | -0.037 | 0.005 | 0.000 | 0.000 |
| design_proxy | false | 0.979 | 0.640 | 0.778 | 0.473 | 0.640 | 0.080 |
| interaction_proxy | false | 0.766 | 0.375 | 0.481 | 0.178 | 0.900 | 0.020 |
| genuine_increment | true | 0.590 | 0.765 | 0.580 | 0.123 | 0.940 | 0.960 |
| axis_specialist_proxy | false | 0.837 | 0.010 | 0.333 | 0.028 | 0.020 | 0.000 |
| sign_flip_increment | false | -0.029 | -0.051 | -0.037 | 0.007 | 0.020 | 0.200 |

The source-faithful robust sign-error statistic is compared with MBE on the Dziugaite et al. public ledger rather than relabeled for this synthetic design. See `../09_published_metric_reaudit/studies/dziugaite2020/out/SOURCE_REPRODUCTION.md`.
