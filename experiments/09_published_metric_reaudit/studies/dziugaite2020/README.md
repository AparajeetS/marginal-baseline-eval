# Dziugaite et al. (2020) Reaudit

This is a complementary MBE analysis of the public model ledger from
*In Search of Robust Measures of Generalization*. It is not a reproduction of
the paper's distributionally robust sign-error statistic and cannot invalidate
that paper on its own.

## Provenance

- Paper: <https://arxiv.org/abs/2010.11924>
- Official artifact: <https://github.com/nitarshan/robust-generalization-measures>
- Source file: `data/nin.cifar10_svhn.csv`
- Source SHA-256: `1fc11e07bd3826cbf887004c1d5cbf5450102a34bd99d368f05a5c1cd603a9fc`
- Upstream license: Apache-2.0
- Original ledger: 10,000 trained models, 1,000 configurations, 10 repeats
  per configuration, split across CIFAR-10 and SVHN.

## Preparation

The preparation script mirrors the official `load_data` rules: retain
`is.converged`, retain `is.high_train_accuracy`, remove rows containing any
NaN or infinity, and round learning rate to four decimals. This leaves 9,700
runs across all 1,000 configurations (4,986 CIFAR-10 and 4,714 SVHN).

```bash
python experiments/09_published_metric_reaudit/prepare_dziugaite2020.py \
  experiments/09_published_metric_reaudit/data/dziugaite2020/nin.cifar10_svhn.csv \
  experiments/09_published_metric_reaudit/data/dziugaite2020/nin.cifar10_svhn_reaudit.csv
```

The source and prepared ledgers are intentionally ignored by Git. The frozen
manifest, transformation code, provenance, and result tables are versioned.

## Audit Questions

`B1_design` asks whether each measure adds information beyond the five
experimental design variables. `B2_training_state` additionally conditions on
training cross-entropy, training accuracy, and epoch. Since training accuracy
is part of the definition of generalization gap, B2 is a deliberately strict
sensitivity analysis, not a causal adjustment set.

All 32 `complexity.*` columns are included. Cross-fitting is grouped by the
upstream `experiment_id`, so repeats of a configuration never straddle train
and test folds. Residual association and permutation inference operate on
configuration means, and predictive error gives every configuration equal
weight. The run-level residual correlation is retained in the CSV as a
descriptive diagnostic. Results are reported pooled and separately for
CIFAR-10 and SVHN. No metric is omitted based on its result.

## Run

```bash
python experiments/09_published_metric_reaudit/run_reaudit.py \
  experiments/09_published_metric_reaudit/studies/dziugaite2020/manifest.json \
  --output-prefix experiments/09_published_metric_reaudit/studies/dziugaite2020/out/reaudit \
  --permutations 199 --bootstrap 499 --seed 2026
```

Reproduce the paper's Figure 1 statistic and verify it against the published
environment counts and complete measure ordering:

```bash
python experiments/09_published_metric_reaudit/studies/dziugaite2020/reproduce_source.py \
  experiments/09_published_metric_reaudit/data/dziugaite2020/nin.cifar10_svhn_reaudit.csv \
  --output-dir experiments/09_published_metric_reaudit/studies/dziugaite2020/out

python experiments/09_published_metric_reaudit/studies/dziugaite2020/compare_source_mbe.py \
  experiments/09_published_metric_reaudit/studies/dziugaite2020/out/source_sign_error_summary.csv \
  experiments/09_published_metric_reaudit/studies/dziugaite2020/out/reaudit.csv \
  --output-dir experiments/09_published_metric_reaudit/studies/dziugaite2020/out
```
