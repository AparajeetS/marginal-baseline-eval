# CEI v2 — Structural Constraint Index via Per-Sample Gradient Spectrum

## The v1 Problem (recap)

CEI v1 = erank(Σ_activation) / n_l. Measured runtime activation geometry,
per layer, averaged. Failures: BatchNorm flips direction on CNNs (it
renormalises activations, corrupting any activation-space metric); activation
rank conflates the data's intrinsic geometry with the network's learned
structure. The fix is to move from **activation space** (forward pass) to
**parameter/gradient space** (backward pass), which normalisation layers do
not corrupt.

## Candidate exploration (v2 search)

| Metric | rho direction | Consistent across experiments? | Verdict |
|---|---|---|---|
| abs weight erank | correct | yes | range 0.0004, frozen |
| delta-W erank | correct | n_train confound | fails |
| layer alignment | weak p=0.29 | — | noise |
| gradient rank | correct | L2 confound | fails |
| gradient coherence | FLIPS | no | fails |
| **FIM_norm** | **correct** | **yes, both significant** | **PASSES** |

## CEI v2 Definition

### Per-sample gradient second-moment matrix

For a network with parameters theta, data (X, y), loss L:

  g_i = nabla_theta L(x_i, y_i; theta)   [per-sample gradient vector]

  S = (1/N) sum_{i=1}^{N} g_i g_i^T   [gradient 2nd moment, shape d x d]

> **Terminology note (important).** S equals what the literature sometimes
> calls the *empirical Fisher*. It is NOT the true Fisher information matrix:
> the true Fisher samples labels from the model's own predictive distribution
> p_theta(y|x), whereas S uses the observed labels y_i. Their eigenstructure
> differs, and erank measures exactly that eigenstructure (Kunstner, Hennig &
> Balles, "Limitations of the Empirical Fisher Approximation", NeurIPS 2019).
> We therefore do NOT inherit Fisher-Rao / natural-gradient / PAC-Bayes
> guarantees. We treat S as what it literally is: the **second moment of the
> per-sample gradient distribution**, i.e. a measure of gradient diversity.
> The metric stands on its own empirical merits, not on borrowed Fisher theory.

### Structural Constraint Index (FIM_norm)

Compute via the dual N x N Gram matrix (N << d in practice):

  G = [g_1, g_2, ..., g_N]^T   (N x d matrix)
  S_dual = G G^T / N            (N x N matrix, same nonzero spectrum as S)

  erank(S_dual) = exp( -sum_k p_k log p_k )
                 where p_k = sigma_k / sum_j sigma_j
                 sigma_k = singular values (= eigenvalues, PSD) of S_dual

  FIM_norm = erank(S_dual) / N

The dual identity erank(G G^T) = erank(G^T G) holds exactly: the N x N and
d x d matrices share their nonzero spectrum, hence identical normalised-entropy.
This makes the metric tractable for any d (compute the N x N matrix).

### Range and interpretation

FIM_norm in (1/N, 1].

- FIM_norm -> 1/N:  one dominant gradient direction; all samples pull the
                    network the same way. Maximum structural constraint.
- FIM_norm -> 1:    N independent gradient directions; each sample pulls
                    in a completely different direction. No constraint.

**Generalisation hypothesis**: Lower FIM_norm = more structurally constrained
= better generalisation. The network has learned to respond to the data in a
concentrated, structured way rather than memorising independent patterns.

## METHODOLOGICAL STANDARDS (must hold across all experiments)

These were not uniform in the first round of experiments and are now codified:

1. **Same data partition.** FIM_norm is computed on the **TRAINING set**
   (X_tr, y_tr) in every experiment. Rationale: the noise mechanism (corrupted
   labels -> scattered gradients) only exists where the corrupted labels live,
   i.e. the training set. (The original CIFAR run mistakenly used a held-out
   eval set and produced a wrong-direction result; corrected.)

2. **Fixed N across a probe.** Within any single probe (e.g. the n_train sweep)
   N must be constant, because erank/N shrinks mechanically with N once N
   exceeds the true gradient rank. The original n_train probe used N=40 for
   n=40 but N=100 for n>=200 — a confound on the smallest-n endpoint. Report
   raw erank at fixed N, or hold N = min(n_train) across the sweep.

3. **Same N_FIM and same epochs** within a probe (already satisfied).

## Empirical validation

### Dual acid test (both experiments must show consistent direction)

