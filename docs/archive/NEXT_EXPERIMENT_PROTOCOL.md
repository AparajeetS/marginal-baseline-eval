# Next Experiment Protocol

> **Superseded MBE 1.0 plan.** Do not launch this experiment. The active design
> is [`docs/MBE_2_RESEARCH_PROGRAM.md`](../MBE_2_RESEARCH_PROGRAM.md), with
> gates in [`ROADMAP.md`](../../ROADMAP.md).

Status: historical pre-registration draft.

This protocol should be frozen before launching new compute.

## Goal

Test whether the current MBE findings replicate under a locked holdout design.

Primary questions:

1. Does FIM_norm remain task- and pooling-sensitive?
2. Do feature, weight, distance/update, and sharpness/noise-scale proxies remain
   fragile under MBE?
3. Do confidence, task-proximal, and gradient/Fisher magnitude metrics continue
   to survive more often?
4. Does the random metric remain weak?

## Design

Run fresh training sweeps that do not reuse the current Kaggle result rows.

Minimum target:

- 480 image runs:
  - CNN;
  - ResNet;
  - ViT;
  - WideResNet.
- 200 text runs:
  - character-transformer language models.

Preferred target if compute allows:

- 800 to 1,200 total runs with balanced architecture/task blocks.

## Frozen Controls

Default controls:

```text
lr, wd, dropout, optimizer, arch, task, seed
```

Strict controls:

```text
lr, wd, dropout, optimizer, arch, task, seed, val_loss
```

## Frozen Classification

Use the thresholds in `PROTOCOL_FREEZE.md`:

```text
effect_threshold = 0.20
washout_threshold = 0.10
```

Also report threshold sensitivity:

```text
effect_threshold in {0.15, 0.20, 0.25}
washout_threshold in {0.05, 0.10, 0.15}
```

## Frozen Metric Families

Use `METRIC_TAXONOMY.md`.

Required metrics:

- validation/task-proximal metrics;
- confidence/calibration metrics;
- gradient magnitude metrics;
- Fisher magnitude/spectrum metrics;
- FIM_norm and related Fisher-rank metrics;
- sharpness metrics;
- feature geometry metrics;
- weight norms;
- distance/update metrics;
- random metric.

## Required Outputs

For each run:

- raw result CSV;
- audit summary CSV and markdown;
- strict audit summary CSV and markdown;
- bootstrap CI table;
- threshold sensitivity table;
- figure bundle;
- SHA256 hashes for raw CSVs.

## Success Criteria

The replication supports the current paper direction if:

- random metric remains weak-or-mixed;
- MBE preserves a nontrivial set of metrics;
- at least one fragile family shows repeated washout/inversion under controls;
- FIM_norm remains context-sensitive across image/text/full pools;
- conclusions are stable across nearby threshold settings.

The replication weakens the current story if:

- random metric often survives;
- all metrics survive or all metrics fail;
- FIM_norm becomes uniformly stable across tasks and pools;
- class counts change drastically under minor threshold changes.

## No Narrative Tuning Rule

After launch:

- do not change metric list;
- do not change controls;
- do not change thresholds;
- do not drop failed runs unless they meet pre-declared failure criteria;
- report results even if they weaken the current story.
