# Roadmap

## Current State

- `mbe-eval==0.3.0` is published on PyPI.
- The repository includes a 680-model evidence set across image and text runs.
- CPU-only bootstrap CIs and threshold-sensitivity tables are generated from saved CSVs.
- Public Kaggle notebook and figures are available.

## No-Compute Priorities

- Polish manuscript sections from `PAPER_SKELETON.md`.
- Turn current figures into publication-ready versions.
- Expand related work notes.
- Keep protocol and taxonomy frozen unless changes are explicitly versioned.

## Compute-Required Priorities

- Run the locked holdout protocol in `NEXT_EXPERIMENT_PROTOCOL.md`.
- Add block-level bootstrap over seed/config groups.
- Add control-set ablations:
  - no controls;
  - hyperparameters only;
  - hyperparameters + architecture/task;
  - strict + validation loss.
- Add one additional task or dataset if compute allows.

## Release Priorities

- Keep `mbe-eval` focused on reusable MBE audits rather than paper-specific scripts.
- Add more examples for real CSV ledgers.
- Add plotting helpers only after the core API stabilizes.
