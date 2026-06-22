# CEI v2 — FIM_norm: Full Experimental Results

> ## HEADLINE VERDICT (after full review — Tests 11 & 12 are decisive)
> FIM_norm correlates with generalization and is BatchNorm-immune, but it does
> NOT beat the loss at ANY checkpoint:
>   - @ep20: adds nothing beyond loss (partial r=+0.22, p=0.25); reverse asymmetry
>     has loss retaining r=-0.90 after controlling for FIM (Test 11).
>   - @init (the one regime where loss is structurally flat): also null — TEST A
>     rho=-0.305 p=0.10 (n.s.), TEST B rho=+0.377 p=0.10 (n.s., wrong sign). The
>     two sub-tests even disagree in sign, confirming no coherent signal (Test 12).
> Conclusion: gradient effective rank is not a useful generalization predictor
> beyond loss. Honest scope: a NEGATIVE-RESULTS / measurement paper. The reusable
> asset is the validation methodology (dual acid test + partial-vs-loss + bootstrap),
> not the metric.

## Definition

    FIM_norm = erank(F_dual) / N
    
    where F_dual = G G^T / N,  G[i] = per-sample gradient vector,
    N = number of samples used.
    
    Range: (1/N, 1].  Lower = more structurally constrained = better gen.

---

## Test 1 — Dual Acid Test (numpy MLP, tanh, no BatchNorm)

### Experiment A: Label noise, n=400 FIXED, epochs=200 FIXED

| noise | FIM_norm | test_acc |
|-------|----------|----------|
|   0%  |  0.282   |  0.887   |
|  15%  |  0.353   |  0.883   |
|  30%  |  0.472   |  0.872   |
|  50%  |  0.615   |  0.805   |

Spearman rho = -0.770, p = 3.41e-03

### Experiment B: n_train, noise=0 FIXED, epochs=200 FIXED

| n_train | FIM_norm | test_acc |
|---------|----------|----------|
|   40    |  0.642   |  0.585   |
|  200    |  0.387   |  0.830   |
|  400    |  0.282   |  0.887   |
|  800    |  0.143   |  0.918   |

Spearman rho = -0.937, p = 6.99e-06

**PASSES dual acid test. Both significant. Consistent direction.**

---

## Test 2 — Full Study vs SAM Sharpness (6 conditions x 3 seeds)

| Metric | rho (final) | p (final) | rho (@ep20) | p (@ep20) |
|--------|-------------|-----------|-------------|-----------|
| FIM_norm | -0.787 | 1.06e-04 | -0.629 | 5.20e-03 |
| Sharpness | -0.799 | 7.09e-05 | -0.440 | 0.068 |

**FIM_norm@ep20 is significant; Sharpness@ep20 is NOT.**
FIM_norm is the stronger EARLY predictor.

Partial R² (unique variance explained):

| Metric | Partial R² @final | Partial R² @ep20 |
|--------|-------------------|------------------|
| FIM_norm \| sharpness | +0.009 | **+0.031** |
| Sharpness \| FIM_norm | +0.136 | +0.322 |

FIM_norm adds unique information at ep20 (>0.03 threshold).
Sharpness adds substantial unique information at both timepoints.
Metrics are COMPLEMENTARY, not redundant.

Key condition: F (30% noise, n=400):
- Sharpness = 0.011 (same as clean B/C/D — flat minimum found)
- FIM_norm  = 0.456 (elevated vs clean 0.27 — detects label noise)
- FIM_norm sees training data quality; sharpness does not.

---

## Test 3 — CNN + BatchNorm (PyTorch, small CNN on digits)

This was the exact failure mode of CEI v1.

### CNN Noise probe (n=400 fixed):

| noise | FIM_norm | test_acc |
|-------|----------|----------|
|   0%  |  0.053   |  0.910   |
|  15%  |  0.096   |  0.833   |
|  30%  |  0.123   |  0.765   |
|  50%  |  0.126   |  0.638   |

Spearman rho = -0.956, p = 1.20e-06

### CNN n_train probe (noise=0):

| n_train | FIM_norm | test_acc |
|---------|----------|----------|
|    40   |  0.233   |  0.638   |
|   200   |  0.082   |  0.807   |
|   400   |  0.053   |  0.910   |
|   800   |  0.059   |  0.942   |

