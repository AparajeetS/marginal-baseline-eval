# CEI v2 — Complete Findings & Investigation Record

**Status: CONCLUDED (negative result).** Last updated 2026-05-23.

This is the master record of the CEI v2 investigation: the question, the search,
every metric tried, what passed initial validation, the critical review, the two
decisive tests that closed the metric, the honest interpretation, the reusable
methodology, and recommendations. `theory.md` holds the metric definition;
`RESULTS.md` holds the test-by-test data tables; this file is the narrative
synthesis that ties them together.

---

## 0. One-paragraph verdict

We sought a parameter-space "structural constraint" metric to predict neural
network generalization, motivated by the Structural Homeostasis Hypothesis (SHH)
and by CEI v1's failure on BatchNorm. We found **FIM_norm** = erank(GGᵀ/N)/N,
the normalized effective rank of the per-sample gradient second moment. It passes
a dual acid test (label-noise + capacity probes) across MLP, CNN+BatchNorm, and
Transformer+LayerNorm — fixing v1's BatchNorm failure. **But on rigorous review it
does not beat the loss at any checkpoint.** At ep20 it adds nothing beyond the
loss you already measure (partial r=+0.22, p=0.25), while loss retains r=−0.90
after controlling for FIM. At initialization (where loss is structurally flat) it
is also null and sign-inconsistent. The honest conclusion: gradient effective rank
tracks generalization but is dominated by loss everywhere. The metric is closed.
The durable assets are (1) a clean citable negative result and (2) the
metric-validation methodology that produced it in hours.

---

## 1. The question and its lineage

**Origin (software SHH).** Five large open-source systems (NumPy, Pandas, Django,
FastAPI, Airflow) maintain bounded coupling E(t)/N(t) as they grow — "structural
homeostasis." The conjecture: an analogous bounded-interaction regularity governs
generalizing neural networks.

**CEI v1 (`../formalization/`).** Operationalized this as
`CEI_l = erank(Σ_activation_l)/n_l`, the normalized effective rank of each layer's
activation second moment, averaged over layers. Hypothesis (NN-SHH): CEI decreases
monotonically in generalizing nets, not in overfitting ones. Connected to neural
collapse (Papyan 2020). v1 listed three falsification conditions, including the
crucial one: *CEI must predict beyond sharpness.*

**Why v1 failed.** (a) BatchNorm renormalizes activations, so activation-space
erank flips direction on CNNs. (b) Activation rank conflates the data's intrinsic
geometry with the network's learned structure. The fix had to move out of
activation space.

**The v2 move.** From **activation space (forward)** to **parameter/gradient
space (backward)**. Normalization layers act on activations, so a gradient-space
metric is immune to them. This single insight is correct and is the one genuine
technical win of the whole program.

---

## 2. The metric

    g_i      = ∇_θ L(x_i, y_i; θ)              per-sample gradient (dim d)
    G        = [g_1; …; g_N]                   N × d
    S_dual   = G Gᵀ / N                         N × N  (same nonzero spectrum as the
                                                d × d gradient 2nd moment)
    erank(M) = exp(−Σ_k p_k log p_k),  p_k = σ_k/Σσ   (entropy of normalized spectrum)
    FIM_norm = erank(S_dual) / N  ∈ (1/N, 1]

Low FIM_norm = gradient energy concentrated in few directions; high = scattered.
The dual identity erank(GGᵀ)=erank(GᵀG) makes it tractable for any d.

**Terminology caution (recorded permanently):** S_dual is the *empirical* Fisher
(uses observed labels), NOT the true Fisher (which samples labels from the model).
Their spectra differ (Kunstner et al., NeurIPS 2019). We therefore claim NO
Fisher-Rao / natural-gradient / PAC-Bayes guarantees. The object is literally the
second moment of the per-sample gradient distribution — a gradient-diversity
measure.

---

## 3. The search — every candidate and why it died

| # | Candidate | Direction | Failure mode | Verdict |
|---|-----------|-----------|--------------|---------|
| 1 | abs weight erank | correct | dynamic range 0.0004 — frozen, no resolution | dead |
| 2 | ΔW (weight-change) erank | correct | confounded by n_train | dead |
| 3 | layer alignment | weak (p=0.29) | indistinguishable from noise | dead |
| 4 | gradient rank (raw) | correct | confounded by L2 reg | dead |
| 5 | gradient coherence (mean cosine) | **FLIPS** | +0.84 noise / −0.86 n_train — sign flip | dead |
| 6 | **FIM_norm** | correct | passes acid test… then fails vs loss | **closed (this doc)** |

The coherence sign-flip (candidate 5) is instructive: it conflates data richness
(more data → lower coherence) with label quality (noise → lower coherence), which
push test accuracy in opposite directions. FIM_norm's normalization survived that
specific trap — which is why it looked promising — but the deeper loss confound
was never checked until the review.

---

## 4. What passed initial validation (Tests 1–9)

Full tables in `RESULTS.md`. Summary:

- **Test 1 — MLP dual acid test:** noise rho=−0.770 (p=3.4e-3), n_train rho=−0.937
  (p=7.0e-6). PASSES.
