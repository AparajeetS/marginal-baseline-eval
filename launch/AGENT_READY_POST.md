# MBE for auditing ML metric claims

Raw correlation is a weak test for a training metric.

A metric can look predictive because it tracks architecture, learning rate,
task, optimizer, validation loss, or checkpoint state. Marginal Baseline
Evaluation asks the more useful question:

> Does this metric still predict held-out performance after the obvious
> baselines are controlled?

Install:

```bash
pip install mbe-eval
```

Audit a CSV ledger:

```bash
mbe-eval-audit \
  --csv runs.csv \
  --metrics fim_norm,sharpness,val_loss_ep20 \
  --target test_accuracy \
  --controls learning_rate,weight_decay,optimizer,arch \
  --groupby task \
  --bootstrap 200 \
  --results audit_results.json \
  --output audit_report.md
```

For AI coding assistants, the repo now includes `llms.txt`, `AGENTS.md`, JSON
output, and a tiny CSV example that runs without PyTorch:

```bash
python examples/03_agent_csv_audit.py
```

The important output is the comparison between raw rank association and
controlled partial rank association. A metric that survives controls may be
useful in that environment. A metric that washes out or inverts should not be
marketed as generally predictive from the raw correlation alone.

Limitations: MBE needs multiple runs, explicit controls, and careful grouping.
It does not prove causality or universal metric reliability.

Source: https://github.com/AparajeetS/marginal-baseline-eval
PyPI: https://pypi.org/project/mbe-eval/
