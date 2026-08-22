# MBE / Metric Audit Progress Log

Date: 2026-06-28

> **Historical record:** This log predates the v1 evidence audit. Its
> “confirmed” labels describe run completion, not submission-grade scientific
> confirmation. The 680-row pool contains repeated configurations, and its
> legacy text setup lacks a causal attention mask and permits label leakage.
> See `README.md` and `docs/MBE_2_RESEARCH_PROGRAM.md` for the current protocol.

This log records the state of the current large-scale MBE run sequence.

## 1. Package and Code State

- Package state at the time of the run: `mbe-eval==0.2.0`
- Current polished package release target: `mbe-eval==0.3.0`
- PyPI release page: https://pypi.org/project/mbe-eval/
- Core package now supports:
  - raw rank-correlation audits
  - partial rank-correlation MBE controls
  - numeric and categorical controls
  - grouped audits
  - bootstrap confidence interval support
  - backward-compatible `MBEEvaluator`
- `analyze_jmlr_scale.py` was patched so strict audits can include `val_loss` as a covariate without choking on duplicate metric/control columns.

## 2. Confirmed Experiment Outputs

| Dataset/suite | Source file | Models | Notes |
|---|---:|---:|---|
| Image v2 | `experiments/07_jmlr_scale/kaggle_downloads/image_v2/jmlr_scale_image_results.csv` | 160 | 40 each: CNN, ResNet, ViT, WideResNet |
| Image confirmation | `experiments/07_jmlr_scale/kaggle_downloads/confirm_image/jmlr_confirm_image_results.csv` | 320 | 80 each: CNN, ResNet, ViT, WideResNet |
| Text v2 | `experiments/07_jmlr_scale/kaggle_downloads/text_v2/jmlr_scale_text_results.csv` | 80 | char-transformer LM |
| Text confirmation | `experiments/07_jmlr_scale/kaggle_downloads/confirm_text/jmlr_confirm_text_results.csv` | 120 | char-transformer LM |
| Full confirmed pool | all four CSVs | 680 | 480 image + 200 text |

## 3. Generated Audit Reports

Main reports generated from the completed runs:

- `experiments/07_jmlr_scale/jmlr_confirm_image_audit_summary.md`
- `experiments/07_jmlr_scale/jmlr_confirm_text_audit_summary.md`
- `experiments/07_jmlr_scale/jmlr_image_combined_480_audit_summary.md`
- `experiments/07_jmlr_scale/jmlr_image_combined_480_strict_loss_mbe_summary.md`
- `experiments/07_jmlr_scale/jmlr_text_combined_200_audit_summary.md`
- `experiments/07_jmlr_scale/jmlr_text_combined_200_strict_loss_mbe_summary.md`
- `experiments/07_jmlr_scale/jmlr_full_confirmed_680_audit_summary.md`
- `experiments/07_jmlr_scale/jmlr_full_confirmed_680_strict_loss_mbe_summary.md`

## 4. Main Finding

The strongest result is not that FIM_norm simply fails everywhere. The stronger result is that FIM_norm is unstable under ordinary evaluation choices:

- It survives in image-only pooled audits.
- It washes out in text-only audits.
- It reverses sign in the full image+text pooled audit.
- It behaves differently across architectures.
- MBE does not kill everything; it separates stable predictors from fragile pooled artifacts.

## 5. FIM_norm Summary

| Audit | n | Raw rho | MBE partial rho | Class |
|---|---:|---:|---:|---|
| Image only, default controls | 480 | -0.662 | -0.218 | survives |
| Image only, strict + val_loss | 480 | -0.662 | -0.383 | survives |
| Text only, default controls | 200 | -0.291 | +0.014 | washout |
| Text only, strict + val_loss | 200 | -0.291 | +0.188 | weak-or-mixed |
| Full 680, default controls | 680 | +0.225 | -0.203 | reverse-inversion |
| Full 680, strict + val_loss | 680 | +0.225 | -0.300 | reverse-inversion |

## 6. Metrics Weakened Besides FIM_norm