Spearman rho = -0.837, p = 6.93e-04

**PASSES dual acid test on CNN + BatchNorm.**
Architecture-agnostic claim confirmed.
CEI v1 failed here; FIM_norm does not.

---

## Test 4 — Sample-Count Stability (N_FIM sensitivity)

| N_FIM | CV (overfit) | CV (generalise) | CV (noisy) |
|-------|-------------|-----------------|------------|
|     5 | 9.7% | 26.6% | 20.0% |
|    10 | 9.3% | 22.3% | 10.3% |
|    20 | 4.0% | 25.4% |  8.3% |
|    50 | 0.0%* | 13.3% |  8.1% |
|   100 | 0.0%* |  7.7% |  3.4% |
|   200 | 0.0%* |  5.5% |  2.8% |

*overfit model has n=40 training samples; N_FIM caps at 40, CV=0 by design.

Recommendation: **N_FIM = 100** for reliable estimates (CV < 10% all cases).
N_FIM = 50 acceptable when compute is limited.

---

## Test 5 — Early Stopping Utility

| Strategy | Condition A (n=40) | Condition B (n=400 clean) | Condition C (n=400, 30% noise) |
|---|---|---|---|
| Fixed 300 ep | te=0.610, ep=299 | te=0.870, ep=299 | te=0.826, ep=299 |
| Val loss patience | te=0.610, ep=299 | te=0.870, ep=299 | te=0.826, ep=299 |
| FIM_flat | te=0.180, ep=13 ❌ | te=0.870, ep=299 ✓ | te=0.786, ep=171 (~ok) |
| FIM_thresh | te=0.372, ep=66 ❌ | te=0.664, ep=28 ❌ | te=0.560, ep=27 ❌ |

**Verdict**: FIM_norm is NOT a reliable automatic stopping criterion in current
form. Simple threshold rules are too architecture/condition-sensitive.
FIM_norm AS A PREDICTOR (rho=-0.629 at ep20) is strong; AS A STOPPING SIGNAL
it needs more careful calibration (adaptive thresholds, per-run normalisation).

---

## Test 6 — Transformer + LayerNorm (small ViT-style on digits)

Architecture: 2-layer TransformerEncoder, d_model=64, nhead=4, pre-LN (norm_first=True),
8 patches of dim 8 from 64-dim input, CLS token -> FC(64->10). AdamW + wd=1e-4.

### Noise probe (n=400 fixed):

| noise | FIM_norm      | test_acc |
|-------|---------------|----------|
|   0%  | 0.312 +/-0.070  |  0.883   |
|  15%  | 0.316 +/-0.056  |  0.772   |
|  30%  | 0.350 +/-0.066  |  0.672   |
|  50%  | 0.441 +/-0.108  |  0.488   |

Spearman rho = -0.476, p = 1.18e-01  **NOT SIGNIFICANT**

### n_train probe (noise=0):

| n_train | FIM_norm      | test_acc |
|---------|---------------|----------|
|    40   | 0.537 +/-0.023  |  0.512   |
|   200   | 0.411 +/-0.022  |  0.787   |
|   400   | 0.312 +/-0.070  |  0.883   |
|   800   | 0.191 +/-0.054  |  0.927   |

Spearman rho = -0.951, p = 2.04e-06  **SIGNIFICANT**

**VERDICT: PARTIAL** — n_train probe passes strongly; noise probe correct direction
but not significant at alpha=0.05 (3 seeds only, high within-condition variance).

Interpretation: The transformer with AdamW+weight_decay resists label-noise
memorisation differently from the unregularised MLP. The n_train capacity effect
dominates regardless of architecture. The noise sensitivity depends on how well
the architecture/regulariser prevents memorisation — a smaller FIM_norm signal
is expected when the model cannot fully memorise noise labels.

Note: n_train rho=-0.951 is stronger than MLP (-0.937) and CNN (-0.837),
confirming FIM_norm is architecture-agnostic for the capacity axis.

---

## Test 7 — Baselines Comparison (6 metrics, same gradient sample)

