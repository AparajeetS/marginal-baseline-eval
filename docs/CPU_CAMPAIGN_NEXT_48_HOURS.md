# MBE CPU Campaign: Next 48 Hours

Status: completed historical execution and synthesis plan, frozen 2026-07-29.

The VM shutdown deadline is 2026-07-31 00:30 UTC
(2026-07-31 06:00 IST). The remaining VM window is shorter than 48 hours, so
compute work must finish before that deadline. Local validation and writing may
continue after shutdown.

## Objective

Use the remaining CPU allocation to close three specific credibility gaps:

1. determine whether the degree-6 interaction veto in the observed text design
   is caused by excessive nuisance complexity;
2. finish high-repetition calibration of the refit and residual-permutation
   inference paths;
3. measure whether 99, 199, and 499 refit draws give decisions stable enough
   relative to a paired 999-draw reference.

This window does not add trained models, protected-holdout evidence, or
cross-task generalization evidence. It must not be reported as GPU-scale model
evidence.

## Operating Rules

- Access only the designated 16-vCPU campaign VM.
- Never exceed 16 active experiment workers.
- Do not inspect partial scientific outcomes to change a grid or select a
  favorable nuisance model.
- Infrastructure failures may be resumed with identical settings. Scientific
  estimation failures are retained and reported.
- Every transition requires process exit, expected artifacts, exact row counts,
  schema checks, duplicate checks, and a recorded manifest.
- No new compute-heavy job starts within six hours of the shutdown deadline.
- Completed outputs are hashed and copied to the local repository before the
  VM is stopped.
- The system shutdown timer must remain scheduled for
  `2026-07-31 00:30:00 UTC`.
- Do not commit or push automatically.

## State Machine

### Stage 0A: Degree-2 Observed-Design Sensitivity

Current command:

```bash
python experiments/16_causal_text_observed_design_power/run_power.py \
  experiments/15_causal_text_factorial_replication/kaggle_downloads/v1/mbe2_causal_text_factorial_replication.csv \
  --output-dir experiments/16_causal_text_observed_design_power/out_sensitivity_degree2 \
  --repetitions 100 --refit-bootstrap 199 --permutations 99 \
  --degree 2 --workers 8
```

Completion gate:

- the parent and all workers have exited successfully;
- `power_ledger.csv` has exactly 9,000 rows;
- `power_summary.csv` has exactly 45 rows;
- all 9,000 ledger rows have `status == estimated`;
- there are exactly 4,500 unique
  `(reliability_tier, baseline, beta, repetition)` cells and two nuisance rows
  per cell;
- the manifest records degree 2, 100 repetitions, 199 refits, and seed
  `20260729`.

After the gate passes, create a degree-2 versus degree-6 comparison without
changing the degree-6 primary result. Report null support, power by effect,
nuisance-family disagreement, and strict consensus separately.

### Stage 0B: Corrected Inference Stress

Current workload: eight amended shards with `n = 100, 150, 200, 300`, 25
repetitions per shard, 199 refits, 199 refit permutations, 250 block-null
repetitions per shard, and 999 block permutations.

Completion gate:

- all eight shard processes have exit status zero;
- every shard has 1,000 refit-ledger rows and 1,000 block-ledger rows;
- the pooled refit ledger has exactly 8,000 rows;
- the pooled block ledger has exactly 8,000 rows;
- every refit cell has 200 repetitions;
- every block structure has 2,000 repetitions;
- no duplicate shard/repetition/scenario/nuisance or
  shard/structure/repetition keys exist;
- `merge_campaign.py` exits zero and records these counts.

After the gate passes, report Wilson intervals for each block-null rejection
rate and false-support/power curves by sample size and nuisance family.
Residual permutation remains diagnostic regardless of whether its point
estimate improves.

### Stage 1: Frozen Nuisance-Complexity Map

This stage may start only after Stage 0A passes. It is known-truth calibration,
not real-metric outcome selection.

Observed-design arm:

