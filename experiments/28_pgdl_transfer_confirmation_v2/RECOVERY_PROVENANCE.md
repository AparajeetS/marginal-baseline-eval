# Worker-Initialization Recovery

The first confirmation attempt did not execute the preregistered degree-2,
ridge-0.1 rule. Under Windows multiprocessing spawn, workers imported the
experiment 26 source module with its degree-4, ridge-10 defaults; the overrides
had been applied only in the parent process.

The defect was detected because all score and p-value columns were exactly
equal to experiment 26. The invalid scientific-run bundle was removed from the
current tree because it did not execute the preregistered method; its source
freeze and original file hashes remain recoverable from Git history under
`FROZEN_SHA256SUMS_V1_WORKER_INITIALIZATION_FAILURE`. The non-scientific smoke
outputs are not evidence. The concise recovery record is retained here.

The recovery changes only worker initialization: every spawned process now
sets the already-preregistered protocol ID, degree 2, and ridge 0.1 before any
cell runs. The confirmation grid, seeds, simulations, thresholds, and gate are
unchanged. A confirmation-runner hash was also added to the generated manifest.
No protected target or checkpoint metric was read before or during recovery.