All metrics computed from the same N=100 per-sample gradients. Dual acid test
(noise probe + n_train probe) on MLP/digits.

| Metric         | noise rho | n_train rho | Consistent | Both sig | Notes            |
|----------------|-----------|-------------|------------|----------|------------------|
| fim_norm       | -0.691    | -0.942      | YES        | YES      | PASS             |
| trace_norm     | -0.765    | -0.781      | YES        | YES      | PASS (magnitude) |
| stable_rank_n  | -0.688    | -0.893      | YES        | YES      | PASS             |
| spectral_n     | -0.222    | -0.308      | YES        | NO       | DIR only         |
| grad_norm      | -0.765    | -0.935      | YES        | YES      | PASS (magnitude) |
| weight_norm    | +0.702    | +0.939      | YES        | YES      | WRONG SIGN       |

Key findings:
- FIM_norm, trace_norm, stable_rank_n, and grad_norm all pass the dual acid test.
- spectral_n fails significance — the largest eigenvalue alone is noisy.
- weight_norm passes empirically but with POSITIVE rho (larger weights = better
  generalisation), which is an n_train confound (more data -> more updates ->
  larger weights). This direction is theory-inconsistent with L2 regularisation.
- FIM_norm advantage over trace_norm/grad_norm: captures the *distribution* of
  gradient directions (entropy), not just their magnitude. In the full study
  (Test 2), condition F (30% noise) showed that FIM_norm detects training data
  quality independently of sharpness while trace_norm/grad_norm may not (they
  are magnitude-only and thus conflate gradient energy with gradient structure).

Justification for erank choice: trace_norm = sum(sigma_i), grad_norm = sqrt(trace),
both are 0th-order statistics of the spectrum. FIM_norm = exp(H(sigma)) is a
1st-order statistic (entropy), measuring effective dimensionality. This is the
theoretically grounded quantity that directly operationalises the SHH structural
constraint concept.

---

## Test 8 — Bootstrap 95% CIs (10,000 resamples)

Design: noise probe (NOISE=[0,0.15,0.30,0.50] x 3 seeds = n=12),
n_train probe (NTRAIN=[40,200,400,800] x 3 seeds = n=12).
ep20 early-predictor test uses n_train probe conditions.

| Experiment + Metric       | rho    | 95% CI              | sig |
|---------------------------|--------|---------------------|-----|
| MLP noise    FIM_norm     | -0.643 | [-0.952, +0.007]    |  ~  |
| MLP noise    Sharpness    | -0.306 | [-0.789, +0.317]    |     |
| MLP n_train  FIM_norm     | -0.881 | [-0.993, -0.538]    |  *  |
| MLP n_train  Sharpness    | -0.937 | [-0.993, -0.727]    |  *  |
| MLP@ep20     FIM_norm     | -0.727 | [-0.971, -0.150]    |  *  |
| MLP@ep20     Sharpness    | -0.958 | [-1.000, -0.798]    |  *  |
| CNN noise    FIM_norm     | -0.956 | [-1.000, -0.780]    |  *  |
| CNN n_train  FIM_norm     | -0.837 | [-0.980, -0.413]    |  *  |

* = CI excludes zero. ~ = CI just includes zero (marginal).

Key observations:
- MLP noise FIM_norm: CI upper bound = +0.007 — borderline. Direction is
  consistent across all 10,000 resamples except the extreme tail. Not formally
  significant but practically near-certain direction.
- CNN noise FIM_norm: CI solidly excludes zero — the architecture-agnosticity
  claim is well-supported.
- MLP@ep20: Sharpness appears STRONGER than FIM_norm here (rho -0.958 vs -0.727).
  This is because the bootstrap uses ONLY n_train conditions (40/200/400/800),
  which are precisely the conditions where sharpness excels. The full 6-condition
  study (Test 2) — which adds heterogeneous conditions including 30% noise labels —
  is the correct test for early predictor comparison. In that design, sharpness@ep20
  is NOT significant (p=0.068) while FIM_norm@ep20 IS (p=5.20e-03). The bootstrap
  ep20 result should be interpreted as: both metrics work on pure capacity variation;
  FIM_norm additionally works on noise/quality variation.