- repeat the complete observed-design grid at degrees 1, 3, and 4;
- retain 100 repetitions, all three reliability tiers, B1/B2/B3, all five
  injected effects, both nuisance families, 199 refits, 99 permutations, and
  the existing seed;
- run the three degrees sequentially with eight workers;
- require 9,000 ledger rows, 45 summary rows, and zero unreported estimation
  failures per degree.

Generic-proxy arm:

- run polynomial ridge and polynomial ridge with interactions at degrees
  1, 3, and 4;
- retain `n = 100, 200, 400, 800`, 100 repetitions, 499 permutations, 499
  bootstrap draws, and the existing calibration seed;
- use one process for each degree-by-family cell, for at most six workers;
- retain all null, proxy, post-treatment, and signal scenarios.

The combined table covers degrees 1, 2, 3, 4, and 6. A specification is not
called calibrated merely because it has power. Null/proxy control,
observed-design null behavior, estimability, and injected-signal power are
reported as separate axes. No degree is promoted to the real-metric primary
analysis during this campaign.

### Stage 2: Paired Refit-Draw Convergence

Run `experiments/18_refit_draw_convergence/run_draw_convergence.py` after one
current eight-worker lane has completed and enough CPU is free. Use 100 paired
simulation repetitions, `n = 150`, both nuisance families, all five known-truth
scenarios, 199 residual permutations, and refit draw counts
`99, 199, 499, 999`.

Completion gate:

- the process exits zero;
- the ledger has exactly 4,000 rows;
- the summary has exactly 40 rows;
- the convergence table has exactly 30 rows;
- every paired cell is estimable;
- there are no duplicate repetition/scenario/nuisance/draw keys;
- the manifest matches the frozen settings.

The 999-draw result is a higher-draw Monte Carlo reference, not ground truth.
Report paired decision agreement, directional flip rates, and lower-bound
movement. The purpose is to choose a defensible default draw budget, not the
draw count that produces the most positive findings.

### Stage 3: Synthesis And Software Gate

After Stages 0-2 pass or their failures are documented:

1. regenerate pooled campaign tables from raw ledgers;
2. write one nuisance-complexity ablation table spanning degrees 1-6;
3. update the statistical specification to separate the predictive estimand,
   nuisance calibration gate, and residual diagnostic;
4. update the claim ledger, evidence index, credibility ledger, supporting
   evidence, and JMLR manuscript skeleton;
5. add tests for any changed report or API behavior;
6. run the full test suite in a clean environment;
7. build wheel and source distribution;
8. run a fresh install-and-smoke test;
9. write SHA-256 manifests for all new outputs and copy them locally;
10. record incomplete cells and negative results with the same prominence as
    favorable results.

No automated commit, push, PyPI release, or manuscript submission occurs.

## Two-Day Schedule

### Day 1: Completion And Calibration

- Monitor Stages 0A and 0B every 30 minutes.
- Validate and sync each lane immediately after its gate passes.
- Start the observed-design complexity arm when Stage 0A frees eight cores.
- Start the generic-proxy arm when at least six additional cores are free.
- Start paired refit-draw convergence when worker capacity permits without
  exceeding 16.
- Preserve logs and amendments before inspecting aggregate results.

### Day 2: Analysis, Reproducibility, And Handoff

- Finish any Stage 1 or Stage 2 work early enough to leave six hours for
  validation and transfer.
- Build the combined ablation, inference-calibration, and convergence tables.
- Reconcile every affected public claim and paper placeholder against those
  tables.
- Run tests, package builds, reproduction commands, and hash checks.
- Sync all completed evidence to the designated local repository checkout.
- Verify the shutdown timer and stop launching work by
  2026-07-30 18:30 UTC.
- Permit the scheduled shutdown no later than 2026-07-31 00:30 UTC.

## End State

The campaign is complete when the repository contains validated raw ledgers,
manifests, summaries, logs, hashes, a nuisance-complexity ablation, a
refit-draw convergence report, updated claim boundaries, and a passing package
build. If a gate fails, the end state is a documented failure and narrowed
claim, not a substituted experiment.
