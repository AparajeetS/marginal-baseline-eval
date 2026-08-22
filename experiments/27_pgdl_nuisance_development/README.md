# PGDL Nuisance Development

This experiment develops nuisance fits on synthetic outcomes over the allowed
PGDL Tasks 6-9 design metadata. It never loads a real generalization target or
checkpoint metric.

```bash
python experiments/27_pgdl_nuisance_development/run_development.py \
  experiments/09_published_metric_reaudit/data/pgdl_model_ledger.csv \
  experiments/09_published_metric_reaudit/studies/pgdl2020/metric_plan.json \
  --output-dir experiments/27_pgdl_nuisance_development/out \
  --workers 8
```

This was a development screen, not confirmation. Its selected finalist and
scope are recorded in [DEVELOPMENT_RESULTS.md](DEVELOPMENT_RESULTS.md); the
untouched-seed result is experiment 28.
