# Shared Method Comparison

This benchmark uses known-truth balanced factorial ledgers. Scores answer different questions; CMI and rank coefficients are descriptive and are not thresholded as hypothesis tests.

| Scenario | True stable increment | Raw rho | Partial rho | Granulated tau | Jiang CMI | Additive MBE support | Interaction MBE support |
|---|---:|---:|---:|---:|---:|---:|---:|
| independent_null | false | -0.015 | 0.002 | -0.012 | 0.006 | 0.000 | 0.020 |
| design_proxy | false | 0.980 | 0.631 | 0.778 | 0.426 | 0.640 | 0.020 |
| interaction_proxy | false | 0.750 | 0.370 | 0.407 | 0.184 | 0.900 | 0.040 |
| genuine_increment | true | 0.570 | 0.795 | 0.580 | 0.123 | 0.960 | 0.980 |
| axis_specialist_proxy | false | 0.839 | 0.008 | 0.358 | 0.023 | 0.000 | 0.000 |
| sign_flip_increment | false | -0.052 | -0.063 | -0.037 | 0.008 | 0.000 | 0.180 |

The source-faithful robust sign-error statistic is compared with MBE on the Dziugaite et al. public ledger rather than relabeled for this synthetic design. See `../09_published_metric_reaudit/studies/dziugaite2020/out/SOURCE_REPRODUCTION.md`.
