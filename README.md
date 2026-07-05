# Marginal Baseline Evaluation

[![PyPI](https://img.shields.io/pypi/v/mbe-eval.svg)](https://pypi.org/project/mbe-eval/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Marginal Baseline Evaluation (MBE)** is an audit protocol for testing whether
machine-learning training metrics still predict held-out performance after
controlling for ordinary baselines such as learning rate, weight decay,
optimizer, architecture, task, seed, and validation loss.

The project started from a concrete failure mode: a proposed metric can look
promising under raw pooled correlation while actually tracking easier baselines,
training loss, architecture mix, or other design variables. MBE makes that
failure visible by comparing raw association against controlled partial
rank-correlation.

## Current Status

This is an active research direction with an accompanying Python package,
Kaggle-scale experiment artifacts, and a public walkthrough notebook.

- Package: [`mbe-eval`](https://pypi.org/project/mbe-eval/)
- Public notebook: [Audit ML Training Metrics with MBE](https://www.kaggle.com/code/aparajeetshadangi/audit-ml-training-metrics-with-mbe)
- Documentation map: [docs/README.md](docs/README.md)
- Evidence ledger: [SUPPORTING_EVIDENCE.md](SUPPORTING_EVIDENCE.md)
- Reproducibility notes: [REPRODUCIBILITY.md](REPRODUCIBILITY.md)
- Protocol freeze: [PROTOCOL_FREEZE.md](PROTOCOL_FREEZE.md)
- Metric taxonomy: [METRIC_TAXONOMY.md](METRIC_TAXONOMY.md)
- Figures: [FIGURES.md](FIGURES.md)
- Project brief: [PROJECT_BRIEF.md](PROJECT_BRIEF.md)
- Next experiment protocol: [NEXT_EXPERIMENT_PROTOCOL.md](NEXT_EXPERIMENT_PROTOCOL.md)
- Paper skeleton: [PAPER_SKELETON.md](PAPER_SKELETON.md)
- Paper notes: [PAPER.md](PAPER.md) and [JMLR_STRATEGY.md](JMLR_STRATEGY.md)
- Contribution guide: [CONTRIBUTING.md](CONTRIBUTING.md)
- Roadmap: [ROADMAP.md](ROADMAP.md)

The latest confirmed evidence set contains **680 trained models**:

- 480 CIFAR-10 image models across CNN, ResNet, ViT, and WideResNet settings.
- 200 character-transformer language models.
- 40+ candidate metrics including gradient/Fisher metrics, feature metrics,
  confidence/calibration metrics, sharpness metrics, weight norms, and
  distance/update proxies.

## What The Evidence Suggests

The current Kaggle-scale runs support a selective audit story:

- MBE does **not** destroy every metric.
- Several validation, confidence/logit, gradient/Fisher magnitude, and
  task-proximal metrics survive.
- Several feature-rank, weight-norm, distance/update, and sharpness/noise-scale
  metrics weaken, wash out, or invert under controls.
- FIM_norm is the motivating case study: it looked promising under conventional
  metric validation, then became task-dependent under MBE.

FIM_norm summary from the current confirmed pool:

| Audit | n | Raw rho | MBE partial rho | Class |
|---|---:|---:|---:|---|
| Image only, default controls | 480 | -0.662 | -0.218 | survives |
| Image only, strict + validation loss | 480 | -0.662 | -0.383 | survives |
| Text only, default controls | 200 | -0.291 | +0.014 | washout |
| Text only, strict + validation loss | 200 | -0.291 | +0.188 | weak-or-mixed |
| Full image+text pool, default controls | 680 | +0.225 | -0.203 | reverse-inversion |
| Full image+text pool, strict + validation loss | 680 | +0.225 | -0.300 | reverse-inversion |

Full result tables and interpretation are in
[SUPPORTING_EVIDENCE.md](SUPPORTING_EVIDENCE.md).
CPU-only bootstrap confidence intervals and threshold sensitivity are in
[experiments/07_jmlr_scale/no_compute_outputs/NO_COMPUTE_UNCERTAINTY.md](experiments/07_jmlr_scale/no_compute_outputs/NO_COMPUTE_UNCERTAINTY.md).

## Install

```bash
pip install mbe-eval
```

Optional FIM_norm extraction utilities require PyTorch:

```bash
pip install "mbe-eval[torch]"
```

For local development:

```bash
git clone https://github.com/AparajeetS/metric-audit-paper.git
cd metric-audit-paper
pip install -e ".[dev]"
```

## Try It In One Command

After installation:

```bash
mbe-eval-demo --bootstrap 200
```

This runs a CPU-only synthetic audit, prints the MBE table, and writes
`mbe_demo_report.md`. The demo is intentionally small; replace the synthetic
dataframe with your training-run ledger for real experiments.
Use `--no-output` if you only want the printed table.

To audit your own CSV ledger:

```bash
mbe-eval-audit \
  --csv runs.csv \
  --metrics fim_norm,val_loss_ep20,grad_norm \
  --target test_accuracy \
  --controls learning_rate,weight_decay,optimizer,arch,seed \
  --bootstrap 200 \
  --output audit_report.md
```

## Basic API

```python
import pandas as pd
from mbe_eval import audit_metrics, audit_report_markdown

df = pd.DataFrame(
    {
        "fim_norm": [0.42, 0.51, 0.37, 0.65, 0.62, 0.35],
        "val_loss_ep20": [1.2, 0.9, 1.4, 0.7, 0.8, 1.5],
        "learning_rate": [1e-3, 1e-3, 3e-4, 3e-4, 1e-4, 1e-4],
        "arch": ["cnn", "cnn", "resnet", "resnet", "vit", "vit"],
        "test_accuracy": [0.71, 0.78, 0.68, 0.82, 0.80, 0.66],
    }
)

report = audit_metrics(
    df,
    metrics=["fim_norm", "val_loss_ep20"],
    target="test_accuracy",
    controls=["learning_rate", "arch"],
    bootstrap=100,
)

print(report[["metric", "raw_r", "partial_r", "classification"]])
print(audit_report_markdown(report, target="test_accuracy", controls=["learning_rate", "arch"]))
```

Your dataframe should have one row per trained model/run, one held-out target,
candidate metric columns, and baseline/design columns to control.

## Reproduce Current Tables

The main paper-scale audit can be regenerated from saved result CSVs:

```bash
python experiments/07_jmlr_scale/analyze_jmlr_scale.py
```

The public notebook source lives in:

```bash
kaggle/mbe_metric_audit/how_to_audit_ml_training_metrics_mbe.ipynb
```

Kaggle training scripts and raw result manifests are under
`experiments/07_jmlr_scale/`. See [REPRODUCIBILITY.md](REPRODUCIBILITY.md) and
[experiments/07_jmlr_scale/ARTIFACTS.md](experiments/07_jmlr_scale/ARTIFACTS.md)
for commands and artifact hashes.

## Repository Layout

```text
metric-audit-paper/
+-- mbe_eval/                  # installable MBE package
+-- examples/                  # small local examples
+-- experiments/               # paper-scale and exploratory experiments
+-- figures/                   # generated no-compute evidence figures
+-- kaggle/mbe_metric_audit/   # public Kaggle notebook source
+-- docs/                      # documentation index
+-- SUPPORTING_EVIDENCE.md     # run-by-run evidence ledger
+-- REPRODUCIBILITY.md         # reproduction commands and expected artifacts
+-- PAPER.md                   # evolving paper direction
+-- JMLR_STRATEGY.md           # publication strategy notes
```

## Research Claim

The claim is not that any one metric is universally bad. The claim is narrower
and more useful:

> Raw pooled correlation is insufficient for validating ML training metrics.
> MBE audits whether a metric retains signal beyond ordinary training baselines
> and experimental design variables.

## Citation

```bibtex
@article{shadangi2026mbe,
  title={Marginal Baseline Evaluation for Auditing Generalization Metrics},
  author={Shadangi, Aparajeet},
  year={2026},
  note={Preprint and open-source research artifact}
}
```

## License

MIT License. See [LICENSE](LICENSE).
