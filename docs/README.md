# Documentation

This index separates active research specifications from evidence, execution
guides, product notes, and historical material.

## Start Here

- [Research overview](PROJECT_OVERVIEW.md)
- [One-page project status](PROJECT_STATUS.md)
- [AI-safety measurement case](AI_SAFETY_MEASUREMENT_CASE.md)
- [Safety-study feasibility memo](SAFETY_STUDY_FEASIBILITY_MEMO.md)
- [Evidence index](EVIDENCE_INDEX.md)
- [Experiment synthesis](EXPERIMENT_EVIDENCE_SYNTHESIS.md)
- [Authoritative roadmap](../ROADMAP.md)
- [Open research inventory](../OPEN_RESEARCH.md)
- [Reproducibility guide](../REPRODUCIBILITY.md)
- [Credibility ledger](MBE_CREDIBILITY_LEDGER.md)

## Active Method

- [AI-safety measurement case](AI_SAFETY_MEASUREMENT_CASE.md): proposed
  jailbreak and harmfulness-judge audit, opening gate, decision comparison,
  and non-claims.
- [Safety-study feasibility memo](SAFETY_STUDY_FEASIBILITY_MEMO.md):
  outcome-blind StrongREJECT and HarmBench intake, frozen study shape, opening
  gates, and stop rules.
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
- [Evidence index](EVIDENCE_INDEX.md): corrected artifacts, calibration gates,
  retained failures, and current non-claims.
- [Experiment synthesis](EXPERIMENT_EVIDENCE_SYNTHESIS.md): findings and
  reproduction entry point for every experiment program.
- [Artifact integrity and lineage](ARTIFACT_INTEGRITY.md): current checksums,
  historical receipts, recovery records, and source snapshots.
- [No-GPU closure status](NO_GPU_CLOSURE_STATUS.md): work completed without new
  training and work requiring external state.
- [Protocol calibration](../experiments/08_protocol_calibration/)
- [Published-study reaudit](../experiments/09_published_metric_reaudit/)
- [Method comparison](../experiments/10_method_comparison/)
- [Conditional comparator benchmark](../experiments/23_conditional_comparator_benchmark/)
- [Oracle feasibility frontier](../experiments/30_oracle_feasibility_frontier/)
- [Image target-transport atlas](../experiments/31_image_target_transport_atlas/)
- [External holdout intake](../experiments/24_external_holdout/)
- [Independent replication packet](../experiments/12_independent_replication/)
- [Credibility freeze](../experiments/11_credibility_freeze/)

## Execution

- [Roadmap](../ROADMAP.md): milestone gates and stop-loss rules.
- [JMLR critical path](JMLR_CRITICAL_PATH_2026-08-26.md): current scientific blockers and opening gates.
- [Execution resources](EXECUTION_RESOURCES.md): workload estimates and
  compute-release gates, without monetary assumptions.
- [Historical CPU campaign runbook](CPU_CAMPAIGN_NEXT_48_HOURS.md): frozen queue
  and completion gates used for the July 2026 campaign.
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
