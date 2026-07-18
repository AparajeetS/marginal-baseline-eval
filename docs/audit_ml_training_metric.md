# How To Audit An ML Training Metric

Use this guide when a training metric looks predictive and you want to know
whether it adds information beyond ordinary baselines.

## 1. Build A Run Ledger

Create a CSV with one row per trained model or run.

Required columns:

- candidate metrics, such as `fim_norm`, `sharpness`, `gns`, or
  `val_loss_ep20`;
- one held-out target, such as `test_accuracy` or `test_loss`;
- ordinary controls, such as `learning_rate`, `weight_decay`, `optimizer`,
  `arch`, `task`, `seed`, or checkpoint loss.

## 2. Run MBE

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

## 3. Compare Raw And Controlled Signal

The central question is not "is the raw correlation large?" The question is:

> Does the metric still predict the target after the ordinary explanations are
> controlled?

If `raw_r` is large and `partial_r` is small, the metric may mostly be tracking
the controls. If the sign flips, the pooled claim may be misleading.

## 4. Report The Boundary

Write down:

- target column;
- controls;
- grouping columns;
- number of runs;
- candidate metrics;
- whether each metric survived, washed out, or inverted.

Do not generalize beyond the environments in the ledger.