- 5 of 8 rows are significant; 1 is marginal; 2 are not. The non-significant
  rows are both sharpness on the noise probe (as expected from full study).

---

## Test 9 — ResNet-18 / CIFAR-10 (the v1 benchmark)

3 conditions x 3 seeds. FIM on TRAINING data (corrected — see note). A/B at 15
epochs, C at 25 epochs. N_FIM=60 fixed for all (no N confound).

| Condition            | FIM_norm        | test_acc | expected |
|----------------------|-----------------|----------|----------|
| A n=500 no-reg       | 0.264 +/- 0.025 |  0.343   | high FIM |
| B n=5000 wd=1e-4     | 0.135 +/- 0.055 |  0.577   | low FIM  |
| C n=5000 30% noise   | 0.130 +/- 0.096 |  0.402   | high FIM |

Spearman rho(FIM, test_acc) = -0.400, p=0.286 (correct direction, NOT significant).

**Direction now correct (A>B), but condition C reveals a real limitation.**

### CRITICAL METHODOLOGICAL FIX (data partition)
The FIRST CIFAR run computed FIM on a held-out EVAL set (clean labels), unlike the
MLP/CNN/Transformer tests which use TRAINING data. That produced a WRONG-direction
result (B's FIM > A's). The noise mechanism only exists where corrupted labels live
(the training set), so eval-set FIM is measuring the wrong thing. Switching to
training data flipped A vs B to the correct ordering. Codified as Standard 1 in
theory.md: FIM is always computed on the training set.

### NEW FINDING: memorization collapses the signal
Condition C (30% noise) FIM trajectory (seed 42): 0.11 -> 0.39 -> 0.21 -> 0.02.
It SPIKES while fitting noise (ep5) then COLLAPSES to ~0.02 by ep14 when tr=0.996.
ResNet-18 has the capacity to FULLY memorize the noisy labels -> training loss -> 0
-> training gradients -> 0 -> erank collapses -> noise becomes undetectable at
convergence. The noise signal lives in the TRAJECTORY (the spike), not the final
value, in the over-parameterized regime.

Why the MLP didn't show this: the tanh MLP (n=400, limited capacity) does NOT fully
memorize 50% noise in 200 epochs, so its training gradients stay non-zero and
scattered -> sustained high FIM. The CIFAR ResNet (11M params) does fully memorize.

IMPLICATION: raw FIM_norm at convergence is entangled with training-loss magnitude.
The proposed fix (unit-normalized per-sample gradients, isolating direction from
magnitude) is tested in Test 10.

---

## Test 10 — Review follow-up (5 seeds, fixed-N, loss baseline, per-layer, unit-norm)

Addresses 4 review issues on the digits MLP. Training-data FIM, N_FIM=40 FIXED
for all conditions (so the n_train probe has no N-normalization confound).

| Metric    | noise rho (p)      | n_train rho (p)     |
|-----------|--------------------|---------------------|
| fim_raw   | -0.728 (2.7e-04)   | -0.924 (5.9e-09)    |
| fim_unit  | -0.534 (1.5e-02)   | **+0.374 (0.10)**   |
| loss      | -0.666 (1.3e-03)   | -0.922 (7.6e-09)    |

Partial correlation (FIM controlling for loss):
| Partial            | noise              | n_train            |
|--------------------|--------------------|--------------------|
| fim_raw  vs te|loss | -0.395 (p=0.085)   | -0.523 (p=0.018)   |
| fim_unit vs te|loss | +0.014 (p=0.95)    | -0.124 (p=0.60)    |

Per-layer fim_raw vs test_acc (all 4 weight matrices):
| Layer (size)   | noise rho | n_train rho |
|----------------|-----------|-------------|
| L0 (8192)      | -0.697    | -0.911      |
| L1 (8192)      | -0.743    | -0.911      |
| L2 (2048)      | -0.738    | -0.921      |
| L3 (320)       | -0.684    | -0.899      |

### Findings (these REVISE earlier claims — read carefully)

1. **Fixed-N confound RESOLVED (Issue 3).** With N=40 fixed for ALL n_train,
   fim_raw still gives rho=-0.924 (vs -0.937 with the confound). The n_train
   effect is REAL, not a normalization artifact. Good.

