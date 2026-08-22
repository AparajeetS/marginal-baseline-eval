# Orthogonal Score 192-Group Confirmation

Read `PREREGISTRATION.md` first. This package runs one fixed rule on fresh
known-truth seeds. It never reads protected result ledgers.

```bash
python experiments/25_orthogonal_confirmation_192/run_confirmation.py \
  --output-dir experiments/25_orthogonal_confirmation_192/out \
  --workers 8
```

`FINAL_ELIGIBILITY.json` is binding. A pass is limited to external evaluations
with at least 192 defensible independent units. It never unlocks the existing
24/48-group GPU associations.