**Experiment A — Label noise (n=400 FIXED, epochs=200 FIXED, noise varies):**

| noise | FIM_norm | test_acc |
|-------|----------|----------|
|   0%  |  0.282   |  0.887   |
|  15%  |  0.353   |  0.883   |
|  30%  |  0.472   |  0.872   |
|  50%  |  0.615   |  0.805   |

Spearman rho = -0.770, p = 3.41e-03.  Lower FIM_norm = better test acc.
(Clean probe: n=400 fixed -> N=100 fixed throughout. No N confound.)

**Experiment B — n_train (noise=0 FIXED, epochs=200 FIXED, n_train varies):**

| n_train | FIM_norm | test_acc |
|---------|----------|----------|
|   40    |  0.642   |  0.585   |
|  200    |  0.387   |  0.830   |
|  400    |  0.282   |  0.887   |
|  800    |  0.143   |  0.918   |

Spearman rho = -0.937, p = 6.99e-06.  Monotone, very significant.
CAVEAT: n=40 used N=40 while n>=200 used N=100. The trend among n in
{200,400,800} at fixed N=100 (0.387 -> 0.282 -> 0.143) is clean; the n=40
endpoint is partly confounded by smaller N. Needs a fixed-N rerun to claim
the full rho cleanly.

### Consistency check: PASSES
- Same direction (negative) in both experiments: YES
- Both p < 0.05: YES

### What every previous metric failed

Gradient coherence (GC): rho = -0.862 for n_train probe (lower = better),
but rho = +0.842 for noise probe (HIGHER = better). Direction flips.
GC failed because it conflates data richness (more data -> lower GC) with
label quality (noisy labels -> lower GC), which have opposite effects on
test accuracy.

FIM_norm avoids this because, after normalization by N, both more noise AND
less data -> higher FIM_norm -> worse test accuracy. Consistent direction.

## Mechanistic interpretation (calibrated to data)

**Why does noisy label training -> high FIM_norm?**
With corrupted labels, the gradient for each sample points toward a (partly)
random output class. Samples produce gradients in more independent directions
-> the Gram matrix G G^T spreads its spectrum -> erank rises -> FIM_norm rises.
NOTE: the limit is NOT reached — 50% label noise gives FIM_norm ~ 0.615, not
~ 1.0. The gradients retain substantial shared structure (the input features
are still real even when labels are random). So the mechanism is directional,
not saturating; the language should reflect that.

**Why does more data (clean) -> low FIM_norm?**
With many clean samples sharing class structure, gradients for similar samples
point in similar directions. The Gram spectrum concentrates on the dominant
class-discriminant directions -> low erank -> low FIM_norm.

**What the signal actually is (revised after the unit-norm diagnostic):**
Unit-normalizing each per-sample gradient before the Gram matrix DESTROYS the
predictive signal (n_train rho flips from -0.924 to +0.374). Therefore the
working signal is NOT the directional diversity of gradients — it is the
MAGNITUDE structure. High-loss / hard samples carry large gradients that
dominate the spectrum. FIM_norm = erank of the magnitude-weighted gradient
Gram = effective number of samples carrying significant gradient ENERGY,
divided by N. A generalizing model classifies most samples correctly (small
gradients) with energy concentrated on a few hard examples -> low erank. A
struggling / memorizing-in-progress model spreads gradient energy across many
samples -> high erank.

Consequence: FIM_norm is strongly correlated with the mean loss (both ~ -0.92
on the n_train probe). It adds a SIGNIFICANT but modest independent signal
beyond loss on n_train (partial p=0.018) and only a MARGINAL one on noise
(partial p=0.085). The independent contribution is the *concentration/inequality*
of per-sample gradient energy, beyond its mean — a participation-ratio statistic
of the loss distribution, not an intrinsic representational dimensionality.

**The connection to SHH (tempered):**
The original analogy — FIM_norm as the count of independent interaction modes,
echoing software SHH's bounded coupling — is weaker than first framed. The metric
tracks the concentration of learning effort across samples, which largely
coincides with the loss. The defensible, narrow claims are: (1) it is BatchNorm/
LayerNorm-immune because it lives in parameter space (the one clear win over
activation-space metrics like v1); (2) it summarizes the SHAPE of the per-sample
gradient-energy distribution, adding a modest signal beyond mean loss.