Full 680 default audit:

| Metric | Raw rho | MBE partial rho | Class |
|---|---:|---:|---|
| feature_erank | -0.538 | +0.097 | washout |
| feature_norm_mean | -0.425 | +0.071 | washout |
| distance_from_init_l2 | +0.672 | +0.014 | washout |
| update_to_weight_ratio | +0.241 | +0.066 | washout |
| weight_l1 | +0.614 | -0.027 | washout |
| weight_l2 | +0.685 | +0.093 | washout |

Full 680 strict audit with validation loss also controlled:

| Metric | Raw rho | MBE partial rho | Class |
|---|---:|---:|---|
| asam_sharpness | -0.700 | -0.070 | washout |
| feature_cosine_mean | +0.786 | -0.031 | washout |
| feature_norm_mean | -0.425 | +0.069 | washout |
| grad_noise_scale | -0.424 | -0.028 | washout |

## 7. Metrics That Survived

The following survived the full 680 strict audit, showing that MBE is selective rather than indiscriminately destructive.

| Metric | Raw rho | MBE partial rho | Class |
|---|---:|---:|---|
| fisher_trace | -0.809 | -0.390 | survives |
| grad_norm | -0.809 | -0.376 | survives |
| logit_norm_mean | +0.890 | +0.533 | survives |
| metric_batch_acc | +0.621 | +0.436 | survives |
| confidence_mean | +0.833 | +0.536 | survives |
| entropy_mean | -0.856 | -0.569 | survives |

## 8. Recommended Paper Narrative

Working title:

> Marginal Baseline Evaluation: Auditing Generalization Metrics Beyond Pooled Correlation

Core claim:

> Many proposed generalization metrics look predictive under pooled raw correlation. MBE asks whether a metric keeps predictive signal after controlling for ordinary baselines and experimental design variables. In a 680-model audit across image and language-model experiments, MBE distinguishes stable predictors from fragile metrics whose conclusions wash out, invert, or depend on task/architecture.

Avoid claiming:

- FIM_norm is universally useless.
- MBE proves causality.
- All geometric metrics fail.

Prefer claiming:

- Raw pooled metric evaluation is insufficient.
- FIM_norm is a useful case study because it looked plausible, then failed under stronger auditing.
- MBE exposes washout, sign inversion, hidden-after-control, and task/architecture dependence.
- MBE is selective: several validation, gradient/Fisher magnitude, confidence/logit, and task-proximal metrics survive.

## 9. Remaining Work Before Submission

Must-have:

1. Freeze the analysis protocol:
   - raw correlation
   - MBE partial correlation
   - strict loss-control MBE
   - grouping rules
   - classification thresholds

2. Add uncertainty:
   - bootstrap confidence intervals
   - seed-level resampling
   - threshold sensitivity tables
   - permutation controls

3. Run a fresh holdout replication:
   - fixed configs
   - new seeds
   - no narrative tuning after launch
   - report whether qualitative classes replicate

4. Add ablations:
   - no controls
   - hyperparameters only
   - hyperparameters + architecture/task
   - hyperparameters + architecture/task + validation loss
   - within-suite and within-architecture analyses

5. Clean the metric taxonomy:
   - normalized-rank metrics
   - gradient/Fisher magnitude metrics
   - sharpness metrics
   - confidence/calibration metrics
   - feature metrics
   - distance/update metrics

6. Reproducibility:
   - exact commands to regenerate tables
   - raw CSV artifact list
   - environment file
   - checksums for key CSVs
   - one reproduction README

Nice-to-have:

- one additional image dataset or one additional text dataset
- one larger architecture probe if compute allows
- a compact public leaderboard table: metric family vs raw, MBE, strict MBE, class

## 10. Next Milestone

Use the 680-model audit as the first complete evidence set. The next milestone should be:

> Draft the paper around the 680-model result, then run one locked holdout replication and bootstrap all reported correlations. If the holdout preserves the FIM_norm task-dependence/reversal story while random controls stay weak and several metrics survive, the work becomes credible enough to target a suitable venue.
