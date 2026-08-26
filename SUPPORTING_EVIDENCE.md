# Current Evidence Summary

This page is the short entry point to the current MBE evidence. It replaces the
former root-level exploratory ledger, which is preserved unchanged as the
[MBE v1 supporting-evidence archive](docs/archive/SUPPORTING_EVIDENCE_V1.md).
That archive documents the historical 680-row pilot and its corrections; it is
not confirmatory evidence for MBE 2.0.

## What The Public Record Establishes

- The `mbe-eval` package, CLI, examples, validators, calibration harnesses, and
  reproduction paths are implemented and public.
- Corrected prospective infrastructure produced a 96-run image factorial, a
  144-run multi-corpus causal-LM atlas, a 180-run causal-text replication, and
  a separate 360-model image target-transport atlas. Their structural and
  causal-validity checks are recorded with hashes and manifests.
- Known-truth studies expose a reproducible calibration-power frontier. In the
  frozen oracle study, 24 independent configurations were underpowered even
  with known nuisance functions. At 48 configurations, the observable oracle
  passed the stated calibration and power gates, showing that useful signal was
  present in that design.
- Learned rules at 48 configurations did not clear the same bar: their
  worst-null false-support rates were 14.2-15.2%. The current estimator is
  therefore not validated for protected-data opening.
- A 153,600-row comparator benchmark found no tested MBE or conditional-
  independence procedure that combined strict worst-cell calibration with
  useful worst-cell power at 24/48 configurations.

## Evidence Boundary

Protected image, text-atlas, PGDL, and SVHN target-metric associations remain
sealed because their prespecified opening gates did not pass. No protected
association should be inferred from artifact completion or model counts.
External holdout evidence and an independently executed, signed replication
are still missing. The project does not currently establish universal MBE
validity, universal metric failure, causal metric effects, a production metric
selector, or completed AI-safety evidence.

The proposed safety study would audit automated jailbreak or harmfulness judges
against independently defined human assessments. StrongREJECT is useful
development data but has only 47 observed model-by-jailbreak blocks, below the
current 48-block floor; HarmBench remains a prospective transfer candidate
pending canonical intake, independence, and licensing checks. Eligibility also
requires a newly frozen known-truth rule to pass before outcomes are opened.

## Reviewer Path

1. Read the [one-page scientific status](docs/PROJECT_STATUS.md).
2. Use the [evidence index](docs/EVIDENCE_INDEX.md) for claim-to-artifact
   mapping and the [experiment synthesis](docs/EXPERIMENT_EVIDENCE_SYNTHESIS.md)
   for program-level detail.
3. Follow the [reproducibility guide](REPRODUCIBILITY.md) and
   [artifact-integrity guide](docs/ARTIFACT_INTEGRITY.md).
4. Consult the [adversarial credibility ledger](docs/MBE_CREDIBILITY_LEDGER.md)
   for every failed, blocked, withdrawn, and unresolved gate.

Negative scientific results and validity corrections remain in the active
record. The archived v1 ledger is retained for provenance and regression
context, not promoted as current evidence.