**Memorization collapse (over-parameterized regime):**
When a high-capacity model FULLY memorizes the training set (train loss -> 0),
all training gradients vanish and erank collapses -> FIM_norm at convergence can
no longer detect label noise (CIFAR condition C: FIM spikes at ep5 then collapses
to ~0.02 at ep14, tr=0.996). The noise signal is in the TRAJECTORY, not the final
value. This is a direct consequence of the magnitude-driven nature above.

## Positioning against existing literature (related work)

The honest novelty claim is narrow and defensible:

- **Gradient Signal-to-Noise Ratio (GSNR)** — Liu et al. 2020 relate the ratio
  of squared-mean to variance of gradients to generalisation. FIM_norm is a
  *spectral* (effective-rank) cousin: rather than a per-coordinate SNR, it
  measures the entropy of the gradient second-moment spectrum.
- **Coherent Gradients** — Chatterjee, ICLR 2020: generalisation arises when
  per-example gradients reinforce along shared directions. FIM_norm quantifies
  exactly that coherence as spectral concentration (low erank = coherent).
  Crucially, naive gradient *coherence* (mean pairwise cosine) FAILS the dual
  acid test by sign-flip; the effective-rank formulation does not.
- **Effective rank of representations** — Roy & Vetterli 2007 (definition);
  Kumar et al. 2023 (plasticity), Huh et al. 2024 (platonic) apply it to
  activations. v1 lived here. v2 applies erank to gradients instead.

NOVELTY: effective rank (entropy) of the per-sample gradient Gram matrix,
N-normalized, passes a dual acid test (noise + capacity) where GSNR-like
coherence fails. That is the contribution — not a new Fisher theory.

## Formal properties (corrected)

1. **Normalisation-invariant in computation**: computed in parameter space, so
   BatchNorm/LayerNorm (which act on activations) cannot corrupt it. Confirmed:
   passes on CNN+BatchNorm where v1 failed. NOTE: this is invariance in
   *computation*, not a guarantee of uniform predictive *performance* across
   architectures (the transformer noise probe was non-significant).

2. **Only gradients required**: works for any differentiable architecture; no
   activation hooks, no architecture-specific instrumentation.

3. **Tractable**: O(N^2 d) via the dual form. N=100 per-sample gradients.
   ~0.06s per measurement on the digits MLP. For large d the per-sample
   backward passes (N of them) dominate cost, not the N x N eigendecomposition.

4. **Gradient-diversity interpretation** (replaces the earlier Fisher-Rao
   claim): FIM_norm is the normalised effective rank of the gradient second
   moment — a measure of how many independent directions the per-sample
   gradients occupy. We make NO appeal to natural-gradient or PAC-Bayes theory,
   which concern the *true* Fisher (see terminology note above).

## Known limitations / open issues (carried forward)

1. **Empirical vs true Fisher** — addressed by reframing as gradient 2nd moment.
2. **N-confound on n_train probe** — needs fixed-N rerun (Standard 2).
3. **Whole-network only** — per-layer FIM_norm not yet computed; would recover
   v1's layer-localization story and reconnect to neural collapse.
4. **Layer-scale weighting** — concatenating gradients lets high-magnitude
   layers dominate; a per-layer-whitened variant is untested.
5. **Loss baseline untested** — must show FIM_norm predicts beyond the loss
   value itself (gradients scale with loss).
6. **Underpowered statistics** — n=12 / n=18 correlations; more seeds needed.
7. **Not a reliable stopping criterion** — confirmed negative in fim_early_stop.

## Open questions (status)

1. Does FIM_norm@early_epochs predict final test_acc?  ANSWERED: yes, ep20
   rho=-0.629 (p=5.2e-3), stronger early predictor than sharpness.
2. Does FIM_norm add info beyond SAM sharpness?  ANSWERED: yes, complementary
   (partial R^2 +0.031 at ep20; detects label noise where sharpness is blind).
3. Does direction hold on CNNs with BatchNorm?  ANSWERED: yes (the v1 failure).
4. Does it hold on Transformers (LayerNorm)?  PARTIAL: n_train rho=-0.951;
   noise probe correct direction but p=0.118 (underpowered at 3 seeds).
5. ResNet-18 / CIFAR-10 replication?  IN PROGRESS (corrected to training-data
   FIM; 15-epoch eval-data run produced wrong direction due to Standard 1).
6. Per-layer decomposition + loss baseline + fixed-N rerun?  TODO (this round).
