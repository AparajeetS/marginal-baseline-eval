# Causal-Text Factorial Sequential Replication: Initial Report

## Scope

This is one corrected WikiText-2 causal-LM environment. It supports a configuration-blocked, refit-aware within-environment MBE analysis. It does not establish transport, a universal metric ranking, or a selector claim across tasks.

## Integrity

- Planned rows: 180
- Completed valid rows: 180
- Error rows: 0
- Distinct configuration interventions: 36
- Repeated seeds per configuration: [5]
- Causal behavioral test: passed

## Inference Guard

The active MBE 2.0 protocol requires at least 30 independent configuration/environment units for the configuration-blocked inference path. This factorial has 36 configuration interventions, so seed-level rows are used only as repeated measurements within those units.

## Negative-Control Finding

`random_metric` is a deterministic Gaussian value derived from the full run ID. It varies across all configuration means and is used as the configuration-level negative control. The earlier seed-only control failure is retained in the previous factorial's artifact record.

## Raw Association With Test NLL

The rows are first averaged within configuration, so this table has 36 independent intervention units rather than 180 seed-level rows. Negative Spearman values correspond to lower test NLL for larger metric values; direction is descriptive only and metric-specific.

| Metric | Raw Spearman | permutation p (descriptive) |
|---|---:|---:|
| prediction_confidence | -0.984 | 0.0010 |
| prediction_margin | -0.968 | 0.0010 |
| distance_from_initialization_l2 | -0.897 | 0.0010 |
| feature_erank | -0.864 | 0.0010 |
| update_to_weight_ratio | -0.780 | 0.0010 |
| relative_distance_from_initialization | -0.769 | 0.0010 |
| random_metric | -0.092 | 0.5480 |
| fim_erank | -0.038 | 0.8230 |
| fim_norm | -0.038 | 0.8330 |
| parameter_l2 | -0.002 | 0.9870 |
| empirical_fisher_trace | 0.106 | 0.5170 |
| gradient_norm | 0.157 | 0.3520 |
| sharpness_random_perturbation | 0.199 | 0.2280 |
| prediction_entropy | 0.979 | 0.0010 |

## Metric-Batch Stability

Each non-random metric was recomputed on three deterministic diagnostic batches per model. The table reports the median within-model batch standard deviation and its ratio to the metric's across-model standard deviation. Smaller ratios indicate less batch sensitivity in this environment.

| Metric | Median batch SD | Batch/Across-model SD |
|---|---:|---:|
| relative_distance_from_initialization | 0 | 0.000 |
| update_to_weight_ratio | 0 | 0.000 |
| parameter_l2 | 0 | 0.000 |
| distance_from_initialization_l2 | 0 | 0.000 |
| feature_erank | 0.0158615 | 0.069 |
| empirical_fisher_trace | 0.886539 | 0.156 |
| gradient_norm | 0.061195 | 0.200 |
| prediction_entropy | 0.154092 | 0.376 |
| prediction_confidence | 0.0149353 | 0.460 |
| prediction_margin | 0.0131143 | 0.469 |
| metric_batch_loss | 0.221671 | 0.490 |
| fim_norm | 0.0175914 | 0.497 |
| fim_erank | 0.140731 | 0.497 |
| metric_batch_accuracy | 0.0206391 | 0.654 |
| sharpness_random_perturbation | 0.00265717 | 0.830 |

## Configuration-Blocked Refit Analysis

For every metric and baseline level, the analysis uses 199 full refit configuration bootstraps and both frozen nuisance families: degree-six ridge and degree-six ridge with pairwise control interactions. A within-environment predictive increment requires the lower refit interval to be above zero for both families. Residual permutation is reported as a secondary diagnostic only.

| Baseline | Metrics with both refit lower intervals above zero | Random control |
|---|---|---|
| B2_training_state | none | no_consensus_increment |

The complete per-metric, per-nuisance-family values are in `refit_analysis.csv` and `refit_consensus.csv`. These are scoped within-environment results, not universal survivor or washout labels.

## Next Evidence Gate

Replicate this exact analysis in a corrected image environment, then test the frozen metric and baseline policy on an external locked holdout. Neither one text environment nor this configuration grid establishes cross-task transport.
