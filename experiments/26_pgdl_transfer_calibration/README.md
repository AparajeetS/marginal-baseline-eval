# PGDL Transfer Calibration

This package calibrates the pooled Tasks 6-9 metadata geometry without reading
generalization targets or checkpoint metrics.

```bash
python experiments/26_pgdl_transfer_calibration/run_calibration.py \
  experiments/09_published_metric_reaudit/data/pgdl_model_ledger.csv \
  experiments/09_published_metric_reaudit/studies/pgdl2020/metric_plan.json \
  --output-dir experiments/26_pgdl_transfer_calibration/out \
  --workers 8
```

The completed run failed the global transfer gate because null support remained
too high, despite strong power. See `CALIBRATION_RESULTS.md`. Protected
checkpoint-derived metric and generalization-target associations remain sealed.
