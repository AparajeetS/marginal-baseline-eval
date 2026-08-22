# Worker-Initialization Recovery

The first confirmation attempt did not execute the preregistered degree-2,
ridge-0.1 rule. Under Windows multiprocessing spawn, workers imported the
experiment 26 source module with its degree-4, ridge-10 defaults; the overrides
had been applied only in the parent process.

The defect was detected because all score and p-value columns were exactly
equal to experiment 26. The invalid outputs are preserved under
`out_failed_worker_initialization_v1/` and the original smoke outputs under
`out_smoke_failed_worker_initialization_v1/`. The original code freeze is
preserved as `FROZEN_SHA256SUMS_V1_WORKER_INITIALIZATION_FAILURE`.

The recovery changes only worker initialization: every spawned process now
sets the already-preregistered protocol ID, degree 2, and ridge 0.1 before any
cell runs. The confirmation grid, seeds, simulations, thresholds, and gate are
unchanged. A confirmation-runner hash was also added to the generated manifest.
No protected target or checkpoint metric was read before or during recovery.
