# External Evidence Handoffs

Status: preparation only. No external executor has been selected, contacted,
or represented as committed by this document.

## Independent Execution

The executable known-truth and sealed-PGDL packet is
`experiments/12_independent_replication/replication_packet_v2.json`. A suitable
external executor must have made no contribution to the estimator, candidate
selection, or protected-outcome analysis. They receive the frozen repository
revision, packet manifest, conflict template, and one validation command:

```bash
python experiments/12_independent_replication/validate_packet_v2.py \
  --reviewer "FULL NAME" \
  --conflict-statement "DISCLOSE CONFLICTS OR WRITE NONE" \
  --output-dir external_replication_v2 \
  --run-tests
```

The executor must publish the generated report, add discrepancies or `none
observed`, and sign a conclusion. A passing internal dry run does not count as
an independent replication. The final protected-holdout packet cannot be sent
until a future estimator passes its opening gate.

## External Holdout Candidate Register

Candidate selection must be completed before metric-target associations are
opened. A candidate is eligible only if it meets the requirements in
`experiments/24_external_holdout/PROTOCOL_DRAFT.md`.

| Candidate | Plausible use | Current assessment | Decision |
|---|---|---|---|
| PGDL Tasks 6-9 | Generalization metric transfer | 240 independent models, but previous metadata exposure means it is not wholly unseen; binding calibration gate failed. | Remain sealed. |
| HarmBench / StrongREJECT | Safety-evaluation metric audit | Rich model, attack, defense, and evaluator structure; requires a frozen independent behavioral or human-adjudicated target and unit-of-analysis audit. | Candidate for a new safety work package, not a current holdout. |
| MIB | Mechanistic-interpretability metric audit | Ground-truth intervention setting and metrics are compelling, but the published task/model grid alone may not meet the minimum independent-unit and metadata requirements. | Feasibility/benchmark candidate, not a current holdout. |

No candidate may be substituted after viewing metric-target results. If no
candidate qualifies, this work package reports abstention.

## Prospective Selection Freeze

The selector is evaluated only on task-family outcomes generated after its
recommendations are frozen. The required pre-outcome packet is specified in
`docs/PROSPECTIVE_SELECTION_PROTOCOL.md`. Before beginning a prospective run,
freeze and hash:

1. eligible metrics and their implementations;
2. the declared target, baseline ladder, and utility function;
3. task-family identities and the withheld outcome partition;
4. the selector, its abstention threshold, and all comparators;
5. exact training, extraction, and analysis commands;
6. the selected metric or abstention for each future task family.

The primary unit is a task family. Fewer than 12 families is feasibility-only;
20 or more is preferred for a primary selector claim. A selector result that
does not beat both the global-metric and pooled-correlation selectors, or whose
abstention fails to reduce regret over useful coverage, is reported as a
withdrawn selector claim rather than repaired after outcomes are seen.
