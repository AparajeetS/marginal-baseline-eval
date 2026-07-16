# Open Research Inventory

Marginal Baseline Evaluation is maintained as shared research infrastructure.
The repository, package, protocols, evidence records, and reproduction paths are
public so that researchers can inspect the method, audit its claims, reproduce
the available analyses, and propose competing designs.

## What Is Public

| Surface | Public location | Current status |
|---|---|---|
| Source code | [`mbe_eval/`](mbe_eval/) | MIT licensed; installable audit implementation |
| Python package | [PyPI: `mbe-eval`](https://pypi.org/project/mbe-eval/) | Stable v1 API; version shown on PyPI |
| Command-line tools | `mbe-eval-audit`, `mbe-eval-demo` | Included with the package |
| Public notebook | [Kaggle walkthrough](https://www.kaggle.com/code/aparajeetshadangi/audit-ml-training-metrics-with-mbe) | Introductory v1 demonstration |
| Current protocol | [`docs/MBE_2_RESEARCH_PROGRAM.md`](docs/MBE_2_RESEARCH_PROGRAM.md) | Active MBE 2.0 research design |
| Legacy protocol | [`PROTOCOL_FREEZE.md`](PROTOCOL_FREEZE.md) | Preserved for provenance; superseded |
| Evidence ledger | [`SUPPORTING_EVIDENCE.md`](SUPPORTING_EVIDENCE.md) | Exploratory results with validity warnings |
| Reproduction guide | [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md) | CPU and GPU paths separated |
| Milestone roadmap | [`docs/JMLR_MILESTONE_ROADMAP.md`](docs/JMLR_MILESTONE_ROADMAP.md) | Gated plan to submission-grade evidence |
| Compute budget | [`docs/COMPUTE_AND_COST_PLAN.md`](docs/COMPUTE_AND_COST_PLAN.md) | Minimum and recommended estimates |
| Grant execution plan | [`GRANT_EXECUTION_PLAN.md`](GRANT_EXECUTION_PLAN.md) | Exact run matrix, holdout, budget ceilings, and deliverables |
| Independent replication | [`docs/INDEPENDENT_REPLICATION_PROTOCOL.md`](docs/INDEPENDENT_REPLICATION_PROTOCOL.md) | Conflict, execution, acceptance, and reporting rules |
| Synthetic calibration | [`experiments/08_protocol_calibration/`](experiments/08_protocol_calibration/) | Known-ground-truth MBE 2.0 protocol checks |
| Published metric reaudit | [`experiments/09_published_metric_reaudit/`](experiments/09_published_metric_reaudit/) | Strict manifest schema and retrospective audit runner |
| Conditional reliability protocol | [`docs/CONDITIONAL_METRIC_RELIABILITY_PROTOCOL.md`](docs/CONDITIONAL_METRIC_RELIABILITY_PROTOCOL.md) | Frozen atlas, selector, and abstention evaluation |
| Audit service boundary | [`docs/METRIC_RELIABILITY_AUDIT_SERVICE.md`](docs/METRIC_RELIABILITY_AUDIT_SERVICE.md) | Open-core and private-audit product model |
| Credibility ledger | [`docs/MBE_CREDIBILITY_LEDGER.md`](docs/MBE_CREDIBILITY_LEDGER.md) | Adversarial validation gates, failures, and blocked claims |
| Citation metadata | [`CITATION.cff`](CITATION.cff) | Machine-readable citation |

## What Works Without New Compute

Researchers can install the package, run the synthetic demo, audit their own
CSV training ledger, inspect the statistical implementation, regenerate tables
from the committed artifacts, and submit issues or pull requests. The package
does not require access to the authors' infrastructure.

```bash
pip install mbe-eval
mbe-eval-demo --bootstrap 200
```

## Research Maturity

The public software and the scientific claim have different maturity levels:

- **MBE v1 software:** available and usable for linear partial-rank audits.
- **MBE v1 evidence:** exploratory and retained for provenance; it contains
  repeated configurations, and the legacy text setup is invalid as causal
  language-model evidence.
- **MBE 2.0:** the active research program. Its nonlinear, cross-fitted,
  multi-environment protocol is specified but is not yet fully implemented in
  the released package or supported by submission-grade evidence.

This distinction is intentional. Openness includes publishing negative results,
known limitations, and unfinished validation work rather than presenting a
research plan as completed evidence.

## Independence And Continuity

The project uses the MIT License, standard Python packaging, plain CSV and
Markdown artifacts, and publicly documented commands. A third party may fork,
maintain, reproduce, criticize, or extend it without requesting permission.
Maintenance and decision practices are documented in [`GOVERNANCE.md`](GOVERNANCE.md).

## Reporting Problems

- Scientific or reproducibility issue: open a GitHub issue with the artifact,
  command, expected result, and observed result.
- Package improvement: use the package-improvement issue template.
- Security concern: follow [`SECURITY.md`](SECURITY.md).
- Contribution: follow [`CONTRIBUTING.md`](CONTRIBUTING.md).
