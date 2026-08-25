# VM Execution Provenance

## Launch

- Campaign: `mbe3-oracle-feasibility-frontier-v1`
- Authorized project: `unesco-504802`
- Authorized instance: `mbe-calibration-20260811`
- Zone: `us-central1-f`
- Remote workspace: `/home/apara/mbe-calibration`
- Launch time: 2026-08-22 20:29:52 UTC
- Worker ceiling: 16 experiment workers
- Service: `mbe-oracle-frontier.service`
- Output: `experiments/30_oracle_feasibility_frontier/out/v1`

The first start attempt failed with Google Cloud
`ZONE_RESOURCE_POOL_EXHAUSTED` because `n2-standard-16` capacity was
unavailable in `us-central1-f`. While the instance remained stopped, its
hardware profile was changed to `e2-standard-16`. The same authorized VM,
boot disk, frozen scripts, task grid, seeds, thresholds, and output path were
retained. No scientific setting changed.

Remote SHA-256 values for the preregistration, runner, validator,
`mbe_eval/orthogonal.py`, and `mbe_eval/crossfit.py` matched
`FROZEN_SHA256SUMS` before launch. The VM reported Python 3.11.2 with NumPy,
pandas, SciPy, and scikit-learn installed in the campaign virtual environment.

Google Compute Engine retains `maxRunDuration=86400s` and
`instanceTerminationAction=STOP`; based on the recorded start timestamp, the
automatic stop boundary is 2026-08-23 20:26:55 UTC.

## Initial Health Check

The service entered `activating/start`, one coordinator and exactly 16 workers
were present, all workers were CPU-bound, memory and disk pressure were absent,
and no non-estimable row had been observed at the first failure-count check.
Terminal row-count, duplicate, estimability, manifest, protected-read, and hash
gates must pass before results are interpreted.

## Completion

- Terminal state: `COMPLETE`
- Completion time: 2026-08-23 05:50:45 UTC
- Final rows: 126,000 / 126,000
- Final validation: all gates passed remotely and independently after local
  synchronization
- Non-estimable rows: 0
- Duplicate task keys: 0
- Protected associations opened: no

The complete ledger, summary, diagnostic, manifest, output hashes, service
logs, validation report, and campaign state were synchronized into this
experiment directory before the VM was stopped.
