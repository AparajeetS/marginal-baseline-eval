# MBE Protocol Freeze

> **Legacy MBE 1.0 protocol.** This document is preserved to explain the
> existing pilot artifacts. It is superseded by
> [`docs/MBE_2_RESEARCH_PROGRAM.md`](../MBE_2_RESEARCH_PROGRAM.md) and must
> not be used to launch future compute.

Status: historical draft freeze for the current evidence set.

This document defines the evaluation protocol used for the current
Marginal Baseline Evaluation (MBE) evidence and the protocol that should be
used for the next locked replication. Its purpose is to prevent narrative drift:
future experiments should be judged against these rules before seeing results.

## Unit Of Analysis

Each row is one trained model/run.

Required columns:

- candidate metric columns;
- one held-out target column;
- baseline/control columns describing the training condition.

Current target:

```text
final_acc
```

Higher `final_acc` is better. Metrics where lower is better are not sign-flipped
before auditing; signs are interpreted after correlation.

## Default MBE Controls

The default control set is:

```text
lr, wd, dropout, optimizer, arch, task, seed
```

These controls represent ordinary design variables a reviewer would expect to
explain a large amount of training-run variation.

## Strict MBE Controls

The strict control set adds validation loss:

```text
lr, wd, dropout, optimizer, arch, task, seed, val_loss
```

Strict MBE asks whether a candidate metric has signal beyond both experimental
design variables and a strong task-proximal baseline.

## Primary Statistic

For each metric:

1. compute raw Spearman rank correlation with `final_acc`;
2. compute partial rank correlation with `final_acc` after residualizing ranked
   metric and ranked target against the control design matrix;
3. report the delta:

```text
delta = MBE partial rho - raw Spearman rho
```

Numeric controls are rank transformed. Categorical controls are one-hot encoded
with one dropped level.

## Grouping Rules

Always report:

- pooled result over all rows;
- suite-level result when `suite` exists;
- architecture-level result when `arch` exists.

The primary headline table is the pooled result. Suite and architecture tables
are used to diagnose pooling artifacts and task dependence.

## Classification Rules

Default thresholds:

```text
effect_threshold = 0.20
washout_threshold = 0.10
```

Classification:

| Class | Rule |
|---|---|
| `washout` | `abs(raw_r) >= 0.20` and `abs(partial_r) < 0.10` |
| `sign-inversion` | `raw_r <= -0.20` and `partial_r >= +0.20` |
| `reverse-inversion` | `raw_r >= +0.20` and `partial_r <= -0.20` |
| `hidden-after-control` | `abs(raw_r) < 0.20` and `abs(partial_r) >= 0.20` |
| `survives` | raw and partial have same sign and `abs(partial_r) >= 0.20` |
| `weak-or-mixed` | none of the above |

Inversion classes are not counted as washout. They are stronger warnings and
should be reported separately.

## Uncertainty Protocol

For current saved artifacts, use bootstrap resampling over rows:

```text
bootstrap resamples = 500 for paper tables when time allows
bootstrap resamples = 200 for routine checks
seed = 20260705
```

Report 2.5% and 97.5% quantiles for:

- raw Spearman rho;
- MBE partial rho;
- delta.

For the next locked replication, bootstrap should be run both:

- over individual rows;
- over seed/config blocks when a stable block identifier exists.

## Threshold Sensitivity

For every headline table, recompute class counts under:

```text
effect_threshold in {0.15, 0.20, 0.25}
washout_threshold in {0.05, 0.10, 0.15}
```

The main conclusion should not depend on one threshold pair. A conclusion is
considered robust if the same qualitative story holds for the default threshold
and at least four neighboring settings.

## Positive And Negative Controls

Always include:

- `val_loss` where available as a positive task-proximal control;
- `random_metric` as a negative control.

Expected behavior:

- `val_loss` should usually survive in default MBE;
- `random_metric` should usually remain weak-or-mixed.

If these controls fail, the run should be treated as diagnostic rather than
headline evidence.

## Claims Allowed From Current Evidence

Allowed:

- Raw pooled correlation is insufficient to validate training metrics.
- MBE is selective: it preserves some metrics and weakens or inverts others.
- FIM_norm is task- and pooling-sensitive in the current 680-model evidence set.
- Several feature, weight, distance/update, and sharpness/noise-scale metrics
  are fragile under controls.

Not allowed:

- FIM_norm is universally useless.
- MBE proves causal effects.
- All geometric metrics fail.
- The current evidence is a final submission-ready replication.

## Next Locked Replication

Before launching new GPU runs:

1. freeze metric list;
2. freeze control sets;
3. freeze seed/config grid;
4. freeze classification thresholds;
5. define exclusion criteria for failed runs;
6. precommit output filenames and summary scripts;
7. run without changing narrative after launch.
