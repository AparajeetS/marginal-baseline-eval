# PGDL Transfer Confirmation V2

Untouched-seed confirmation of the experiment 27 finalist. The runner imports
the hashed experiment 26 PGDL metadata adapter and synthetic generator, then
overrides only the preregistered protocol namespace, degree, and ridge penalty.

```bash
python experiments/28_pgdl_transfer_confirmation_v2/run_confirmation.py \
  experiments/09_published_metric_reaudit/data/pgdl_model_ledger.csv \
  experiments/09_published_metric_reaudit/studies/pgdl2020/metric_plan.json \
  --output-dir experiments/28_pgdl_transfer_confirmation_v2/out \
  --workers 8
```

The corrected confirmation completed after a documented Windows worker
initialization recovery. B1 and B2 passed; B3 narrowly missed the frozen power
gate. See `CONFIRMATION_RESULTS.md`. Protected associations remain sealed.
