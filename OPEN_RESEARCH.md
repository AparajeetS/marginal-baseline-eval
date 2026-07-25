# Open Research Inventory

Marginal Baseline Evaluation is maintained as shared research infrastructure.
The code, protocols, evidence records, and reproduction paths are public so
that researchers can inspect the method, audit its claims, reproduce the
available analyses, and propose competing designs.

## Public Surfaces

| Surface | Location | Status |
|---|---|---|
| Source code | [`mbe_eval/`](mbe_eval/) | MIT licensed; installable |
| Python package | [PyPI: `mbe-eval`](https://pypi.org/project/mbe-eval/) | Stable v1 API |
| Command-line tools | `mbe-eval-audit`, `mbe-eval-demo` | Included in package |
| Public notebook | [Kaggle walkthrough](https://www.kaggle.com/code/aparajeetshadangi/audit-ml-training-metrics-with-mbe) | Introductory v1 demonstration |
| Active research program | [`docs/MBE_2_RESEARCH_PROGRAM.md`](docs/MBE_2_RESEARCH_PROGRAM.md) | MBE 2.0 specification |
| Statistical specification | [`docs/STATISTICAL_ESTIMAND_AND_INFERENCE.md`](docs/STATISTICAL_ESTIMAND_AND_INFERENCE.md) | Estimand, inference, assumptions |
| Evidence ledger | [`SUPPORTING_EVIDENCE.md`](SUPPORTING_EVIDENCE.md) | Exploratory results with warnings |
| Credibility ledger | [`docs/MBE_CREDIBILITY_LEDGER.md`](docs/MBE_CREDIBILITY_LEDGER.md) | Claim-by-claim gate status |
| Reproduction guide | [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md) | CPU, artifact, and GPU paths |
| Roadmap | [`ROADMAP.md`](ROADMAP.md) | Gated path to submission-grade evidence |
| Execution resources | [`docs/EXECUTION_RESOURCES.md`](docs/EXECUTION_RESOURCES.md) | Workload estimates and release gates |
| Independent replication | [`docs/INDEPENDENT_REPLICATION_PROTOCOL.md`](docs/INDEPENDENT_REPLICATION_PROTOCOL.md) | Independence and acceptance rules |
| Synthetic calibration | [`experiments/08_protocol_calibration/`](experiments/08_protocol_calibration/) | Known-truth protocol checks |
| Published-study reaudit | [`experiments/09_published_metric_reaudit/`](experiments/09_published_metric_reaudit/) | Manifest-based retrospective audit |
| Method comparison | [`experiments/10_method_comparison/`](experiments/10_method_comparison/) | Shared known-truth benchmark |
| Credibility freeze | [`experiments/11_credibility_freeze/`](experiments/11_credibility_freeze/) | Preregistration, hashes, and claim checks |
| Citation metadata | [`CITATION.cff`](CITATION.cff) | Machine-readable citation |

## What Works Without New Compute

Researchers can:

- install the package and run the synthetic demo;
- audit their own multi-run CSV ledger;
- inspect the statistical implementation;
- regenerate tables from committed artifacts;
- rerun known-truth calibration and method comparisons;
- validate the frozen claim ledger;
- submit issues, replications, or competing implementations.

```bash
pip install mbe-eval
mbe-eval-demo --bootstrap 200
```

## Maturity

- **MBE v1 software:** usable for linear partial-rank audits.
- **MBE v1 evidence:** exploratory and retained for provenance.
- **MBE 2.0 implementation:** public and under calibration.
- **Conditional reliability atlas:** protocol frozen; broad evidence incomplete.
- **Prospective selector:** provisional until it beats fixed comparators on
  protected environments.
- **Independent replication:** protocol public; execution incomplete.

Openness includes negative results, implementation failures, and blocked claims.
A research plan is not presented as completed evidence.

## Continuity

The project uses an MIT license, standard Python packaging, plain CSV and
Markdown artifacts, deterministic manifests, and public commands. A third party
may fork, maintain, reproduce, criticize, or extend it without permission.
Maintenance and decision practices are described in [GOVERNANCE.md](GOVERNANCE.md).

## Reporting Problems

- Scientific or reproducibility issue:
  [open a GitHub issue](https://github.com/AparajeetS/marginal-baseline-eval/issues).
- Security-sensitive issue: follow [SECURITY.md](SECURITY.md).
- Contribution or replication: follow [CONTRIBUTING.md](CONTRIBUTING.md).
*** End of File
