# Independent Replication Protocol

Status: grant execution specification. The external replicator is not yet
selected. Their identity, conflicts, and scope will be published before the
protected holdout is opened.

## Purpose

The central MBE 2.0 result must not be validated only by the project creator.
The replication is an independent execution of frozen code and analysis, not a
second exploratory analysis that can tune the narrative.

## Independence Rule

The replicator must:

- have made no contribution to the primary MBE 2.0 implementation or metric
  selection;
- have no access to protected-holdout outcomes before the protocol, container,
  and primary analysis command are frozen;
- disclose financial, institutional, publication, and collaboration conflicts;
- be free to publish discrepancies or a failed replication.

Selection is completed before the scale gate. If no eligible replicator is
secured, the project may release the internal results but may not describe the
independent-replication milestone as complete.

## Replication Package

The replicator receives:

1. a signed repository tag and container digest;
2. the preregistered estimands, metric cards, baseline ladder, and thresholds;
3. dataset and split hashes without protected outcomes;
4. one command for training or artifact acquisition;
5. one command for validation and table generation;
6. expected schemas, checksums, runtime ranges, and failure rules.

The primary team does not provide expected headline values before the
replicator commits their report.

The executable audit entrypoint is
`experiments/12_independent_replication/run_replication_audit.py`. It records
the reviewer, conflict statement, commit, frozen-hash verification, test output,
dirty paths, discrepancies, and conclusion in machine-readable form.

## Required Checks

- clean-environment installation and CLI smoke test;
- schema, duplicate-key, leakage, and causal-mask checks;
- reproduction of synthetic calibration and deceptive controls;
- independent execution of at least one image environment and one causal-text
  environment;
- execution of the frozen protected-holdout analysis;
- comparison of raw ledgers, exclusions, confidence intervals, and primary
  conclusions;
- public discrepancy log, including unresolved differences.

## Acceptance Criteria

Replication is successful only when:

- all primary tables regenerate from raw artifacts;
- no material result depends on an undocumented exclusion or manual edit;
- independent and primary estimates agree within the preregistered tolerance,
  or differences are fully explained and corrected;
- the replicator signs and publishes a report regardless of direction.

## Proposed $5,000 Allocation

| Item | Ceiling |
|---|---:|
| External replicator honorarium | $3,500 |
| Independent compute and storage | $1,000 |
| Public report, discrepancy resolution, and archival release | $500 |

Payments compensate execution and reporting, not a positive result. The final
recipient, invoices, deviations, and unused balance will be included in the
public spend ledger.
