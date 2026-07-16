# Source Statistic Reproduction and MBE Comparison

## Reproduction Checksum

The reconstruction exactly matches published Figure 1 on all externally visible checks:

- 9,242 directed environments overall;
- 2,418 learning-rate, 2,538 depth, 328 width, 2,972 training-size, and 986 dataset environments;
- the complete ordering of all 24 plotted measures by mean sign error;
- maximum sign error of 1.0 for every measure.

The original paper therefore reproduces under its public code, public data, ESS threshold 12, and noise filtering.

## Cross-Method Association

Spearman correlations between source mean sign error (lower is better) and MBE quantities:

| MBE quantity | Rank correlation |
|---|---:|
| `raw_r` | -0.747 |
| `partial_r` | -0.590 |
| `crossfit_residual_r` | -0.424 |
| `delta_mse` | -0.003 |
| `relative_mse_improvement` | 0.015 |

Source average sign error and raw association broadly agree, but source ranking is nearly unrelated to MBE out-of-fold predictive increment. The methods are measuring different desirable properties: intervention-wise directional robustness versus information beyond a marginal design baseline.

## Best Source Mean Sign Error

| Rank | Measure | Mean error | P90 error | MBE residual rho | Delta MSE |
|---:|---|---:|---:|---:|---:|
| 1 | `complexity.pacbayes_orig` | 0.097 | 0.360 | 0.588 | 0.0066 |
| 2 | `complexity.pacbayes_flatness` | 0.102 | 0.507 | 0.580 | 0.0060 |
| 3 | `complexity.pacbayes_init` | 0.106 | 0.819 | 0.641 | 0.0096 |
| 4 | `complexity.path_norm_over_margin` | 0.122 | 0.990 | 0.337 | 0.0069 |
| 5 | `complexity.pacbayes_mag_flatness` | 0.126 | 0.520 | 0.631 | 0.0085 |
| 6 | `complexity.path_norm` | 0.127 | 1.000 | 0.319 | 0.0068 |
| 7 | `complexity.fro_dist` | 0.140 | 1.000 | 0.590 | 0.0074 |
| 8 | `complexity.log_sum_of_fro` | 0.162 | 1.000 | 0.284 | 0.0017 |
| 9 | `complexity.param_norm` | 0.179 | 1.000 | 0.471 | 0.0039 |
| 10 | `complexity.log_sum_of_fro_over_margin` | 0.186 | 1.000 | 0.262 | 0.0013 |

## Interpretation

There is no contradiction between the source result that every measure fails perfectly in at least one environment and the MBE result that most measures retain incremental information on average. A metric can be informative across the model population while failing catastrophically under a particular intervention. Conversely, a low average sign error does not guarantee useful out-of-fold increment beyond cheap controls.

This comparison strengthens the audit-protocol narrative and weakens any blanket claim that established metrics are simply empty.
