# Project Brief

## Project

**Marginal Baseline Evaluation (MBE)** is an open research project and Python
package for stress-testing claims about machine-learning training metrics.

## Problem

New metrics are often validated with pooled correlation against held-out
performance. That can overstate value when the metric tracks learning rate,
architecture, task composition, training state, or another ordinary predictor.
It can also hide failures to transfer across environments.

MBE 2.0 asks five distinct questions:

1. Does the metric associate with the target unconditionally?
2. Does it add predictive information beyond a declared baseline?
3. Does that information transport across tasks, architectures, and datasets?
4. Does it respond correctly under interventions with known direction?
5. Is it reliable and inexpensive enough to measure consistently?

The revised endpoint is not a universal metric ranking. MBE produces a
target- and environment-specific reliability profile, a public reliability
atlas, and, if held-out task-family tests support it, an abstaining selector
that recommends which metrics are defensible for a particular use case.

## Current State

The software is usable today. Researchers can install `mbe-eval`, run a
CPU-only demonstration, audit a CSV training ledger, inspect the implementation,
and generate a Markdown report. The current v0.3.1 release implements the MBE
v1 linear partial-rank audit.

The scientific program is earlier-stage. Existing Kaggle runs are exploratory
pilot evidence. The 680-row legacy ledger contains repeated configurations, and
the text setup lacks a causal mask and permits label leakage. Those results are
preserved as provenance and as a case study in why audit protocols themselves
need stress testing; they are not presented as confirmatory language-model
evidence.

The active MBE 2.0 program replaces a single partial-correlation verdict with
cross-fitted nonlinear baselines, separate targets, environment transport,
intervention tests, uncertainty, practical significance, and explicit positive
and negative controls.

The conditional selector is not yet a validated general router. PGDL provides
eight tasks for an atlas and feasibility study; broad automated-selection
claims require more independent task families and leave-one-family-out
validation.

It does not claim priority for conditioning or partial correlation by
themselves. The proposed contribution is a calibrated, auditable combination
of five estimands, a baseline information ladder, deceptive controls,
configuration-blocked uncertainty, environment transport, matched
interventions, measurement reliability, and scoped claim cards. That novelty
claim must pass comparison against prior conditional and robust evaluation
methods before the main compute block is released.

## Open Research Outputs

- Python package: https://pypi.org/project/mbe-eval/
- GitHub: https://github.com/AparajeetS/marginal-baseline-eval
- Public notebook: https://www.kaggle.com/code/aparajeetshadangi/audit-ml-training-metrics-with-mbe
- Open research inventory: [`OPEN_RESEARCH.md`](OPEN_RESEARCH.md)
- Technical program: [`docs/MBE_2_RESEARCH_PROGRAM.md`](docs/MBE_2_RESEARCH_PROGRAM.md)
- Conditional reliability protocol: [`docs/CONDITIONAL_METRIC_RELIABILITY_PROTOCOL.md`](docs/CONDITIONAL_METRIC_RELIABILITY_PROTOCOL.md)
- Audit service model: [`docs/METRIC_RELIABILITY_AUDIT_SERVICE.md`](docs/METRIC_RELIABILITY_AUDIT_SERVICE.md)
- Evidence ledger: [`SUPPORTING_EVIDENCE.md`](SUPPORTING_EVIDENCE.md)
- Reproduction guide: [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md)
- Governance: [`GOVERNANCE.md`](GOVERNANCE.md)
- Grant execution plan: [`GRANT_EXECUTION_PLAN.md`](GRANT_EXECUTION_PLAN.md)
- Independent replication protocol: [`docs/INDEPENDENT_REPLICATION_PROTOCOL.md`](docs/INDEPENDENT_REPLICATION_PROTOCOL.md)
- MIT license: [`LICENSE`](LICENSE)

## Why Support Is Needed

The highest-value next work is methodological calibration followed by corrected
replication, not simply a larger rerun. Funding or credits would support:

- synthetic tests with known nuisance structure and oracle controls;
- reanalysis of suitable public model corpora;
- corrected image and causally masked language-model factorial experiments;
- grouped uncertainty, baseline ablations, and locked external holdouts;
- release-quality artifacts, documentation, and independent reproduction.

The minimum corrected factorial contains 340 training runs: 240 image runs
from `2 datasets x 3 architectures x 8 configurations x 5 seeds`, plus 100
causally masked language-model runs from
`1 dataset x 2 model sizes x 10 configurations x 5 seeds`. These are 68
configuration blocks with repeated seeds, not 340 IID observations. A
corrected pilot must confirm runtime, leakage checks, and uncertainty adequacy
before scale compute is approved.

The minimum operational target is approximately 400 RTX 4090-equivalent
GPU-hours. The recommended envelope is approximately 650 equivalent hours when
the public-corpus and pilot gates support proceeding. The grant compute-and-
storage allocation is a gated ceiling covering primary execution, holdout,
approved reruns, independent execution, storage, transfer, and provider
variance; it is not a raw GPU-rental quote or spending target.

## Expected Impact

MBE is intended to become shared validation infrastructure for metric papers,
benchmark designers, and small labs. Its value is not declaring metrics
universally good or bad. It is making the evidentiary standard explicit and
reproducible: what a metric predicts, beyond which baseline, in which
environment, under which intervention, and with what uncertainty and cost.

The same open protocol can support private metric-reliability audits. Paid
value would come from secure execution, customer-specific calibration,
integration, monitoring, and support; the core method, public benchmark, and
scientific failures remain open.

If active maintenance stopped, the MIT-licensed implementation, package source,
protocols, artifact formats, and reproduction instructions would remain
available for independent continuation.
