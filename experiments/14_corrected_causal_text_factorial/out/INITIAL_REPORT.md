# Corrected Causal-Text Factorial: Initial Report

## Scope

This is one corrected WikiText-2 causal-LM environment. It supports pipeline validation, measurement-reliability reporting, and descriptive within-environment associations. It does not establish transport, a universal metric ranking, or an inferential MBE survivor/washout label.

## Integrity

- Planned rows: 100
- Completed valid rows: 100
- Error rows: 0
- Distinct configuration interventions: 20
- Repeated seeds per configuration: [5]
- Causal behavioral test: passed

## Inference Guard

The active MBE 2.0 protocol abstains below 30 independent configuration/environment units. This experiment has 20 configuration interventions (two sizes times ten training settings), so seed-level rows must not be treated as 100 independent observations. No metric receives an inferential increment-supported or washout label from this run.

## Negative-Control Finding

`random_metric` was generated from the repeated seed ID only. Its values therefore average to the same constant in every configuration and cannot serve as a configuration-level negative control. This is an implementation failure in the control metric, not evidence about the trained models or the other metric values. A new factorial will derive the random control from the full run ID and retain this failure in its ledger.

## Raw Association With Test NLL

The rows are first averaged within configuration, so this table has 20 independent intervention units rather than 100 seed-level rows. Negative Spearman values correspond to lower test NLL for larger metric values; direction is descriptive only and metric-specific.

| Metric | Raw Spearman | permutation p (descriptive) |
|---|---:|---:|
| prediction_confidence | -0.976 | 0.0010 |
| prediction_margin | -0.962 | 0.0010 |
| distance_from_initialization_l2 | -0.875 | 0.0010 |
| feature_erank | -0.821 | 0.0010 |
| relative_distance_from_initialization | -0.728 | 0.0020 |
| update_to_weight_ratio | -0.710 | 0.0030 |
| fim_norm | -0.281 | 0.2480 |
| fim_erank | -0.281 | 0.2120 |
| parameter_l2 | -0.015 | 0.9540 |
| empirical_fisher_trace | 0.012 | 0.9800 |
| gradient_norm | 0.021 | 0.9360 |
| sharpness_random_perturbation | 0.266 | 0.2710 |
| prediction_entropy | 0.965 | 0.0010 |
| random_metric | nan | nan |

## Metric-Batch Stability

Each non-random metric was recomputed on three deterministic diagnostic batches per model. The table reports the median within-model batch standard deviation and its ratio to the metric's across-model standard deviation. Smaller ratios indicate less batch sensitivity in this environment.

| Metric | Median batch SD | Batch/Across-model SD |
|---|---:|---:|
| relative_distance_from_initialization | 0 | 0.000 |
| update_to_weight_ratio | 0 | 0.000 |
| parameter_l2 | 0 | 0.000 |
| distance_from_initialization_l2 | 0 | 0.000 |
| feature_erank | 0.0163083 | 0.123 |
| empirical_fisher_trace | 0.803999 | 0.152 |
| prediction_entropy | 0.0625865 | 0.170 |
| gradient_norm | 0.0696996 | 0.235 |
| prediction_confidence | 0.00969376 | 0.302 |
| prediction_margin | 0.00965527 | 0.345 |
| metric_batch_loss | 0.148642 | 0.347 |
| fim_norm | 0.0191872 | 0.605 |
| fim_erank | 0.153497 | 0.605 |
| metric_batch_accuracy | 0.0246018 | 0.696 |
| sharpness_random_perturbation | 0.00290894 | 1.065 |

## Next Evidence Gate

Run a preregistered extension with at least six additional configurations per model size (32 independent configurations total), then apply the frozen full-refit, configuration-blocked MBE analysis. The extension is a new sequential replication and must not be pooled as though its settings were chosen before observing this report.
