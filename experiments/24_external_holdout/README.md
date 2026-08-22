# External Holdout Intake

This directory records the frozen intake for PGDL Tasks 6-9: 240 independent
models across four tasks. It defines the independent unit, protected columns,
eligibility rules, and hashes before any checkpoint-metric association is
opened.

The opening decision is currently **abstain**. Experiment 26 failed null
control, and the corrected experiment 28 rule missed one prespecified power
bound. The protected checkpoint-metric and generalization-target associations
therefore remain sealed.

Validate the machine-readable intake with:

```bash
python experiments/24_external_holdout/validate_intake.py
```

Read [PROTOCOL_DRAFT.md](PROTOCOL_DRAFT.md) for the holdout requirements and
[PGDL_TASKS_6_9_INTAKE.json](PGDL_TASKS_6_9_INTAKE.json) for the frozen record.
The word "external" refers to the source corpus; this is not yet an externally
executed replication.
