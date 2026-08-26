# Supporting Evidence

> **Evidence status:** This is an exploratory MBE v1 ledger preserved for
> provenance. It is not submission-grade confirmatory evidence. The 680-row
> pool contains repeated configurations, and its legacy text models lack a
> causal attention mask and permit label leakage. Text and mixed-pool results
> are retained to document the failure, not to support language-model claims.
> New evidence must follow the [MBE 2.0 research program](../MBE_2_RESEARCH_PROGRAM.md).

> **Corrected evidence update (2026-07-26):** The current MBE 2.0 evidence is
> indexed in [docs/EVIDENCE_INDEX.md](../EVIDENCE_INDEX.md). A corrected
> causal-LM pipeline has passed its implementation gate. The first 100-run
> causal-text factorial is public but receives no metric verdict because it has
> 20 configuration units and an invalid configuration-level random control; a
> separately reported 180-run replication was active at that date. These
> results do not alter the historical status of this v1 ledger.

> **Calibration update (2026-07-29):** The 180-run replication, expanded
> inference stress, observed-design power study, degrees 1-6 nuisance
> ablation, and paired refit-draw convergence are complete. The frozen
> two-family rule abstained on the real metrics, but known-truth simulation
> found that its mandatory interaction-family veto has only 1.0%-4.6% power
> for a large effect at 36 configurations. That abstention is not a substantive
> metric null. Current evidence and reproduction links are summarized in
> [docs/EVIDENCE_INDEX.md](../EVIDENCE_INDEX.md).

This file records the evidence accumulated so far for Marginal Baseline
Evaluation (MBE) and the FIM_norm case study.

Definitions used below:

- `washout`: a metric had meaningful raw association but its MBE partial
  correlation collapsed below the washout threshold.
- `sign-inversion` / `reverse-inversion`: the controlled association flipped
  direction. These are not counted as washout, but they are stronger audit
  warnings.
- `hidden-after-control`: weak raw association became meaningful only after
  controls. This can indicate masking by baseline/design variables.
- `survives`: the metric retained meaningful association after MBE controls.

Within these exploratory runs, MBE does not kill all
metrics. It weakens, washes out, or inverts some fragile proxies while leaving
several validation, confidence/logit, gradient/Fisher magnitude, and
task-proximal metrics intact.

## 1. Normal FIM_norm Validation Before MBE

Source notes:

- `experiments/06_independent_audit/fim_norm_normal_eval.md`
- `experiments/06_independent_audit/fim_norm_metric_evidence.md`

These are conventional metric-evaluation checks, not MBE checks.

| Run / evidence | Main result | What it suggests | Washout metrics |
|---|---|---|---|
| MLP dual acid test | Label-noise probe: FIM_norm vs accuracy `rho=-0.770`, `p=3.41e-03`; data-capacity probe: `rho=-0.937`, `p=6.99e-06` | FIM_norm showed strong associations under conventional metric validation; lower FIM_norm tracked better generalization across two controlled stress directions. | Not applicable: no MBE controls in this run |
| Condition means | FIM_norm increased monotonically with label noise and decreased with more training data, while accuracy moved in the expected opposite direction | The metric had visually clean and statistically plausible behavior before MBE. | Not applicable |
| CNN + BatchNorm transfer | Noise probe `rho=-0.956`, n-train probe `rho=-0.837` | FIM_norm transferred beyond MLPs and survived BatchNorm settings under ordinary evaluation. | Not applicable |
| Transformer + LayerNorm transfer | Noise probe had correct sign but was not significant; n-train probe `rho=-0.951` | FIM_norm had partial architecture-transfer evidence, with weaker noise evidence on transformer. | Not applicable |
| Baseline metric comparison | FIM_norm, trace_norm, stable_rank_n, grad_norm, and weight_norm all looked strong in raw tests | FIM_norm was not obviously bad; it belonged to a plausible gradient-energy family. | Not applicable |
| Bootstrap checks | MLP and CNN FIM_norm CIs often excluded zero | The raw signal was not just a single point-estimate artifact. | Not applicable |

Interpretation:

FIM_norm passed enough conventional checks to motivate further investigation.
That makes it a useful case study: MBE stress-tests a metric that appeared
credible under conventional validation rather than an intentionally weak one.

## 2. Early Loss-Controlled Stress Test

Source:

- `experiments/06_independent_audit/fim_norm_normal_eval.md`

