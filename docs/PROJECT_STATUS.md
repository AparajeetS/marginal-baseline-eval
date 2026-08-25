# MBE Project Status

Updated: 2026-08-26

## The Problem

Machine-learning research often treats a metric as useful when it correlates
with a held-out score. That can be misleading when both quantities track
ordinary facts such as model size, optimizer choice, training loss, task
difficulty, or response length. The practical question is not only whether a
metric correlates with an outcome, but whether it adds reliable information
beyond the baselines already available for the decision being made.

Marginal Baseline Evaluation (MBE) is an open audit protocol for that question.
It combines a declared baseline-information ladder, grouped out-of-sample
estimation, design-matched negative controls, uncertainty, transport checks,
and explicit abstention. The long-term objective is a task-specific reliability
layer that can say which metrics have earned trust for a particular target and
environment, while refusing to rank them when the evidence is inadequate.

## What Exists Today

- An MIT-licensed Python package, command-line audit tools, public Kaggle
  notebook, documentation, and agent-oriented entry points.
- A 680-row exploratory image/text ledger covering more than 40 metric
  candidates. It is useful as motivation and regression evidence, not as a
  confirmatory sample.
- Corrected prospective artifacts: 96 CIFAR-10 image runs, 144 causal-LM runs
  across three corpora, and a separate 180-run causal-text replication.
- A completed 360-model, multi-target image transport atlas across CIFAR-10,
  CIFAR-100, and a protected SVHN environment, with all structural gates
  passing and no target-metric associations inspected.
- A completed 48,000-cell outcome-blind calibration screen, a 153,600-row
  strong-comparator benchmark, and multiple disjoint development and
  confirmation studies.
- A completed 126,000-row oracle feasibility frontier separating information,
  measurement, and nuisance-estimation limits at 24-192 configurations.
- A 240-model PGDL external-holdout intake and an executable, hash-sealed
  independent-replication packet.
- Public preregistrations, canonical result ledgers, integrity manifests,
  SHA-256 records, validators, failure provenance, and explicit non-claims.

## What The Evidence Says

The project has not found a universal winner. Instead, it has found a
calibration-power frontier. Procedures that look powerful at 24-48 independent
configurations can produce excessive support in difficult known-null cells;
the most conservative procedures can become too weak to support real metric
claims. A 192-group orthogonal-score rule passed its scoped synthetic
confirmation, but did not transfer cleanly to the pooled PGDL geometry. A
revised PGDL rule controlled every null cell and then missed one prespecified
power bound by 0.008. The protected outcomes remained sealed.

The oracle frontier sharpened that result. In its frozen noisy-observable
regime, 24 independent configurations were underpowered even when the nuisance
functions were known exactly. At 48 configurations, the observable oracle
passed calibration and power, but learned nuisance estimators still produced
excess false support. The completed 360-model image atlas has 24 independent
configurations per environment, so it is a high-quality prospective artifact,
not a license to treat its 120 repeated-seed rows per dataset as independent
evidence. Its protected SVHN associations remain sealed.

That restraint is part of the result. The repository preserves failed gates,
an invalid seed-range attempt, an independent-unit counting correction, and
development candidates that did not advance. These results support continued
work on calibrated, sample-size-aware metric auditing. They do not establish
that MBE is universally valid, that established metrics are broadly defective,
or that a production metric selector is ready.

## Why Further Work Matters

Metrics increasingly mediate model selection, robustness claims, safety
monitoring, automated evaluation, and mechanistic-interpretability research.
If a metric's apparent value is explainable by cheap baseline information, a
decision system can become more confident without becoming better informed.
A credible pre-decision audit layer would make the evidential scope of those
measurements explicit and would surface abstention before they guide higher
stakes choices.

The first proposed safety-facing case is an audit of automated jailbreak and
harmfulness judges against independently defined human assessments. It will
compare raw-correlation selection, a globally fixed judge, and an MBE-supported
choice or abstention on a held-out model or attack family. StrongREJECT is the
leading development candidate and HarmBench is a transfer candidate, but both
must pass provenance, licensing, target-independence, and independent-unit
checks before use. The [AI-safety measurement case](AI_SAFETY_MEASUREMENT_CASE.md)
states the design and non-claims.

The next decisive work is scientific rather than cosmetic: develop and freeze
a rule with controlled false support and useful power at realistic sample
sizes, confirm it on disjoint known-truth data, evaluate one genuinely external
holdout, obtain an externally executed signed replication, and test prospective
metric selection on future task families. Positive, null, and failed outcomes
are all publication-worthy when the gate is fixed in advance.

## Review Trail

- [Evidence index](EVIDENCE_INDEX.md)
- [AI-safety measurement case](AI_SAFETY_MEASUREMENT_CASE.md)
- [Experiment synthesis](EXPERIMENT_EVIDENCE_SYNTHESIS.md)
- [Credibility ledger](MBE_CREDIBILITY_LEDGER.md)
- [Statistical specification](STATISTICAL_ESTIMAND_AND_INFERENCE.md)
- [JMLR critical path](JMLR_CRITICAL_PATH_2026-08-26.md)
- [Reproduction guide](../REPRODUCIBILITY.md)
- [Open research inventory](../OPEN_RESEARCH.md)