- **Test 2 — vs SAM sharpness (6×3):** FIM@ep20 rho=−0.629 (p=5.2e-3) significant;
  sharpness@ep20 rho=−0.440 (p=0.068) not. Looked like FIM was the better early
  predictor and complementary to sharpness. *(NOTE: loss was never the control here
  — Test 11 later showed this conclusion is unsafe.)*
- **Test 3 — CNN + BatchNorm:** noise rho=−0.956, n_train rho=−0.837. PASSES — the
  exact v1 failure case, fixed.
- **Test 4 — stability:** N_FIM=100 gives CV<10% across conditions.
- **Test 5 — early stopping:** FIM is NOT a reliable automatic stopping criterion.
- **Test 6 — Transformer + LayerNorm:** n_train rho=−0.951 (p=2.0e-6); noise
  rho=−0.476 (p=0.118, n.s.). PARTIAL. Bonus: SAM sharpness is near-zero and
  catastrophically noisy on pre-LN transformers — FIM still discriminates capacity.
- **Test 7 — baselines:** fim_norm, trace_norm, stable_rank_n, grad_norm all pass
  the acid test on digits; spectral_n fails significance; weight_norm passes with
  WRONG sign (n_train confound). FIM is not uniquely the only passing metric.
- **Test 8 — bootstrap 95% CIs (10k):** CNN noise solid; MLP/n_train solid; MLP
  noise marginal (CI upper +0.007). 5/8 rows significant.
- **Test 9 — ResNet-18/CIFAR-10:** after fixing a data-partition bug (below),
  direction correct (A FIM=0.264/te=0.343 > B FIM=0.135/te=0.577), rho=−0.400
  (n.s.). Revealed **memorization collapse** (below).

At the end of this phase the metric looked like a qualified success. It was not.

---

## 5. The critical review — assumptions rechecked

Six issues surfaced; three were fixed and re-tested (Test 10), two became the
decisive tests (11, 12), one is a permanent caveat.

1. **Empirical Fisher ≠ true Fisher** → reframed terminology; dropped borrowed
   theory. Permanent caveat.
2. **Data-partition inconsistency (BUG).** MLP/CNN/Transformer computed FIM on
   TRAINING data; CIFAR mistakenly used a clean held-out EVAL set. Since the noise
   mechanism lives only in the training labels, eval-set FIM measured the wrong
   thing and produced a wrong-direction CIFAR result. Fixed → direction corrected.
   Codified as Standard 1 (always training data).
3. **N-normalization confound.** n_train probe used N=40 for n=40 but N=100 for
   n≥200; erank/N shrinks with N once N exceeds the true rank. Fixed by holding
   N=40 for all (Test 10) → rho still −0.924. Confound was not the driver. RESOLVED.
4. **Whole-network only** → added per-layer FIM (Test 10): signal is UNIFORM across
   all 4 layers (no v1-style localization). Robust but not localized.
5. **Layer-scale weighting** → mitigated by #4 (every layer carries it).
6. **LOSS BASELINE NEVER TESTED** → became Test 11. This was the fatal omission.

### Test 10 results (5 seeds, fixed-N, training-data FIM)
- Fixed-N n_train rho=−0.924 (confound resolved).
- **FIM is largely a loss proxy:** fim_raw vs loss are near-identical predictors
  (n_train −0.924 vs −0.922). Partial fim|loss significant on n_train (p=0.018),
  marginal on noise (p=0.085).
- **Signal is MAGNITUDE-driven, not direction-driven:** unit-normalizing the
  gradients destroys it (n_train rho flips to +0.374). The working signal is the
  concentration of gradient *energy* (high-loss/hard samples dominate), NOT the
  intrinsic dimensionality of gradient *directions*. This reframes the metric and
  explains why it tracks loss.

---

## 6. The decisive tests — the metric is closed

### Test 11 — does FIM@ep20 beat loss@ep20 at predicting FINAL test accuracy?
6 conditions × 5 seeds, decoupling early loss from final generalization.
- Raw early predictors: val_loss@20 rho=−0.924; fim_eval@20 rho=−0.514. Loss is far
  stronger alone.
- **Partial FIM vs final_te | loss: ALL fail.** Best = fim_eval|val_loss r=+0.216
  (wrong sign), p=0.25. FIM adds nothing beyond loss.
- **Reverse asymmetry:** loss vs final_te | FIM keeps r=−0.90 (p=1.3e-11). The
  dependence is one-directional — FIM is a weaker shadow of loss.
- **Why:** label noise raises val_loss@20 immediately (1.61→1.81→1.94), so loss
  already encodes the damage. There was never a hidden signal for FIM to reveal.