| Run / evidence | Main result | What it suggests | Washout metrics |
|---|---|---|---|
| Epoch-20 FIM_norm vs validation-loss control | Raw FIM_norm vs accuracy `rho=-0.514`; validation loss vs accuracy `rho=-0.924`; FIM_norm controlling validation loss `partial=+0.216`, `p=0.25`; validation loss controlling FIM_norm remained strong at `partial=-0.900`, `p=1.3e-11` | Much of FIM_norm's apparent signal was already explained by validation loss. | FIM_norm |

Interpretation:

This was the first clean hint that the FIM_norm signal might be derivative of
simpler training-state quantities.

## 3. Independent Artifact Audit

Source:

- `experiments/06_independent_audit/artifact_audit_report.md`

These audits recomputed rank-based correlations directly from saved CSV
artifacts.

| Run | Rows | Main result | What it suggests | Washout metrics |
|---|---:|---|---|---|
| `mlp_large_grid_v3_asam` | 1000 | FIM_norm `-0.815 -> +0.033`; weight_norm `+0.814 -> -0.034`; sam_sharpness and grad_norm inverted | In a large heterogeneous MLP grid, FIM_norm and weight norm collapsed after controls; several sharpness/gradient quantities were control-sensitive. | FIM_norm, weight_norm |
| `mlp_unified_grid_current` | 1000 | FIM_norm `-0.803 -> +0.056`; weight_norm `+0.808 -> -0.057`; sam_sharpness and grad_norm inverted | The FIM_norm washout replicated in the newer unified MLP grid. | FIM_norm, weight_norm |
| `cnn_kaggle_local_50` | 50 | FIM_norm `+0.376 -> +0.445`; val_loss `-0.892 -> -0.513`; most metrics survived | Tiny local CPU CNN run was useful for plumbing, but too small/undertrained to support paper claims. It did not reproduce FIM_norm washout. | None in the audit report |
| `cnn_kaggle_download_250` | 250 | FIM_norm `-0.051 -> -0.069`; val_loss `-0.095 -> -0.049`; most raw correlations were already weak | In a larger CIFAR-10 CNN grid, the metrics showed little robust signal; FIM_norm was weak and washed out. | asam_sharpness, weight_norm, FIM_norm, val_loss |

Interpretation:

The large MLP grids strongly support the "normal metric signal can wash out
under controls" story. The 50-row CNN run should be treated only as an
engineering smoke test. The 250-row CIFAR run suggests that naive CNN-grid
metric correlations can be noisy or weak unless the design is scaled and
controlled carefully.

## 4. ResNet CPU Smoke Tests

Sources:

- `experiments/06_independent_audit/resnet_fim_mbe_quick_report.md`
- `experiments/06_independent_audit/resnet_fim_mbe_standard_report.md`

| Run | Rows | Main result | What it suggests | Washout metrics |
|---|---:|---|---|---|
| ResNet quick smoke | 8 | FIM_norm `-0.703 -> -0.858`; val_loss `-0.788 -> -0.880`; train_acc `+0.795 -> +0.889` | Plumbing worked; all reported metrics retained or strengthened signal, but n=8 is not evidence-scale. | None |
| ResNet standard smoke | 18 | FIM_norm `-0.146 -> +0.418` with lr+wd controls and `+0.368` with lr+wd+seed; val_loss, train_acc, train_loss survived | The run shows FIM_norm can be unstable even in ResNet plumbing, but this is still too small for a publication claim. | None by threshold table; FIM_norm shows sign instability from weak raw signal |

Interpretation:

These runs validate code paths and show why larger image-scale runs were
needed. They should not be used as central claims.

## 5. Kaggle-Scale Runs

Sources:

- mixed image+text early-pool audit summary
- image confirmation audit summary
- text confirmation audit summary
- image combined audit summary
- image combined strict loss-control summary
- text combined audit summary
- text combined strict loss-control summary
- full confirmed 680-model audit summary
- full confirmed 680-model strict loss-control summary
- locked text holdout audit summary
- locked image time-boxed holdout audit summary

The default large-scale MBE controls are:

```text
lr, wd, dropout, optimizer, arch, task, seed
```

Strict audits additionally control:

```text
val_loss
```

### Pooled Run Summary

