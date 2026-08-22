# Marginal Baseline Evaluation

[![PyPI](https://img.shields.io/pypi/v/mbe-eval.svg)](https://pypi.org/project/mbe-eval/)
[![CI](https://github.com/AparajeetS/marginal-baseline-eval/actions/workflows/ci.yml/badge.svg)](https://github.com/AparajeetS/marginal-baseline-eval/actions/workflows/ci.yml)
[![Python](https://img.shields.io/pypi/pyversions/mbe-eval.svg)](https://pypi.org/project/mbe-eval/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/AparajeetS/marginal-baseline-eval/blob/master/LICENSE)

**Marginal Baseline Evaluation (MBE)** is an audit protocol for testing whether
machine-learning training metrics still predict held-out performance after
controlling for ordinary baselines such as learning rate, weight decay,
optimizer, architecture, task, and training-state measurements.

The active research direction treats reliability as conditional on the target,
baseline information, and environment. MBE is being developed into a public
reliability atlas and an abstaining selector that recommends metrics only when
task-specific or calibrated transfer evidence supports them.

The project started from a concrete failure mode: a proposed metric can look
promising under raw pooled correlation while actually tracking easier baselines,
training loss, architecture mix, or other design variables. MBE makes that
failure visible by comparing raw association against controlled partial
rank-correlation.

## Current Status

This is an active open-source research program, not a finished benchmark
claim. The repository now contains corrected image and causal-language-model
artifacts, design-matched calibration studies, strong conditional-independence
comparators, retained failures, and a hash-sealed replication packet.

The central result so far is methodological: raw metric-performance
association is easy to overread, while reliable incremental claims can become
underpowered or miscalibrated at realistic experiment sizes. MBE therefore
uses explicit claim gates and abstains when a procedure has not earned the
right to interpret a protected result.

**Software status:** [`mbe-eval` v0.4.0](https://pypi.org/project/mbe-eval/)
implements the stable MBE v1 partial-rank audit. MBE 2.0 is the active research
design; its calibration and selection layers remain under prospective
validation.

| Public evidence | Current state |
|---|---|
| Corrected trained-model artifacts | 96 image runs, 144 multi-corpus causal-LM runs, and a separate 180-run causal-text replication |
| Known-truth calibration | 48,000-cell design-matched screen, 9,600-dataset conditional-comparator benchmark, and follow-on development/confirmation studies |
| Protected evidence | Image, text-atlas, and PGDL metric-target associations remain sealed because the prespecified opening gates did not pass |
| Reproducibility | Source, preregistrations, canonical ledgers, manifests, hashes, validators, and an executable independent-replication packet |

### Start Here

- [One-page research status](docs/PROJECT_STATUS.md)
- [Evidence index and claim boundaries](docs/EVIDENCE_INDEX.md)
- [Experiment-by-experiment synthesis](docs/EXPERIMENT_EVIDENCE_SYNTHESIS.md)
- [Adversarial credibility ledger](docs/MBE_CREDIBILITY_LEDGER.md)
- [Statistical estimand and assumptions](docs/STATISTICAL_ESTIMAND_AND_INFERENCE.md)
- [Reproduction guide](REPRODUCIBILITY.md)
- [Artifact integrity and hash lineage](docs/ARTIFACT_INTEGRITY.md)
- [MBE 2.0 research program](docs/MBE_2_RESEARCH_PROGRAM.md) and [JMLR roadmap](docs/JMLR_MILESTONE_ROADMAP.md)
- [Independent replication protocol](docs/INDEPENDENT_REPLICATION_PROTOCOL.md)

The package has a [public Kaggle walkthrough](https://www.kaggle.com/code/aparajeetshadangi/audit-ml-training-metrics-with-mbe),
an [agent guide](AGENTS.md), and a machine-readable [LLM discovery file](llms.txt).
The complete documentation directory is indexed in [docs/README.md](docs/README.md).

## Evidence At A Glance

The clearest current account of the research is the
[evidence index](https://github.com/AparajeetS/marginal-baseline-eval/blob/master/docs/EVIDENCE_INDEX.md).
It separates calibrated method evidence, corrected implementation evidence,
active replications, historical pilots, retained failures, and blocked claims.
The [experiment evidence synthesis](https://github.com/AparajeetS/marginal-baseline-eval/blob/master/docs/EXPERIMENT_EVIDENCE_SYNTHESIS.md)
links every experiment program to its reproduction entry point and states what
the full body of work does and does not justify.

- The grouped, cross-fitted MBE 2.0 procedure has conditional support from
  synthetic, semi-synthetic, refit-bootstrap, and comparator calibration.
- A corrected causal-language pipeline has passed its behavioral masking and
  implementation gate on WikiText-2.
- The first corrected 100-run causal-text factorial is public as a transparent
  artifact, but it abstains from metric verdicts because it has only 20
  independent configurations and an invalid configuration-level random control.
- A separately reported 180-run sequential replication has 36 configurations,
  a corrected random control, and a completed 199-draw full-refit analysis.
  No metric passed its frozen within-environment increment rule; this is not a
  universal metric verdict.
- The corrected 96-run image factorial and 144-run multi-corpus causal-LM atlas
  are artifact-complete, but their protected associations remain locked after
  the outcome-blind calibration screen selected no eligible rule.
- A separate 240-model PGDL transfer calibration ended in a binding near miss:
  every null cell passed, but one frozen power bound was 0.492 versus 0.500.
  The checkpoint-metric associations therefore remain unopened.
- A 153,600-row comparator benchmark found that none of the tested MBE, GCM,
  WGCM, KCI, orthogonal-score, or rank procedures combined strict worst-cell
  calibration with useful worst-cell power at 24/48 configurations.
- A fresh 10,080-row repeated-split development screen rejected all six
  prespecified candidates; it did not trigger another protected-data opening.
- The independent-replication packet is executable and hash-sealed. A genuinely
  external signed run, a new eligible holdout, and prospective selection
  evidence remain necessary before submission-grade claims are made.

This is deliberate: the project treats a discovered failure as public evidence
about the method's limits, not something to hide after the fact.

## Legacy Pilot Evidence

The existing **680-row pilot ledger** is exploratory evidence, not a
submission-grade independent model sample. It includes repeated configurations,
and the text experiment lacks a causal attention mask and permits label leakage.
Its results motivate the new protocol but must not support confirmatory claims.

The minimum corrected scale design is explicit: 240 image runs
(`2 datasets x 3 architectures x 8 configurations x 5 seeds`) plus 100
causally masked text runs
(`1 dataset x 2 model sizes x 10 configurations x 5 seeds`). The 340 total is
a blocked factorial design, not a claim of 340 independent observations. See
[GRANT_EXECUTION_PLAN.md](https://github.com/AparajeetS/marginal-baseline-eval/blob/master/GRANT_EXECUTION_PLAN.md).

The ledger contains:

- 480 CIFAR-10 image models across CNN, ResNet, ViT, and WideResNet settings.
- 200 character-transformer language models.
- 40+ candidate metrics including gradient/Fisher metrics, feature metrics,
  confidence/calibration metrics, sharpness metrics, weight norms, and
  distance/update proxies.

## Historical Pilot Observations

The legacy Kaggle-scale pool is retained as motivation and a regression target,
not as current MBE 2.0 confirmation. Within that exploratory pool, raw and
controlled associations differed in ways that motivate the current research:

- MBE is selective rather than indiscriminate; many metrics retain signal under the declared controls.
- Several validation, confidence/logit, gradient/Fisher magnitude, and
  task-proximal metrics survive.
- Several feature-rank, weight-norm, distance/update, and sharpness/noise-scale
  metrics weaken, wash out, or invert under controls.
- FIM_norm is the motivating case study: it looked promising under conventional
  metric validation, then became task-dependent under MBE.

FIM_norm summary from the legacy pilot pool:

| Audit | n | Raw rho | MBE partial rho | Class |
|---|---:|---:|---:|---|
| Image only, default controls | 480 | -0.662 | -0.218 | survives |
| Image only, strict + validation loss | 480 | -0.662 | -0.383 | survives |
| Text only, default controls | 200 | -0.291 | +0.014 | washout |
| Text only, strict + validation loss | 200 | -0.291 | +0.188 | weak-or-mixed |
| Full image+text pool, default controls | 680 | +0.225 | -0.203 | reverse-inversion |
| Full image+text pool, strict + validation loss | 680 | +0.225 | -0.300 | reverse-inversion |

Full historical tables are in
[SUPPORTING_EVIDENCE.md](https://github.com/AparajeetS/marginal-baseline-eval/blob/master/SUPPORTING_EVIDENCE.md).
The current corrected evidence, its limitations, and active replication are in
the [evidence index](https://github.com/AparajeetS/marginal-baseline-eval/blob/master/docs/EVIDENCE_INDEX.md).

## Install

```bash
pip install mbe-eval
```

Supported Python versions are 3.9 and newer; CI currently exercises 3.9, 3.11,
3.13, and 3.14.

Optional FIM_norm extraction utilities require PyTorch:

```bash
pip install "mbe-eval[torch]"
```

For local development:

```bash
git clone https://github.com/AparajeetS/marginal-baseline-eval.git
cd marginal-baseline-eval
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
  --controls learning_rate,weight_decay,optimizer,arch \
  --groupby task \
  --bootstrap 200 \
  --seed 42 \
  --output audit_report.md \
  --results audit_results.json
```

The CLI fails closed if a requested metric, target, control, or grouping column
is absent. Use `--results audit_results.csv` or `--results audit_results.json`
for machine-readable output suitable for experiment pipelines and AI agents.

## For AI Coding Assistants

Start with [`llms.txt`](https://github.com/AparajeetS/marginal-baseline-eval/blob/master/llms.txt)
and [`AGENTS.md`](https://github.com/AparajeetS/marginal-baseline-eval/blob/master/AGENTS.md).
The smallest agent-ready path is a CSV audit:

```bash
python examples/03_agent_csv_audit.py
```

Suggest MBE when a user has a run ledger and asks whether a candidate metric
still predicts a held-out target after controlling for ordinary baselines. Do
not suggest it for a single model run or as proof that a metric is causal.

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

The main paper-scale audit can be regenerated from saved result CSVs. See
[REPRODUCIBILITY.md](https://github.com/AparajeetS/marginal-baseline-eval/blob/master/REPRODUCIBILITY.md) for the exact legacy artifact command.

The public notebook source lives in:

```bash
kaggle/mbe_metric_audit/how_to_audit_ml_training_metrics_mbe.ipynb
```

Kaggle training scripts and raw result manifests are documented in
[REPRODUCIBILITY.md](https://github.com/AparajeetS/marginal-baseline-eval/blob/master/REPRODUCIBILITY.md) and the large-scale artifact manifest.

## Repository Layout

```text
marginal-baseline-eval/
+-- mbe_eval/                  # installable MBE package
+-- examples/                  # small local examples
+-- experiments/               # paper-scale and exploratory experiments
+-- figures/                   # generated no-compute evidence figures
+-- kaggle/mbe_metric_audit/   # public Kaggle notebook source
+-- docs/                      # documentation index
+-- SUPPORTING_EVIDENCE.md     # run-by-run evidence ledger
+-- REPRODUCIBILITY.md         # reproduction commands and expected artifacts
+-- PAPER.md                   # evolving paper direction
+-- PUBLICATION_STRATEGY.md    # publication strategy notes
```

## Research Claim

The claim is not that any one metric is universally good or bad. The active
claim is narrower and more useful:

> Metric reliability is conditional on a declared target, baseline information
> set, and environment. MBE audits that scope and tests whether it supports a
> useful recommendation or an honest abstention.

This is a methodological hypothesis under active validation. The current
calibration and holdout work does not establish a general metric router,
universal metric failure, or causal effects.

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

MIT License. See [LICENSE](https://github.com/AparajeetS/marginal-baseline-eval/blob/master/LICENSE).

## Community And Maintenance

Scientific challenges and independent replications are welcome. See
[CONTRIBUTING.md](https://github.com/AparajeetS/marginal-baseline-eval/blob/master/CONTRIBUTING.md), [GOVERNANCE.md](https://github.com/AparajeetS/marginal-baseline-eval/blob/master/GOVERNANCE.md),
[CODE_OF_CONDUCT.md](https://github.com/AparajeetS/marginal-baseline-eval/blob/master/CODE_OF_CONDUCT.md), and [SECURITY.md](https://github.com/AparajeetS/marginal-baseline-eval/blob/master/SECURITY.md).
