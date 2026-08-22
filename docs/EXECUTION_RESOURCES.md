# Execution Resources

Status: planning specification for future scale confirmation, not a record of
completed compute.

This document estimates workloads needed to execute the research protocol. It
contains no vendor quote, monetary plan, or assumption that scientific quality
is measured by GPU-hours.

Corrected smaller image and causal-language artifacts are already public. Their
protected associations remain sealed because the calibration gate did not
pass; additional large sweeps are released only after a new rule succeeds on
fresh known-truth development and disjoint confirmation data.

## Resource Envelope

The minimum operational range is approximately 315-550 RTX 4090-equivalent
GPU-hours. A broader validation envelope may reach roughly 650 equivalent hours
when public-corpus and pilot gates support the extension.

These ranges assume:

- public model corpora supply part of the benchmark;
- calibration and most statistical analysis run on CPU;
- new training uses reproducible small and medium standard models;
- interrupted jobs support checkpoint and resume;
- checkpoints are curated rather than retained indiscriminately;
- expensive metric families are narrowed by mechanism when pilot runtime
  exceeds the frozen range.

## Minimum Workload

| Work package | Minimum design | 4090-equivalent GPU-hours |
|---|---|---:|
| Public-corpus checkpoint and metric extraction | one substantial corpus | 60-100 |
| Corrected image factorial | 240 runs | 70-120 |
| Corrected causal-text factorial | 100 runs | 70-120 |
| Protected external holdout | public environment or 80-120 new runs | 30-80 |
| Repeatability and batch-size checks | selected checkpoints | 25-40 |
| Pilots, preemption recovery, and approved reruns | controlled reserve | 60-90 |
| **Planning range** |  | **315-550** |

The 340-run factorial consists of 68 configuration blocks with five repeated
seeds:

```text
Image: 2 datasets x 3 architectures x 8 configurations x 5 seeds = 240
Text:  1 dataset x 2 model sizes x 10 configurations x 5 seeds = 100
```

The runs are not treated as 340 independent observations.

## Compute-Release Gates

| Gate | New compute | Requirement |
|---|---:|---|
| Known-truth calibration | CPU | null, proxy, deceptive-control, and signal cases calibrated |
| Public-corpus comparison | 60-100 GPU-h | stable distinction beyond prior methods |
| End-to-end pilot | 15-25 GPU-h | leakage, IDs, recovery, schema, and runtime checks pass |
| Image factorial | 70-120 GPU-h | configurations, seeds, splits, and metric cards frozen |
| Causal-text factorial | 70-120 GPU-h | causal mask and target computation tested |
| Protected holdout | 30-80 GPU-h | commit, container, hypotheses, and command timestamped |
| Reliability checks | 20-40 GPU-h | conclusions survive blocked uncertainty and sensitivity |

No main sweep begins before known-truth calibration, public-corpus comparison,
and the end-to-end pilot pass.

## Operational Controls

Before each compute-heavy gate:

1. freeze the run matrix and expected output schema;
2. estimate runtime from a representative pilot;
3. verify checkpoint/resume and duplicate-run prevention;
4. define automatic shutdown and missing-cell rules;
5. record hardware, software, dataset, and container identifiers;
6. reconcile completed, failed, and retried jobs daily;
7. admit reruns only for documented execution failures or preregistered
   uncertainty checks.

The final reserve is limited to missing factorial cells and declared
uncertainty-critical reruns.

## Storage And Artifact Rules

- retain raw ledgers, manifests, split hashes, and primary checkpoints;
- discard redundant intermediate checkpoints after hash and schema validation;
- keep protected outcomes inaccessible until the freeze is published;
- record artifact provenance independently of a specific cloud provider;
- make final table regeneration possible without retraining.

## Out Of Scope

The planned envelope does not include:

- full ImageNet training across hundreds of configurations;
- pretraining modern large language models from scratch;
- exhaustive evaluation of every published metric;
- post-hoc rerunning until a preferred conclusion appears;
- CEI-R design or tuning on the protected holdout.

If larger-model evidence becomes necessary, released checkpoints and public
corpora are preferred. Repeated seeds, valid controls, and independent task
families take priority over prestige-scale training.

## Decision Rule

Compute is a gated experimental input. When a preceding scientific gate fails,
the next workload pauses until the claim or design is revised.
