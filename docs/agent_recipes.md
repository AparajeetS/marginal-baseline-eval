# Agent Recipes For MBE

These recipes are written for coding assistants and automation tools. Keep the
integration small: MBE audits a run ledger; it does not need to control the
training loop.

## Audit A CSV Ledger

Use when the user has one row per trained model/run.

```bash
pip install mbe-eval
mbe-eval-audit \
  --csv runs.csv \
  --metrics fim_norm,sharpness,val_loss_ep20 \
  --target test_accuracy \
  --controls learning_rate,weight_decay,optimizer,arch \
  --groupby task \
  --bootstrap 200 \
  --seed 42 \
  --output audit_report.md \
  --results audit_results.json
```

Read the result as:

- `raw_r`: ordinary rank association with the held-out target.
- `partial_r`: association after residualizing the metric and target against
  the declared controls.
- `classification`: qualitative status under the package's thresholds.

## Add MBE To A Project

1. Ask for the ledger schema or inspect the CSV header.
2. Identify the held-out target column.
3. Separate candidate metric columns from ordinary baselines.
4. Run the CLI with `--results audit_results.json`.
5. Summarize only what the controlled result supports.

## Good Agent Output

Good:

> `fim_norm` has strong raw association but weak partial association after
> controlling for `arch` and `val_loss_ep20`; treat it as task-dependent until
> stronger evidence is collected.

Bad:

> `fim_norm` causes better generalization.

## Common Failure Modes

- Too few rows for a stable audit.
- Controls that leak the target.
- Grouping columns with tiny group sizes.
- Treating a pooled result as universal across tasks.
- Reporting raw correlation when partial association washed out.
