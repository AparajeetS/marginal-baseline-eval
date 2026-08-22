# Shared Method Comparison

This benchmark uses known-truth balanced factorial ledgers. Scores answer different questions; CMI and rank coefficients are descriptive and are not thresholded as hypothesis tests.

| Scenario | True stable increment | Raw rho | Partial rho | Granulated tau | Jiang CMI | Additive MBE support | Interaction MBE support |
|---|---:|---:|---:|---:|---:|---:|---:|
| independent_null | false | -0.021 | 0.001 | -0.037 | 0.005 | 0.000 | 0.020 |
| design_proxy | false | 0.977 | 0.637 | 0.778 | 0.412 | 0.740 | 0.040 |
| interaction_proxy | false | 0.734 | 0.381 | 0.457 | 0.169 | 0.880 | 0.000 |
| genuine_increment | true | 0.540 | 0.792 | 0.580 | 0.113 | 0.920 | 0.900 |
| axis_specialist_proxy | false | 0.837 | 0.011 | 0.333 | 0.032 | 0.000 | 0.020 |
| sign_flip_increment | false | -0.043 | -0.098 | -0.049 | 0.006 | 0.000 | 0.080 |

The source-faithful robust sign-error statistic is compared with MBE on the Dziugaite et al. public ledger rather than relabeled for this synthetic design. See `../09_published_metric_reaudit/studies/dziugaite2020/out/SOURCE_REPRODUCTION.md`.