### Test 12 — FIM@init (loss is structurally flat: ~log 10 ≈ 2.30 for all)
Any signal here would be beyond-loss by construction.
- TEST A (across conditions): rho=−0.305, p=0.10 — right direction, not significant.
- TEST B (lucky-init, fixed data, 20 inits): rho=+0.377, p=0.10 — WRONG sign, n.s.
- The two disagree in sign → no coherent signal. loss@init range [2.34, 2.58]
  confirms the setup (loss can't discriminate), yet FIM still found nothing.

**Combined (Tests 1–12): gradient effective rank is dominated by loss at init,
mid-training, and convergence. Loss is free, already computed, and strictly better.**

---

## 7. What FIM_norm actually measures (final honest interpretation)

NOT the intrinsic dimensionality of a learned representation (that was the SHH-
flavored hope, falsified by the unit-norm test). It is the **effective
concentration of per-sample gradient ENERGY** — how many samples carry significant
gradient magnitude — which is a participation-ratio statistic of the loss
distribution. That is why it correlates with loss and why removing magnitude
(unit-norm) destroys it.

**Memorization collapse:** in the over-parameterized regime, once a model fully
memorizes the training set, training loss→0, gradients→0, and erank collapses
(CIFAR condition C: FIM spikes at ep5 then collapses to ~0.02 at ep14, tr=0.996).
The noise signal lives in the trajectory, not the converged value — a direct
consequence of the magnitude-driven nature.

---

## 8. The reusable asset — the validation methodology

The transferable IP is NOT the metric; it is the protocol that killed it cleanly:

1. **Dual acid test** — a candidate must show consistent direction AND significance
   on TWO orthogonal probes (label-noise at fixed capacity; capacity at fixed
   noise). Kills sign-flippers (coherence) immediately.
2. **Loss-baseline partial correlation** — the non-negotiable control. Does the
   candidate predict generalization BEYOND the loss already in hand? Most proposed
   metrics in the literature never report this.
3. **Bootstrap CIs** — honest uncertainty on small-n rank correlations.
4. **Init probe** — the clean room where loss is structurally uninformative; the
   last court of appeal for any "beyond-loss" claim.
5. **Cross-architecture harness** — MLP / CNN+BN / Transformer+LN / ResNet, so
   normalization-layer artifacts surface (this is what exposed v1).

This protocol applied to FIM_norm reached a definitive answer in hours of compute.
That speed-to-truth is the defensible capability.

---

## 9. Conclusions & recommendations

**Scientific conclusion.** Gradient effective rank correlates with generalization
but provides no predictive value beyond loss at any training checkpoint, across
four architectures. A clean, robust negative result.

**Do NOT.** Build an early-stopping / training-efficiency product on FIM_norm — a
practitioner uses validation loss, which is free and strictly better.

**DO.**
1. Write the negative-results paper (TMLR / NeurIPS workshop). The twelve tests are
   assembled; the narrative is this document. Honest negatives from a clean
   methodology get cited and save others the same path. v1's own protocol
   pre-registered this as a valid outcome.
2. Repackage the validation harness (§8) as the actual product/IP: "does your
   proposed training metric beat loss?" — demonstrated by killing our own metric.
3. Optional: re-run the loss-control on Test 2's "beyond sharpness" claim before
   citing it anywhere — it likely does not survive the loss baseline either.

**One technical fact worth carrying forward:** moving a metric from activation
space to parameter space removes BatchNorm/LayerNorm contamination. Narrow, but
real, and reusable for future metric work.

---

## 10. File index

Core docs:
- `FINDINGS.md`        — this master record
- `theory.md`          — metric definition, evolution, methodological standards
- `RESULTS.md`         — test-by-test data tables (Tests 1–12)

Validated-phase scripts & outputs:
- `fim_normalized.py`        / `fim_norm_summary.txt`      — Test 1 (MLP acid test)
- `fim_full_study.py`                                       — Test 2 (vs SAM, 6×3)
- `fim_cnn_test.py`          / `fim_cnn_summary.txt`        — Test 3 (CNN+BatchNorm)
- `fim_stability.py`                                        — Test 4 (N_FIM stability)
- `fim_early_stop.py`                                       — Test 5 (stopping: negative)
- `fim_transformer_test.py`  / `fim_transformer_summary.txt`— Test 6 (Transformer)
- `fim_baselines.py`         / `fim_baselines_summary.txt`  — Test 7 (6 metrics)
- `fim_bootstrap_ci.py`      / `fim_bootstrap_ci.txt`       — Test 8 (bootstrap CIs)
- `fim_cifar_test.py`        / `fim_cifar_summary.txt`      — Test 9 (ResNet-18/CIFAR)

Review-phase scripts & outputs (the decisive ones):
- `fim_review_followup.py`   / `fim_review_followup.txt`    — Test 10 (fixed-N, loss
                                                              proxy, per-layer, unit-norm)
- `fim_early_predictor.py`   / `fim_early_predictor.txt`    — Test 11 (DECISIVE: beats
                                                              loss@ep20? — no)
- `fim_init_test.py`         / `fim_init_test.txt`          — Test 12 (FIM@init — null)

Core utilities:
- `sci_tracker.py`           — effective_rank + helpers

Earlier exploration (the search, candidates 1–5): `probe_*.py`, `config_cei_*.py`,
`sample_cei_*.py`, `cei_blackbox_*.py`, `noise_acid_test.py`, `pilot_v2*.py`.

v1 (DO NOT MODIFY): `../formalization/` — `CEI_NN_formal.tex`, `cei_tracker.py`,
`measurement_protocol.md`, `experiment/`.
