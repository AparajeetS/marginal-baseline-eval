# mbe-eval v0.2.0

PyPI: https://pypi.org/project/mbe-eval/0.2.0/

This release updates the project from a single FIM_norm demonstration into a reusable Marginal Baseline Evaluation (MBE) audit package and ships the current large-scale experiment evidence.

## Highlights

- Published `mbe-eval==0.2.0` on PyPI.
- Added dataframe-first APIs:
  - `audit_metric`
  - `audit_metrics`
  - `partial_rank_corr`
  - `classify_effect`
- Kept backward compatibility for `MBEEvaluator`.
- Removed mandatory PyTorch, plotting, and rich-console dependencies from the core package.
- Made `compute_fim_norm` an optional PyTorch utility via `mbe-eval[torch]`.
- Added unit tests for core MBE behavior and backward compatibility.
- Added large-scale image/text experiment scripts, analysis outputs, and progress logs.

## Current Evidence Snapshot

The current confirmed experiment pool contains 680 models:

- 480 CIFAR-10 image models.
- 200 character-transformer language models.

FIM_norm now has a sharper audit story:

| Audit | n | Raw rho | MBE partial rho | Class |
|---|---:|---:|---:|---|
| Image only, default controls | 480 | -0.662 | -0.218 | survives |
| Text only, default controls | 200 | -0.291 | +0.014 | washout |
| Full image+text pool | 680 | +0.225 | -0.203 | reverse-inversion |
| Full pool, also controlling validation loss | 680 | +0.225 | -0.300 | reverse-inversion |

The key result is selectivity: MBE weakens fragile pooled artifacts while preserving several stable predictors.

## Validation

- `python -m pytest -q`
- `python -m build`
- `python -m twine check dist\mbe_eval-0.2.0*`
