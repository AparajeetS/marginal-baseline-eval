# Metric Taxonomy

This taxonomy groups the current candidate metrics into families. It should be
used for paper tables, figures, and future experiment planning.

## Families

| Family | Metrics | Expected role |
|---|---|---|
| Task-proximal / validation | `val_loss`, `train_loss`, `train_acc`, `metric_batch_loss`, `metric_batch_acc` | Positive-control style metrics close to the objective. These should often survive default MBE and may weaken under strict `val_loss` controls. |
| Confidence / calibration | `confidence_mean`, `entropy_mean`, `margin_mean`, `brier`, `ece`, `logit_norm_mean` | Output-distribution metrics that often track performance directly. Useful as stable comparators. |
| Gradient magnitude | `grad_norm`, `grad_l1`, `grad_linf`, `grad_mean_abs`, `per_sample_grad_norm_mean`, `per_sample_grad_norm_std`, `grad_noise_scale` | Training-state metrics. Some survive strongly; `grad_noise_scale` is more fragile in pooled audits. |
| Fisher magnitude / spectrum | `fisher_trace`, `fisher_spectral`, `fisher_condition`, `fisher_stable_rank`, `fisher_entropy`, `fim_erank`, `fim_norm` | Fisher-derived metrics. FIM_norm is the motivating case study; Fisher magnitude metrics often survive more reliably. |
| Sharpness | `sam_sharpness`, `asam_sharpness`, `hessian_trace_hutchinson`, `hessian_top_eig_power` | Curvature/sharpness proxies. Results are mixed and sensitive to suite/control choices. |
| Feature geometry | `feature_erank`, `feature_erank_norm`, `feature_norm_mean`, `feature_cosine_mean` | Representation metrics. Several wash out or invert in pooled/strict settings. |
| Weight norms | `weight_l1`, `weight_l2`, `weight_linf`, `weight_rms` | Parameter magnitude proxies. Often fragile under MBE, especially pooled default audits. |
| Distance / update | `distance_from_init_l2`, `relative_distance_from_init`, `update_to_weight_ratio` | Training trajectory proxies. Often wash out in default pooled/image audits but can survive in strict or architecture-specific settings. |
| Negative control | `random_metric` | Should remain weak-or-mixed. If it survives, the run needs diagnosis. |

## Current Family-Level Read

The current evidence suggests:

- task-proximal and confidence/calibration metrics are the most stable;
- gradient and Fisher magnitude metrics often survive;
- rank/geometry variants are less stable than magnitude variants;
- feature metrics, weight norms, and distance/update proxies are frequently
  control-sensitive;
- FIM_norm is not uniformly bad, but its conclusion changes across image-only,
  text-only, and pooled image+text audits;
- strict validation-loss controls shift the question from "does this metric
  predict performance?" to "does this metric add information beyond a strong
  validation baseline?"

## Headline Counts From Current 680-Model Runs

Default 680-model pooled audit:

- survives: 19
- washout: 7
- hidden-after-control: 2
- reverse-inversion: 1
- weak-or-mixed: 12

Strict 680-model pooled audit with `val_loss`:

- survives: 26
- washout: 4
- hidden-after-control: 3
- reverse-inversion: 1
- weak-or-mixed: 6

Interpretation:

The strict audit does not simply remove all signal. It changes which families
are being tested as independent contributors beyond validation loss.

## Figure Ideas

CPU-only figures worth generating:

- raw rho vs MBE partial rho scatter, colored by family;
- family-by-class heatmap;
- FIM_norm bar chart across image/text/full pools;
- threshold sensitivity heatmap for class counts;
- default vs strict class transition Sankey/table.
