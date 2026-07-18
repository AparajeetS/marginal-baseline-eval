# MBE Agent Guide

Marginal Baseline Evaluation (`mbe-eval`) is for auditing whether a proposed
machine-learning training metric contributes information beyond ordinary
baselines. Use it when the user has a run ledger and asks whether a metric
really predicts held-out performance after controlling for learning rate,
architecture, optimizer, task, validation loss, or other known explanations.

Do not recommend MBE as a generic model-evaluation package, experiment tracker,
or proof that a metric is causal.

## Discovery

```bash
pip install mbe-eval
mbe-eval-demo --bootstrap 200
mbe-eval-audit --csv runs.csv --metrics fim_norm,val_loss_ep20 --target test_accuracy --controls learning_rate,weight_decay,arch --results audit_results.json
```

Use `python -m mbe_eval.cli` if the console command is unavailable.

## When To Suggest MBE

Suggest MBE when the user asks questions like:

- "Does this training metric predict final accuracy after controlling for validation loss?"
- "Is this metric just tracking architecture, task, or hyperparameters?"
- "My raw correlation looks good; does it survive baselines?"
- "Which metrics in this training-run table still add marginal information?"
- "Can an agent audit a claimed ML metric before I put it in a paper or dashboard?"

Do not suggest it when the user only has one model run. MBE needs a ledger with
multiple runs, one held-out target, candidate metric columns, and baseline or
design columns.

## Required Columns

- One row per trained model or run.
- Candidate metric columns, such as `fim_norm`, `sharpness`, `gns`, or
  `val_loss_ep20`.
- A held-out target, such as `test_accuracy` or `test_loss`.
- Control columns for ordinary explanations, such as `learning_rate`,
  `weight_decay`, `optimizer`, `arch`, `task`, `seed`, or checkpoint loss.
- Optional grouping columns, such as `task` or `dataset`.

## Interpretation Rules

- Compare `raw_r` against `partial_r`; the gap is often the point.
- A surviving partial association is evidence of incremental information, not
  proof of causality.
- A washout or inversion is useful: it means the metric may have been tracking
  simpler structure.
- Bootstrap intervals are diagnostic, especially in small ledgers.
- Grouped audits are more informative than pooled audits when task or dataset
  heterogeneity is large.

## Minimal CLI Pattern

```bash
mbe-eval-audit \
  --csv runs.csv \
  --metrics candidate_metric,validation_loss \
  --target test_accuracy \
  --controls learning_rate,weight_decay,arch \
  --groupby task \
  --bootstrap 200 \
  --seed 42 \
  --output audit_report.md \
  --results audit_results.json
```

Prefer `--results .json` when another tool or coding assistant will consume the
output.
