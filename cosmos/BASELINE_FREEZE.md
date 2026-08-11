# Starting Baseline Freeze

**Freeze date:** 11 August 2026

**Purpose:** establish the reproducible starting point for continued work on
the Cosmos Benchmark Audit Toolkit before new analysis is added

## Frozen source state

- Branch: `agent/benchmark-audit-prototype`
- Starting commit: `0aeaf145e65029aab86f87523f0f27ed6a783f2f`
- Package version: `mbe-eval 0.4.0`
- Python used for this reproduction: `3.14.3`
- Operating system: Windows NT 10.0.26200.0
- TruthfulQA source commit:
  `d71c110897f5d31c5d7f309e7bc316c152f6f031`

This freeze records the state from which the Cosmos-specific work continues.
It does not retroactively preregister the existing pilot.

## Reproduction results

### Automated tests

Command:

```bash
python -m pytest -q
```

Result:

```text
68 passed in 5.92s
```

### Deterministic synthetic claim demo

Command:

```bash
python -m mbe_eval.claim_demo --output-dir benchmark-audit-demo
```

Result:

```text
Synthetic predeclared test outcome: supports-claim-under-declared-tests
```

The command produced a synthetic ledger plus Markdown and JSON claim cards.
This fixture is an implementation check, not real-world validation.

### TruthfulQA pilot

Command:

```bash
python experiments/08_truthfulqa_real_audit/run_truthfulqa_audit.py \
  --truthfulqa-root ../TruthfulQA-source
```

Result:

- the runner completed successfully;
- the predeclared state remained
  `supports-claim-under-declared-tests`;
- the tracked result artifacts were reproduced without a diff; and
- E1 remained `+0.1233` relative out-of-fold MSE improvement while aggregate
  E2 remained `+0.1101`.

## Frozen artifact hashes

SHA-256 hashes after reproduction:

```text
ec08ccf8d6fd6f09a0545f50b0d156467d1e72b758e78379b71c1a5cc854ba32  experiments/08_truthfulqa_real_audit/artifacts/claim_card.json
9ddada009d6bd14c01be35dc20f6a7c0cf7fa845b108cc89f508f4835b5681c1  experiments/08_truthfulqa_real_audit/artifacts/derived_ledger.csv
c66907d072311ebd2d4a23f182a55efc252bf38e57b0f31c6c18e76d5ad3218a  experiments/08_truthfulqa_real_audit/artifacts/cohort_manifest.json
097b9603da501c653bc20164ee259ef862738289c76c1bb4f470db59fd12c2e1  experiments/08_truthfulqa_real_audit/artifacts/RESULTS.md
```

## Gate decision

**Gate passed.** The existing prototype, test suite, synthetic self-check, and
TruthfulQA reproduction path are operational from the frozen starting commit.
No unexplained discrepancy was found, so work may proceed to interface
hardening, calibration expansion, and second-benchmark selection.

## Known gaps carried forward

- The Cosmos application linked only to the default repository, while this
  benchmark-audit work lives on a separate branch.
- The demo is runnable code, not a hosted browser application.
- The current real-data evidence comes from one pilot with an internal target.
- General capability is not controlled in the TruthfulQA pilot.
- No independent cold-start reproduction has been completed.
- The second benchmark has not passed its dataset-selection gate.

These gaps are work items, not details to be hidden by the passing baseline.
