# Post-Confirmation Scope Erratum

Recorded immediately after confirmation and before any protected
checkpoint-derived metric association was inspected.

The frozen preregistration says PGDL Task 6 could be considered after a global
192-group pass. That sentence relied on the archive inventory's count of 192
checkpoint members. PGDL Task 6 actually contains 96 independent models, each
with initialization and final checkpoint files. The unified ledger verifies
the transfer-task model counts as:

| Task | Independent models | Checkpoint members |
|---|---:|---:|
| 6 | 96 | 192 |
| 7 | 48 | 96 |
| 8 | 64 | 128 |
| 9 | 32 | 64 |
| Total | 240 | 480 |

The frozen preregistration and its hash are preserved unchanged. The
confirmation result remains valid for two synthetic 192-group geometries, but
Task 6 alone is ineligible and must abstain. A pooled Tasks 6-9 application
requires a new outcome-blind 240-model calibration with task/environment
structure and task-specific controls before checkpoint metrics are opened.
