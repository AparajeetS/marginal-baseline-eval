# Documentation

This index separates active research specifications from evidence, execution
guides, product notes, and historical material.

## Start Here

- [Research overview](PROJECT_OVERVIEW.md)
- [Authoritative roadmap](../ROADMAP.md)
- [Open research inventory](../OPEN_RESEARCH.md)
- [Reproducibility guide](../REPRODUCIBILITY.md)
- [Credibility ledger](MBE_CREDIBILITY_LEDGER.md)

## Active Method

- [MBE 2.0 research program](MBE_2_RESEARCH_PROGRAM.md): objective, estimands,
  baseline ladder, environments, work packages, and decision gates.
- [Statistical estimand and inference](STATISTICAL_ESTIMAND_AND_INFERENCE.md):
  primary estimand, uncertainty, assumptions, and practical significance.
- [Conditional metric reliability protocol](CONDITIONAL_METRIC_RELIABILITY_PROTOCOL.md):
  atlas, selector, evidence levels, and abstention.
- [Prospective selection protocol](PROSPECTIVE_SELECTION_PROTOCOL.md):
  frozen comparison against global and oracle selectors.
- [Metric taxonomy and ablations](METRIC_TAXONOMY_AND_ABLATIONS.md):
  metric families and required ablation table.

## Evidence And Credibility

- [Supporting evidence](../SUPPORTING_EVIDENCE.md): exploratory results and
  validity boundaries.
- [Credibility ledger](MBE_CREDIBILITY_LEDGER.md): supported, blocked,
  provisional, withdrawn, and falsified claims.
- [No-GPU closure status](NO_GPU_CLOSURE_STATUS.md): work completed without new
  training and work requiring external state.
- [Protocol calibration](../experiments/08_protocol_calibration/)
- [Published-study reaudit](../experiments/09_published_metric_reaudit/)
- [Method comparison](../experiments/10_method_comparison/)
- [Credibility freeze](../experiments/11_credibility_freeze/)

## Execution

- [Roadmap](../ROADMAP.md): milestone gates and stop-loss rules.
- [Execution resources](EXECUTION_RESOURCES.md): workload estimates and
  compute-release gates, without monetary assumptions.
- [Independent replication protocol](INDEPENDENT_REPLICATION_PROTOCOL.md):
  independence, execution, acceptance, and discrepancy rules.
- [Reproducibility guide](../REPRODUCIBILITY.md): CPU, artifact-only, and GPU
  paths.

## Guides And Interfaces

- [How to audit an ML training metric](audit_ml_training_metric.md)
- [Agent recipes](agent_recipes.md)
- [Agent contract](../AGENTS.md)
- [Machine-readable discovery file](../llms.txt)
- [Metric reliability audit service](METRIC_RELIABILITY_AUDIT_SERVICE.md)

## Paper

- [Paper workspace](../paper/README.md)
- [Current manuscript skeleton](../paper/JMLR_MANUSCRIPT_SKELETON.md)
- [Archived paper notes](../paper/archive/)

## Historical Material

The files in [archive/](archive/) preserve the v1 protocol, early taxonomy,
superseded experiment plan, and original progress log. They explain how the
research changed but do not define current work.

Release records are kept in [releases/](releases/).