| Run | n | FIM_norm result | Class mix in pooled audit | Washout metrics |
|---|---:|---|---|---|
| Large-scale v2 mixed image+text early pool | 240 | `+0.309 -> -0.200`, weak-or-mixed | 15 survives, 14 weak/mixed, 9 washout, 3 hidden-after-control | grad_noise_scale, per_sample_grad_norm_std, sam_sharpness, hessian_trace_hutchinson, weight_l1, weight_rms, distance_from_init_l2, update_to_weight_ratio, feature_erank |
| Image confirmation only | 320 | `-0.651 -> -0.199`, weak-or-mixed | 18 survives, 18 weak/mixed, 2 washout, 1 hidden-after-control | relative_distance_from_init, update_to_weight_ratio |
| Text confirmation only | 120 | `-0.270 -> -0.015`, washout | 14 survives, 13 weak/mixed, 10 washout, 1 hidden-after-control, 1 reverse-inversion | FIM_norm, fim_erank, fisher_entropy, weight_l2, weight_rms, margin_mean, brier, ece, logit_norm_mean, metric_batch_loss |
| Image combined default | 480 | `-0.662 -> -0.218`, survives | 21 survives, 16 weak/mixed, 3 washout, 1 hidden-after-control | hessian_trace_hutchinson, relative_distance_from_init, update_to_weight_ratio |
| Image combined strict + val_loss | 480 | `-0.662 -> -0.383`, survives | 29 survives, 4 weak/mixed, 4 hidden-after-control, 2 sign-inversion, 1 washout | feature_cosine_mean |
| Text combined default | 200 | `-0.291 -> +0.014`, washout | 15 survives, 12 washout, 10 weak/mixed, 1 hidden-after-control, 1 reverse-inversion | FIM_norm, fim_erank, fisher_entropy, weight_l2, weight_rms, confidence_mean, margin_mean, brier, ece, logit_norm_mean, metric_batch_acc, metric_batch_loss |
| Text combined strict + val_loss | 200 | `-0.291 -> +0.188`, weak-or-mixed | 15 weak/mixed, 15 survives, 7 washout, 1 reverse-inversion | fisher_condition, confidence_mean, entropy_mean, margin_mean, logit_norm_mean, train_loss, train_acc |
| Current + confirm text default | 360 | `+0.463 -> -0.107`, weak-or-mixed | 20 survives, 12 weak/mixed, 8 washout, 1 hidden-after-control | fisher_stable_rank, grad_noise_scale, grad_linf, hessian_trace_hutchinson, weight_l1, update_to_weight_ratio, metric_batch_acc, feature_norm_mean |
| Current + confirm text strict + val_loss | 360 | `+0.463 -> -0.040`, washout | 18 survives, 15 weak/mixed, 6 washout, 1 hidden-after-control | FIM_norm, fisher_stable_rank, grad_noise_scale, weight_l1, weight_linf, feature_norm_mean |
| Full confirmed default | 680 | `+0.225 -> -0.203`, reverse-inversion | 19 survives, 12 weak/mixed, 7 washout, 2 hidden-after-control, 1 reverse-inversion | hessian_trace_hutchinson, weight_l2, weight_l1, distance_from_init_l2, update_to_weight_ratio, feature_erank, feature_norm_mean |
| Full confirmed strict + val_loss | 680 | `+0.225 -> -0.300`, reverse-inversion | 26 survives, 6 weak/mixed, 4 washout, 3 hidden-after-control, 1 reverse-inversion | grad_noise_scale, asam_sharpness, feature_norm_mean, feature_cosine_mean |
| Locked text holdout default | 100 | `-0.534 -> -0.224`, survives | 20 survives, 13 washout, 10 weak/mixed, 2 hidden-after-control, 1 reverse-inversion | fim_unit_erank, fim_unit_norm, grad_loss_logcorr, per_sample_grad_norm_std, weight_l2, weight_rms, distance_from_init_l2, relative_distance_from_init, update_to_weight_ratio, brier, metric_batch_acc, metric_batch_loss, train_acc |
| Locked image time-boxed holdout default | 80 | `-0.699 -> -0.229`, survives | 27 survives, 16 weak/mixed, 2 washout, 2 sign-inversion, 1 hidden-after-control | distance_from_init_l2, relative_distance_from_init |

### FIM_norm Across the Main Confirmed Pool

| Audit | n | Raw rho | MBE partial rho | Class |
|---|---:|---:|---:|---|
| Image only, default controls | 480 | -0.662 | -0.218 | survives |
| Image only, strict + val_loss | 480 | -0.662 | -0.383 | survives |
| Text only, default controls | 200 | -0.291 | +0.014 | washout |
| Text only, strict + val_loss | 200 | -0.291 | +0.188 | weak-or-mixed |
| Full 680, default controls | 680 | +0.225 | -0.203 | reverse-inversion |
| Full 680, strict + val_loss | 680 | +0.225 | -0.300 | reverse-inversion |
| Locked text holdout, default controls | 100 | -0.534 | -0.224 | survives |
| Locked image time-boxed holdout, default controls | 80 | -0.699 | -0.229 | survives |

