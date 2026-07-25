# Paper Direction

Working title:

> Marginal Baseline Evaluation: Auditing Generalization Metrics Beyond Pooled Correlation

This repository currently supports a methods-first paper about **Marginal Baseline Evaluation (MBE)**. The motivating case study is FIM_norm: a metric that looked plausible under ordinary raw evaluation, then showed task dependence, washout, and sign reversal under stronger audits.

## Current Thesis

Raw pooled correlation is not enough evidence for a generalization metric. A metric should be audited against ordinary baselines and design variables:

- hyperparameters such as learning rate, weight decay, dropout, and optimizer,
- architecture and task,
- seed,
- optional strict baselines such as validation loss.

MBE asks whether a metric keeps marginal predictive signal after those controls. The current evidence shows that MBE is selective: it weakens or reverses several fragile metrics while preserving others.

## Current Evidence Set

The confirmed evidence set contains 680 trained models:

- 480 image models on CIFAR-10: CNN, ResNet, ViT, and WideResNet.
- 200 character-transformer language models.

The central FIM_norm result:

| Audit | n | Raw rho | MBE partial rho | Class |
|---|---:|---:|---:|---|
| Image only, default controls | 480 | -0.662 | -0.218 | survives |
| Image only, strict + val_loss | 480 | -0.662 | -0.383 | survives |
| Text only, default controls | 200 | -0.291 | +0.014 | washout |
| Text only, strict + val_loss | 200 | -0.291 | +0.188 | weak-or-mixed |
| Full 680, default controls | 680 | +0.225 | -0.203 | reverse-inversion |
| Full 680, strict + val_loss | 680 | +0.225 | -0.300 | reverse-inversion |

This should be framed as task and pooling instability, not as a universal claim that FIM_norm is useless.

## What Survives MBE

In the full 680-model strict audit, several metrics survive:

- `fisher_trace`
- `grad_norm`
- `logit_norm_mean`
- `metric_batch_acc`
- `confidence_mean`
- `entropy_mean`

This matters because it shows the audit is not merely destructive. It can distinguish stable predictors from fragile pooled artifacts.

## Claims To Make

- MBE is a reusable audit protocol for generalization metrics.
- Raw pooled correlations can hide washout, inversion, and task dependence.
- FIM_norm is a good-faith metric case study that breaks under stronger evaluation.
- Different metric families behave differently under MBE.

## Claims To Avoid

- Do not claim that FIM_norm is universally useless.
- Do not claim that MBE proves causal effects of metrics.
- Do not claim that all geometric metrics fail.
- Do not overfit the paper around one dramatic table; use the full matrix of outcomes.

## Next Required Evidence

Before a serious submission:

- extend bootstrap confidence intervals to all headline tables,
- add permutation controls and block-level resampling,
- keep classification thresholds frozen unless changes are versioned,
- run one locked holdout replication,
- keep reproduction commands and artifact hashes current,
- decide whether to add one more independent image or text suite.
