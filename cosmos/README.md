# Cosmos Benchmark Audit Toolkit

**Status:** active pre-funding work while the Cosmos application is under review  
**Last updated:** 11 August 2026  
**Working branch:** `agent/benchmark-audit-prototype`

This is the landing area for the project proposed to the Cosmos Institute: a
small, open toolkit for testing whether an AI benchmark score supports a
specific claim after declared baseline information and environment shifts are
taken seriously.

The point is not to certify benchmarks. The point is to make their claims
precise enough to test, reproduce, and challenge.

## Start here

1. Read the short [Cosmos reviewer guide](../COSMOS_REVIEWER_GUIDE.md).
2. See the exact [90-day research and execution plan](../COSMOS_90_DAY_EXECUTION_PLAN.md).
3. Inspect the [current deliverable checklist](DELIVERABLE_CHECKLIST.md).
4. Read the [starting baseline freeze](BASELINE_FREEZE.md).
5. Inspect the frozen [TruthfulQA pilot result](../experiments/08_truthfulqa_real_audit/artifacts/RESULTS.md)
   and its machine-readable [claim card](../experiments/08_truthfulqa_real_audit/artifacts/claim_card.json).

## Progress since the application

The application linked to the main MBE repository before this dedicated branch
and reviewer path existed. Work completed since then includes:

- an experimental benchmark-claim audit interface;
- a claim-card renderer that keeps the claim, baselines, environments,
  estimands, evidence states, and limitations together;
- a contestation interface for comparing reasonable alternative
  specifications;
- a deterministic synthetic trap in which a plausible score should fail after
  ordinary capability information is included;
- a protocol-frozen real-data pilot using released TruthfulQA v0 judgments;
- explicit leakage inspection and exclusions before the pilot result was run;
- 68 passing automated tests; and
- this project-specific landing area, execution plan, and reproducibility
  baseline.

These are prototype milestones, not evidence that the method is generally
valid. The next important test is whether the workflow remains informative on
a second benchmark with a materially different structure.

## Current evidence boundary

The TruthfulQA pilot found that the candidate reference-difference score
crossed the predeclared E1 incremental-information threshold and the aggregate
E2 category-transport threshold. Supplied controls did not. That result is
conditional on the frozen data, exclusions, target, proxies, grouping, and
thresholds.

It does not establish construct validity, causality, general model capability
control, or independent validation of TruthfulQA or MBE. The labels and
references arose within the same broader evaluation framework, which is why
the pilot is described as a real-data method demonstration.

## What happens next

Work proceeds through evidence gates:

1. preserve and reproduce the current baseline;
2. harden the input, evidence-state, claim-card, and contestation interfaces;
3. expand synthetic controls that the method must fail correctly;
4. inspect Anthropic's sycophancy evaluations and at least one fallback against
   a written dataset-selection gate;
5. freeze the second benchmark protocol before computing its candidate result;
6. publish the result even if it is negative or unresolved; and
7. obtain a cold-start reproduction by someone who did not build the toolkit.

The second benchmark will not be forced into the method. If the released data
do not provide an honest target, baseline set, environment definition, or
independence unit, the rejection decision will be published instead.

## Reproduce the current software baseline

From a clean checkout:

```bash
git clone https://github.com/AparajeetS/marginal-baseline-eval.git
cd marginal-baseline-eval
git checkout agent/benchmark-audit-prototype
python -m pip install -e ".[dev]"
python -m pytest -q
python -m mbe_eval.claim_demo --output-dir benchmark-audit-demo
```

The TruthfulQA path uses a pinned upstream commit and is documented in
[`experiments/08_truthfulqa_real_audit/README.md`](../experiments/08_truthfulqa_real_audit/README.md).

## Relationship to the larger MBE project

The Benchmark Audit Toolkit is a narrow 90-day proposal focused on E0 through
E2 claim auditing, a second real-data benchmark, usable public artifacts, and
independent reproduction. It is not the full MBE 2.0 research program, the
larger training-metric validation matrix, or a benchmark certification
service. Those longer-horizon directions remain separate so that progress on
this proposal can be judged against what was actually promised.