Interpretation:

FIM_norm is not simply bad everywhere. It survives in image-only pooled audits,
survives the locked 80-run image holdout, washed out in the earlier text-only
combined audit, survives in the locked 100-run text holdout, and reverses in the
full image+text pool. That is a stronger story than "FIM_norm fails": the
result is task-dependent, pooling-sensitive, and protocol-sensitive, exactly
the kind of issue MBE is meant to surface.

## 6. Metrics That Wash Out Most Often

Across the major MBE artifacts, the metrics most often appearing in washout
lists are:

- FIM_norm / fim_erank / fisher_entropy in text or mixed strict settings.
- weight norms: weight_l1, weight_l2, weight_rms, weight_linf.
- distance/update proxies: distance_from_init_l2, relative_distance_from_init,
  update_to_weight_ratio.
- feature metrics: feature_erank, feature_norm_mean, feature_cosine_mean.
- some sharpness and noise-scale metrics: sam_sharpness, asam_sharpness,
  grad_noise_scale, hessian_trace_hutchinson.
- some task-proximal metrics in text strict audits: confidence_mean,
  margin_mean, logit_norm_mean, metric_batch_acc, metric_batch_loss.

This does not mean each metric is universally useless. The repeated pattern is
that several metric families depend heavily on task, architecture, pooling, and
baseline controls.

## 7. Metrics That Repeatedly Survive

The legacy 680-row strict pilot is exploratory evidence that MBE can behave
selectively. In that run, many metrics survived despite strong controls:

- fisher_trace
- fisher_spectral
- fisher_condition
- grad_norm
- grad_l1
- grad_linf
- grad_mean_abs
- per_sample_grad_norm_mean
- per_sample_grad_norm_std
- hessian_trace_hutchinson
- hessian_top_eig_power
- weight_linf
- weight_rms
- distance_from_init_l2
- relative_distance_from_init
- update_to_weight_ratio
- train_loss
- train_acc
- confidence_mean
- entropy_mean
- margin_mean
- brier
- ece
- logit_norm_mean
- metric_batch_acc
- metric_batch_loss

Interpretation:

This is important for the paper. MBE does not uniformly suppress metric signal.
It can preserve strong signals while flagging fragile ones.

## 8. Overall Narrative Supported So Far

The evidence supports this narrative:

1. FIM_norm met several conventional metric-validation checks.
2. Loss-controlled and hyperparameter-controlled audits substantially weakened
   its apparent independent signal.
3. Larger Kaggle-scale audits show that FIM_norm behavior is task-dependent:
   image-only results can survive, text-only results can wash out, and pooled
   image+text results can reverse.
4. MBE also flags other fragile metrics, especially feature-rank, weight-norm,
   distance/update, and some sharpness/noise-scale proxies.
5. MBE preserves many metrics, especially validation/task-proximal,
   confidence/logit, and several gradient/Fisher magnitude metrics.

The strongest current claim is:

> Raw pooled correlation is not enough to validate a generalization metric.
> Marginal Baseline Evaluation exposes whether the metric has signal beyond
> ordinary training baselines and design variables.

## 9. Evidence Gaps Before Submission

The current evidence is strong enough to guide the paper direction, but not yet
enough to freeze a submission. Remaining needs:

- bootstrap confidence intervals for all headline correlations;
- a locked holdout replication with no post-hoc narrative tuning;
- threshold-sensitivity tables for washout/survival labels;
- ablations over control sets: none, hyperparameters only, hyperparameters plus
  architecture/task, and strict + validation loss;
- a cleaned metric taxonomy table;
- a reproducibility page with commands and artifact hashes.

## 10. No-Compute Addendum

After the initial evidence ledger, a CPU-only uncertainty pass was added:

- script: no-compute uncertainty analysis
- report: no-compute uncertainty summary
- bootstrap resamples: 200
- bootstrap unit: row/model run

Headline checks:

- full 680 default FIM_norm: raw `+0.225 [+0.136, +0.314]`, MBE partial `-0.203 [-0.267, -0.117]`, reverse-inversion;
- full 680 strict FIM_norm: raw `+0.225 [+0.138, +0.296]`, MBE partial `-0.300 [-0.389, -0.217]`, reverse-inversion;
- full 680 default random metric: raw and partial CIs overlap zero, weak-or-mixed;
- full 680 strict confidence_mean: raw and partial CIs stay positive, survives.

This strengthens the current narrative without new training compute: the
headline FIM_norm pooled reversal is not just a point-estimate artifact, while
the negative control remains weak and a positive confidence metric survives.
