# Cosmos Deliverable Checklist

**Last updated:** 11 August 2026

This checklist separates completed artifacts from work that is planned or in
progress. A checked item means that a public artifact exists on this branch. It
does not mean that Cosmos has funded or endorsed the work.

## Project separation and starting baseline

- [x] Create a Cosmos-specific reviewer landing area.
- [x] Separate the Benchmark Audit Toolkit from the full MBE 2.0 program.
- [x] Publish the detailed 90-day execution plan.
- [x] Reproduce all automated tests from the starting source state.
- [x] Reproduce the deterministic synthetic claim demo.
- [x] Reproduce the pinned TruthfulQA audit without artifact drift.
- [x] Record source versions, commands, results, gaps, and artifact hashes.

## Interface hardening and calibration

- [ ] Freeze the next claim-card schema revision.
- [ ] Strengthen invalid-input and target-leakage failures.
- [ ] Expand deceptive, negative, and abstention synthetic fixtures.
- [ ] Add repeated-unit and environment-holdout regression tests.
- [ ] Add deterministic manifests for generated audit bundles.
- [ ] Document every evidence-state transition with a test fixture.

## Second benchmark selection

- [x] Inspect Anthropic's released sycophancy evaluations before analysis.
- [ ] Inspect at least one independently structured fallback dataset.
- [ ] Record licensing, provenance, target, baselines, environments,
  independence unit, leakage risks, and sample counts for each candidate.
- [ ] Publish accept, reject, or unresolved decisions for every candidate.
- [ ] Select a benchmark only if it passes the written gate.

## Second real-data audit

- [ ] Freeze the primary claim and protocol before candidate-score analysis.
- [ ] Record the immutable source manifest and all exclusions.
- [ ] Construct the derived analysis ledger reproducibly.
- [ ] Run E0, E1, E2, deceptive controls, and named alternatives.
- [ ] Produce Markdown and JSON claim cards.
- [ ] Produce the contestation bundle and correction history.
- [ ] Publish the result regardless of direction.

## Usability and independent reproduction

- [ ] Complete a cold-start run from only the public documentation.
- [ ] Record every ambiguity and repair the instructions.
- [ ] Obtain an independent reproduction or documented failed attempt.
- [ ] Publish the final artifact manifest and completion report.
