# Independent Replication Protocol

Status: active research protocol. The external replicator is not yet
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

The replicator receives only after the estimator and opening rule are frozen:

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

## Current Boundary

The known-truth and PGDL-calibration handoff is prepared as
`experiments/12_independent_replication/replication_packet_v2.json` with a
one-command validator. It contains no protected association and expects the
current sealed decision. It has not yet been run or signed by an independent
executor. The final protected-holdout packet remains blocked until a future
estimator passes its opening gate. A failed or null replication remains a valid
deliverable and must be retained in the public discrepancy log.

## Reporting Boundary

The replicator reports methods, discrepancies, unresolved failures, and the
final conclusion regardless of direction. Any logistical arrangement must not
condition compensation, authorship, or publication rights on a positive
result.
