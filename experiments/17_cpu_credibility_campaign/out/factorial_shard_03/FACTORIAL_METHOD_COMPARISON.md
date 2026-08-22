# Shared Method Comparison

This benchmark uses known-truth balanced factorial ledgers. Scores answer different questions; CMI and rank coefficients are descriptive and are not thresholded as hypothesis tests.

| Scenario | True stable increment | Raw rho | Partial rho | Granulated tau | Jiang CMI | Additive MBE support | Interaction MBE support |
|---|---:|---:|---:|---:|---:|---:|---:|
| independent_null | false | 0.006 | -0.017 | 0.025 | 0.003 | 0.000 | 0.000 |
| design_proxy | false | 0.978 | 0.617 | 0.778 | 0.419 | 0.680 | 0.080 |
| interaction_proxy | false | 0.743 | 0.370 | 0.432 | 0.171 | 0.900 | 0.020 |
| genuine_increment | true | 0.554 | 0.786 | 0.568 | 0.116 | 0.960 | 0.880 |
| axis_specialist_proxy | false | 0.841 | 0.028 | 0.358 | 0.033 | 0.000 | 0.000 |
| sign_flip_increment | false | -0.061 | -0.036 | -0.037 | 0.006 | 0.000 | 0.060 |

The source-faithful robust sign-error statistic is compared with MBE on the Dziugaite et al. public ledger rather than relabeled for this synthetic design. See `../09_published_metric_reaudit/studies/dziugaite2020/out/SOURCE_REPRODUCTION.md`.
