# External Holdout Protocol

Status: intake frozen; protected analysis remains sealed after the experiment
28 calibration gate failed. Dataset identity and hashes must remain frozen
before any metric-target association is inspected.

## Preferred Existing Holdout

PGDL Tasks 6-9 remain the preferred external transfer corpus. The verified
model counts are 96, 48, 64, and 32, respectively, for 240 independent models
in total. Archive listings contain two checkpoint files per model; checkpoint
member counts must never be reported as independent model counts.

No individual PGDL transfer task reaches the confirmed 192-unit threshold, so
every per-task application of that rule must abstain. A pooled 240-model
analysis is only eligible after a separate outcome-blind calibration reproduces
the four-task geometry, task-specific controls, and environment structure. It
must define a pooled cross-task estimand rather than presenting the result as a
Task 6 claim.

That calibration sequence has now run. Experiment 26 failed null control;
experiment 28 controlled the nulls but missed one frozen power criterion. The
opening decision is therefore negative and binding. The machine-readable
record is `PGDL_TASKS_6_9_INTAKE.json`, validated by `validate_intake.py`.
`INTAKE_SHA256SUMS` seals the intake record, validator, and protocol together.

This is an unopened checkpoint-metric holdout, not a wholly unseen dataset.
Target distributions and the metadata-only training-loss floor were previously
characterized across all PGDL tasks and must be disclosed. Checkpoint-derived
metric associations for Tasks 6-9 remain unopened.

## Eligibility

Any replacement holdout must be independently generated or publicly released outside MBE
method development and provide:

- at least 48 genuinely distinct training configurations, preferably 96;
- repeated seeds where available, or an explicit one-model-per-independent-run
  analysis such as PGDL;
- a declared generalization or robustness target unavailable to the selector
  during training;
- enough run-level metadata to construct design, training-state, and validation
  baseline ladders;
- raw or reproducible implementations for at least eight metric families;
- an explicit license permitting derived public audit artifacts.

The holdout is rejected before analysis if configurations are duplicates,
targets leak into metric computation, exclusions cannot be reconstructed, or
the independent unit is ambiguous.

## Freeze Packet

Before opening outcomes, publish the source citation, license, download and
file hashes, inclusion/exclusion rules, metric cards, target orientation,
baseline columns, independent-unit definition, missingness rules, frozen
estimator, multiplicity correction, negative control, and exact command.

## Analysis

Run all eligible metrics through every baseline level. Report effect estimates,
intervals, adjusted p-values, sign stability, abstentions, and missingness.
Keep confirmatory holdout results separate from earlier image/text development
and report the complete metric ledger regardless of direction.

## Failure Rule

An estimator-calibration failure, structural data failure, or absence of an
eligible external dataset is a reported outcome. It does not authorize another
dataset choice after outcome inspection.