2. **FIM is substantially a LOSS PROXY (Issue 6 — important caveat).**
   fim_raw and loss are nearly identical predictors (n_train: -0.924 vs -0.922).
   Partial correlation shows fim_raw adds SIGNIFICANT info beyond loss on n_train
   (p=0.018) but only MARGINAL on noise (p=0.085). So FIM_norm is NOT purely a
   loss proxy, but loss explains most of its predictive power. The independent
   contribution is the *concentration/inequality* of per-sample gradient energy,
   beyond its mean. This MUST be disclosed; a reviewer will run this exact test.

3. **The signal is MAGNITUDE-driven, not direction-driven (key discovery).**
   Unit-normalizing per-sample gradients DESTROYS the signal: fim_unit n_train
   rho FLIPS to +0.374 (wrong sign, non-significant). The proposed unit-norm fix
   for the CIFAR memorization-collapse therefore FAILS — but it is a profound
   diagnostic: FIM_norm works *because* it captures magnitude-weighted gradient
   structure (high-loss/hard examples dominate the spectrum), NOT because of the
   intrinsic dimensionality of gradient *directions*. This reframes the metric:
   it measures the effective concentration of gradient ENERGY across samples,
   which is why it tracks loss so closely.

4. **Signal is UNIFORM across layers (Issue 4 — no localization).** All four
   layers carry nearly identical signal (n_train rho -0.90 to -0.92). Unlike v1's
   neural-collapse-propagating-backward hypothesis, there is no single carrier
   layer. The whole-network metric is robust and global; the concatenation is not
   dominated by one layer's artifact (mitigates Issue 5).

### Net assessment after review
FIM_norm passes the acid tests and is robust (fixed-N, per-layer, 5 seeds). But
the deep "intrinsic gradient dimensionality / structural constraint" story is
WEAKER than originally framed: the working signal is magnitude-driven and largely
(not entirely) coincides with the loss. Honest positioning: FIM_norm is a
spectral summary of the per-sample gradient-energy distribution that adds a
modest, sometimes-significant signal beyond mean loss, and is BatchNorm-immune
(its one clear advantage over activation-space metrics). That is a real but
narrower contribution than the abstract suggested.

---

## Test 11 — DECISIVE: FIM@ep20 vs final test_acc, controlling for loss@ep20

6 heterogeneous conditions (n in {100,400,800}, noise in {0,0.3,0.5}, l2 in
{0,1e-3}) x 5 seeds = 30 runs. Conditions chosen to decouple early loss from
final generalization. ep_early=20, epochs=200.

[1] Raw early predictors vs FINAL test_acc (Spearman):
| early signal | rho     | p        |
|--------------|---------|----------|
| fim_train@20 | -0.379  | 3.9e-02  |
| fim_eval@20  | -0.514  | 3.7e-03  |
| train_loss@20| -0.860  | 1.2e-09  |
| val_loss@20  | **-0.924** | **3.3e-13** |

val_loss@20 alone is a FAR better early predictor than any FIM variant.

[2] Partial correlation FIM@20 vs final_te | loss@20 (the decisive test):
| partial                          | r      | p       | verdict |
|----------------------------------|--------|---------|---------|
| fim_train vs te \| train_loss     | +0.157 | 0.41    | fails   |
| fim_train vs te \| val_loss       | -0.076 | 0.69    | fails   |
| fim_eval  vs te \| train_loss     | -0.087 | 0.65    | fails   |
| fim_eval  vs te \| val_loss       | +0.216 | 0.25    | fails   |

After controlling for loss, FIM has ZERO independent early signal (best case
wrong-signed).

[3] Reverse asymmetry — loss beyond FIM:
| partial                       | r      | p       |
|-------------------------------|--------|---------|
| train_loss vs te \| fim_eval   | -0.805 | 8.0e-08 |
| val_loss   vs te \| fim_eval   | -0.900 | 1.3e-11 |

Loss keeps essentially ALL its predictive power after controlling for FIM. The
relationship is one-directional: FIM is a (noisy, weaker) function of loss.

