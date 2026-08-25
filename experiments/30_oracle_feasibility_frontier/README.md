# Experiment 30: Oracle Feasibility Frontier

This known-truth study diagnoses whether MBE's small-sample difficulty comes
from limited information, noisy metric measurement, or learned nuisance
estimation. See `PREREGISTRATION.md` for the frozen design and claim boundary.

Run a smoke test:

```bash
python experiments/30_oracle_feasibility_frontier/run_frontier.py \
  --output-dir experiments/30_oracle_feasibility_frontier/out_smoke --smoke
```

Run the frozen campaign:

```bash
python experiments/30_oracle_feasibility_frontier/run_frontier.py \
  --output-dir experiments/30_oracle_feasibility_frontier/out/v1 --workers 16
python experiments/30_oracle_feasibility_frontier/validate_outputs.py \
  --output-dir experiments/30_oracle_feasibility_frontier/out/v1
```

The runner is resumable through `frontier_ledger.partial.csv`. Final outputs
include the complete ledger, cell summary, sample-size diagnostics, manifest,
and SHA-256 checksums.

