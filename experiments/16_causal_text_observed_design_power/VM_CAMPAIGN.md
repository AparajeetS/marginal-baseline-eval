# 16-vCPU VM Campaign

Started: 2026-07-29 00:30 UTC  
Scheduled shutdown: 2026-07-31 00:30 UTC

Machine:

- Google Compute Engine instance `mbe`, `us-central1-c`
- 16 vCPUs, AMD EPYC 9B45, 60 GiB usable memory
- Ubuntu kernel `7.0.0-1008-gcp`, Python 3.14.4
- source commit anchor `1beed740ab31c0b20f609bac6d38a6fd8d50ed9e`
- worktree transfer SHA-256
  `0ead496c903d1ddf911b90ed25f9a834512ae73475bea9242e7ac5d81d420e10`
- causal-text CSV SHA-256
  `1bffd89562923d701141e502988f7b62072ee312786dc348f4861715328b5ef6`

The transfer contains the exact dirty-worktree package, tests, frozen
calibration scripts, and causal-text artifacts required for the campaign.
Unrelated `experiments/07_jmlr_scale` scratch files were not transferred.

Initial environment validation: 49 tests passed in 2.64 seconds. The VM uses a
systemd shutdown timer and is checked hourly from the active Codex task.

## Verified Results

The independent 199-refit causal-text analysis completed successfully. Against
the original `out_primary_199` result:

- all raw metric keys and consensus keys match;
- every consensus status and strict support decision matches;
- raw Spearman statistics and permutation p-values match exactly;
- the largest absolute difference in a consensus lower bound is
  `3.3460040294031046e-13`.

The machine-readable comparison is
[`vm_campaign_artifacts/reproduction_comparison.json`](vm_campaign_artifacts/reproduction_comparison.json).
The regenerated tables are in
[`../15_causal_text_factorial_replication/out_vm_repro_199/`](../15_causal_text_factorial_replication/out_vm_repro_199/).

## Completed Work

- B1, B2, and B3 999-refit sensitivity chunks completed successfully.
- The frozen 4,500-cell degree-6 observed-design power grid completed.
- All four comparator shards, all three generic Monte Carlo nuisance-family
  grids, package validation, and the Dziugaite public-ledger reproduction
  completed successfully.
- Exact remote logs and result hashes were copied into the corresponding
  experiment directories.

## Active Work

- The eight inference-stress shards are being rerun after the invalid `n=72`
  cell caused a pre-simulation exit. The amendment is recorded in experiment
  17.
- A complete degree-2 observed-design sensitivity is running to test whether
  excessive nuisance flexibility caused the primary interaction-family power
  failure.