[4] Why the hypothesized mechanism fails — per-condition ep20 means:
| cond       | fim_ev | val_loss | final_te |
|------------|--------|----------|----------|
| B_n400 cln | 0.680  | 1.611    | 0.882    |
| E_n400_n30 | 0.685  | 1.810    | 0.860    |
| F_n400_n50 | 0.709  | 1.938    | 0.799    |

The hoped-for mechanism was "noise gives deceptively low early loss, FIM catches
it." It does NOT happen: label noise raises val_loss@20 immediately (1.61 -> 1.81
-> 1.94), so val_loss already encodes the damage. FIM (range 0.68-0.71) lacks the
dynamic range to add anything.

### VERDICT: strong thesis does NOT survive.
FIM_norm@ep20 is an early loss proxy with less predictive power than validation
loss. It adds no independent early signal. Consequences:
- The training-efficiency / early-stopping product thesis is closed (a practitioner
  uses val_loss — free, already computed, and strictly better).
- This retroactively weakens Test 2's "better early predictor than sharpness"
  claim, because LOSS was never the control there; loss likely beats both.
- What genuinely survives: (a) BatchNorm/LayerNorm immunity (parameter-space) —
  but loss shares this; (b) an honest measurement finding that gradient effective
  rank tracks, but does not exceed, the loss as a generalization correlate.

---

## Test 12 — FIM@init (the one regime where loss is structurally uninformative)

At init every model has loss ~ log(10) ~ 2.30, so loss cannot discriminate.
Any FIM@init -> final_te correlation would therefore be beyond-loss by construction.

TEST A — FIM@init across heterogeneous conditions (n,noise vary), 6x5=30 runs:
  FIM@init  vs final_te:  rho=-0.305  p=0.102  (n.s., right direction)
  loss@init vs final_te:  rho=+0.180  p=0.340  (flat, range [2.335, 2.579] — as expected)

TEST B — FIM@init across 20 inits, FIXED data (n=400 clean):
  FIM@init  vs final_te:  rho=+0.377  p=0.101  (n.s., WRONG sign)
  FIM@init range [0.603, 0.777], final_te range [0.875, 0.920]

VERDICT: METRIC CLOSED. Neither sub-test is significant, and they disagree in
sign (A negative, B positive) — there is no coherent beyond-loss signal at init.
Combined with Test 11 (null at ep20) and Tests 1-10 (final-epoch FIM tracks but
does not exceed loss), the conclusion is robust: gradient effective rank is
dominated by loss at every point in training. Loss is free and strictly better.

What this leaves as genuine findings:
1. v1's BatchNorm failure is fixable by moving to parameter space (real, narrow).
2. A rigorous metric-validation methodology that killed its own metric in hours.
3. A clean, citable negative result on gradient-erank-as-generalization-predictor.

---

## Summary Table

| Property | CEI v1 | FIM_norm (v2) |
|---|---|---|
| Dual acid test (MLP) | not tested | PASSES |
| CNN + BatchNorm | FAILS | PASSES |
| Transformer + LayerNorm (n_train) | not tested | PASSES |
| Transformer + LayerNorm (noise) | not tested | PARTIAL (direction ok) |
| Better early predictor than sharpness | no | YES (ep20) |
| Detects label noise independently | no | YES |
| Architecture-agnostic (capacity axis) | no | YES |
| Stable at N=100 | n/a | YES (CV<10%) |
| Compute cost | 0.002s | 0.06s (N=100) |
| Reliable auto stopping | n/a | NOT YET |

---

## What FIM_norm measures

The fraction of maximum gradient dimensionality that the network actively
uses during training. A network that has learned a constrained, structured
representation concentrates gradient updates in few directions (low FIM_norm).
A memorising or noise-fitting network scatters updates across many independent
directions (high FIM_norm).

This is the precise neural network analog of the original SHH structural
constraint concept: a mature constrained system has fewer independent modes
of response.

## Open questions for next phase

1. Does FIM_norm noise sensitivity hold for transformers with weaker regularisation?
2. Adaptive threshold calibration for reliable early stopping
3. Combined FIM_norm + sharpness predictor vs either alone
4. FIM_norm at initialization as a predictor of trainability
5. ResNet-18/CIFAR-10 full replication — waiting on results
6. Does FIM_norm add information beyond trace_norm/grad_norm in full study?
