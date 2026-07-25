# mbe-eval v0.3.0

PyPI: https://pypi.org/project/mbe-eval/0.3.0/

This release makes `mbe-eval` easier to evaluate as a standalone research
package and aligns the package metadata with the renamed repository:

https://github.com/AparajeetS/marginal-baseline-eval

## Highlights

- Added `mbe-eval-demo`, a CPU-only command-line demo that runs a synthetic MBE
  audit and writes a markdown report.
- Added `mbe-eval-audit`, a CSV command-line tool for auditing a user's own
  training-run ledger.
- Added markdown reporting helpers:
  - `summarize_audit`
  - `audit_report_markdown`
  - `write_markdown_report`
- Added public demo data generation:
  - `make_demo_runs`
  - `run_demo`
- Updated package metadata and PyPI project links to point at the renamed
  research repository, evidence ledger, and Kaggle notebook.
- Added `SUPPORTING_EVIDENCE.md` with run-by-run Kaggle and independent audit
  findings.
- Added `REPRODUCIBILITY.md` for local checks, saved-artifact analysis, and
  GPU-required replication paths.

## Quick Test

```bash
pip install mbe-eval
mbe-eval-demo --bootstrap 200
mbe-eval-audit --csv runs.csv --metrics fim_norm,val_loss --target test_acc --controls lr,wd,arch
```

## Validation

```bash
python -m pytest -q
python -m build
python -m twine check dist\mbe_eval-0.3.0*
```
