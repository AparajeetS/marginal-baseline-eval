# Contributing

This is an active research repository. The most useful contributions are
reproducible audits, clearer documentation, and careful negative results.

## Local Setup

```bash
git clone https://github.com/AparajeetS/metric-audit-paper.git
cd metric-audit-paper
pip install -e ".[dev]"
python -m pytest -q
```

## Run The Demo

```bash
mbe-eval-demo --bootstrap 200
```

## Audit Your Own CSV

Your CSV should contain one row per trained model/run, one held-out target, one
or more metric columns, and control columns such as learning rate, optimizer,
architecture, task, and seed.

```bash
mbe-eval-audit \
  --csv runs.csv \
  --metrics fim_norm,val_loss,grad_norm \
  --target final_acc \
  --controls lr,wd,optimizer,arch,seed \
  --output audit_report.md
```

## Experiment Contributions

For new experiment results, include:

- raw CSV or a stable artifact reference;
- exact command used to generate the result;
- metric list;
- control set;
- seed/config grid;
- summary CSV and markdown table;
- checksums for raw artifacts if practical.

Do not change metric lists, thresholds, or control sets after seeing results
unless the change is explicitly labeled exploratory.

## Documentation Contributions

Keep claims scoped:

- say "washout under this control set" rather than "metric is useless";
- separate default MBE from strict validation-loss MBE;
- report random/control metrics;
- include uncertainty where available.
