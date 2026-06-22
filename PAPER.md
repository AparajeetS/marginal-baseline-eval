# Metric Audit: How a Negative Result on Structural Homeostasis Produced a Reusable Metric Validation Framework

**Aparajeet Shadangi**  
*Independent Researcher*  
*June 2026*  

**Repository:** [AparajeetS/metric-audit-paper-code](https://github.com/AparajeetS/metric-audit-paper-code)

---

## Abstract

A recurring pattern in deep learning safety and interpretability is the proposal of internal metrics—computed from weights, activations, or gradients—that claim to track model health, generalization, or structural constraints. However, such metrics often correlate strongly with target properties while carrying no predictive signal beyond a trivial baseline, such as the training loss. 

This paper documents a comprehensive negative result. We originally sought to translate the Structural Homeostasis Hypothesis (SHH)—a principle of bounded coupling observed in mature software dependency graphs—into deep neural networks. We proposed the Configurational Exposure Index ($\text{CEI}$) to measure internal interaction complexity. Moving from activation space ($\text{CEI}_{v1}$) to parameter space ($\text{CEI}_{v2}$, or $\text{FIM}_{norm}$) allowed the metric to survive normalization artifacts. $\text{FIM}_{norm}$ easily passed rigorous "dual acid tests" (orthogonal label-noise and capacity probes) across MLPs, CNNs, and Transformers, appearing as a robust, architecture-agnostic generalization predictor. 

However, we subjected the metric to a strict baseline control: partial correlation against early validation loss. Under this control, the metric's predictive power collapsed entirely. It offered zero predictive value beyond the loss at epoch 20 (partial $r = +0.216, p=0.25$), and yielded a null, sign-inconsistent result at initialization ($\rho = -0.305, p=0.10$). 

We publish this sequence not to promote the metric—which we decisively falsified—but to promote the rigorous falsification sequence itself. We formalize this sequence into `metric-audit`: a reusable four-step validation methodology to prevent the publication of representation metrics that offer false assurance.

---

## 1. Introduction: The Software Origins of SHH

Before exploring neural networks, this investigation began in the architecture of large-scale open-source software systems. 

### 1.1 The Collapse Hypothesis
We initially posited the "Collapse Hypothesis" for complex systems: *as a system grows, its internal interactions (dependencies) increase faster than its constraint capacity, eventually leading to structural instability and a "configurational collapse."* 

To test this, we analyzed the longitudinal dependency graphs of five massive Python ecosystems over years of commit history: **NumPy, Pandas, Django, FastAPI, and Apache Airflow**. We measured the "Configurational Exposure Index" (CEI) of the graph—essentially the ratio of import edges to internal modules (average internal degree), alongside the Strongly Connected Component (SCC) fraction.

### 1.2 Falsification and the Birth of SHH
The Collapse Hypothesis failed spectacularly. Across all five systems, we found no monotonic densification or approach to structural criticality. 
- **NumPy** maintained a stable average degree of $\sim 0.6$ and an SCC of $1-2\%$ across all tested versions.
- **Pandas** showed an initial spike in entanglement (degree 4, SCC 24%), followed by progressive, deliberate modularization (dropping to degree 1.7, SCC 9%).
- **Apache Airflow** exhibited oscillatory dynamics, bouncing between architectural resets (9.5% $\to$ 1.8% $\to$ 5%) but never entering runaway entanglement.

Instead of divergence, we observed *structural regulation*. Systems operate within bounded average degree regimes. This observation gave rise to the **Structural Homeostasis Hypothesis (SHH)**: *Mature engineered systems exhibit bounded internal coupling regimes and maintain small cyclic cores across growth phases, often converging toward modular sparsity.*

---

## 2. Formalizing SHH for Neural Networks ($\text{CEI}_{v1}$)

We asked: *does an analogous structural self-organization hold in deep networks during training?* Does the effective interaction complexity of each layer's computation stay bounded, and does that boundedness correlate with generalization?

We defined the neural network analogue of CEI as the normalized effective rank of a layer's activation covariance matrix.

**Definition 1 (Activation Second Moment):** For a dataset $\mathcal{D} = \{x_1, \ldots, x_B\}$ and layer $l$, the post-activation output is $h_l(x) \in \mathbb{R}^{n_l}$. The covariance is:
$$ \Sigma_l = \frac{1}{B} \sum_{i=1}^{B} h_l(x_i)\, h_l(x_i)^\top \in \mathbb{R}^{n_l \times n_l} $$

**Definition 2 (Effective Rank):** For a positive semidefinite matrix $M$ with singular values $\sigma_1 \geq \cdots \geq \sigma_r > 0$, the effective rank (Roy & Vetterli, 2007) is the exponential of the Shannon entropy of the normalized singular-value distribution:
$$ \text{erank}(M) = \exp\!\left(-\sum_{k=1}^{r} p_k \log p_k\right), \quad p_k = \frac{\sigma_k}{\sum_j \sigma_j} $$

**Definition 3 (Layer CEI):** The Configurational Exposure Index of layer $l$ is:
$$ \text{CEI}_l = \frac{\text{erank}(\Sigma_l)}{n_l} \in (0, 1] $$

A $\text{CEI}$ of $1$ means all $n_l$ neurons act independently (maximally unconstrained). A $\text{CEI}$ near $0$ means the activations have collapsed onto a single direction (maximally constrained).

### 2.1 The First Failure: Activation Space and Normalization
$\text{CEI}_{v1}$ tracked generalization well on a simple Tanh MLP. But when deployed on a CNN with BatchNorm, it failed completely. Normalization layers actively re-center and rescale activations across the batch, corrupting the intrinsic geometry of the activation space. Furthermore, activation rank inherently conflates the data's intrinsic geometry with the network's learned structure. We needed a metric that survived normalization.

---

## 3. The Move to Parameter Space: Gradient Effective Rank ($\text{FIM}_{norm}$)

To survive BatchNorm and LayerNorm, we moved from the forward pass (activation space) to the backward pass (parameter space). We hypothesized that a network that has learned a constrained, structured representation will concentrate its gradient updates in a few dominant directions. A memorizing network will scatter updates across many independent directions.

For a network with parameters $\theta$, dataset $(X, y)$, and loss $\mathcal{L}$:
$$g_i = \nabla_{\theta} \mathcal{L}(x_i, y_i; \theta)$$

We compute the dual $N \times N$ Gram matrix of the per-sample gradients (where $N$ is the number of samples in the empirical Fisher batch):
$$G = [g_1, g_2, \dots, g_N]^T$$
$$S_{dual} = \frac{1}{N} G G^T$$

**Definition 4 (Structural Constraint Index / Gradient Effective Rank):**
$$\text{FIM}_{norm} = \frac{\text{erank}(S_{dual})}{N}$$

*(Note: While $S_{dual}$ shares its nonzero spectrum with the empirical Fisher Information Matrix, we do not invoke true Fisher-Rao or PAC-Bayes guarantees, as we use observed, not model-sampled, labels. We treat this strictly as a measure of empirical gradient diversity).*

---

## 4. The `metric-audit` Validation Sequence

We subjected $\text{FIM}_{norm}$ to a systematic, four-stage validation sequence designed to expose common failure modes in proposed representation metrics. 

### Stage 1: The Dual Acid Test (MLP)
Naive metrics, such as Gradient Coherence (mean cosine similarity), fail the "dual acid test" by conflating data volume with label quality. Coherence decreases with label noise (good), but it also decreases with more training data (bad, as more data improves generalization). 

We tested $\text{FIM}_{norm}$ on a Tanh MLP with 4 layers (sizes 8192, 8192, 2048, 320) using $N=100$ gradient samples.

| Probe | Condition | $\text{FIM}_{norm}$ | Test Acc | Spearman $\rho$ (p-value) |
|-------|-----------|--------------------|----------|---------------------------|
| **Capacity** | $n=40$ | 0.642 | 0.585 | \multirow{4}{*}{**-0.937** ($6.99 \times 10^{-6}$)} |
| (Fixed 0% noise) | $n=200$ | 0.387 | 0.830 | |
| | $n=400$ | 0.282 | 0.887 | |
| | $n=800$ | 0.143 | 0.918 | |
| **Noise** | 0% | 0.282 | 0.887 | \multirow{4}{*}{**-0.770** ($3.41 \times 10^{-3}$)} |
| (Fixed $n=400$) | 15% | 0.353 | 0.883 | |
| | 30% | 0.472 | 0.872 | |
| | 50% | 0.615 | 0.805 | |

**Verdict:** PASS. In both orthogonal probes, lower $\text{FIM}_{norm}$ correlated consistently and significantly with better test accuracy. 

### Stage 2: Cross-Architecture Normalization Harness
We deployed the metric on architectures that previously broke $\text{CEI}_{v1}$.

**CNN + BatchNorm** (Small PyTorch CNN on Digits)
- Capacity Probe: $\rho = -0.837, p = 6.93 \times 10^{-4}$
- Noise Probe: $\rho = -0.956, p = 1.20 \times 10^{-6}$

**Transformer + LayerNorm** (2-layer ViT-style Encoder, $d_{model}=64$, 8 patches)
- Capacity Probe: $\rho = -0.951, p = 2.04 \times 10^{-6}$
- Noise Probe: $\rho = -0.476, p = 1.18 \times 10^{-1}$ (Correct direction, but n.s. due to high variance; the architecture heavily resists noise memorization).

**Verdict:** PASS. The parameter-space formulation successfully bypasses normalization artifacts, remaining robust across architectures.

### Comparison vs. SAM Sharpness (Early Predictor)
We tracked $\text{FIM}_{norm}$ and SAM Sharpness across 6 conditions with 3 seeds. 
At epoch 20 (early training):
- $\text{FIM}_{norm}$: $\rho = -0.629, p = 5.2 \times 10^{-3}$ (Significant)
- SAM Sharpness: $\rho = -0.440, p = 0.068$ (Not significant)

Sharpness failed here because it is blind to label noise—it finds flat minima even when fitting 30% noise. $\text{FIM}_{norm}$ detected the noise successfully.

---

## 5. The Decisive Control: Falsifying $\text{FIM}_{norm}$

Had we stopped at Stage 2, we would have published a paper claiming a breakthrough structural metric that beats Sharpness. However, a safety metric is only useful if it provides a signal *beyond* the trivial metrics already available—namely, the validation loss.

### Stage 3: The Loss-Baseline Partial Correlation
We ran 30 heterogeneous runs (varying $n$, noise, and L2 regularization) to completely decouple early loss from final generalization. We evaluated predictors at epoch 20.

**Raw Predictors vs. Final Test Accuracy:**
| Early Signal (@ep20) | Spearman $\rho$ | p-value |
|----------------------|-----------------|---------|
| $\text{FIM}_{norm}$ (eval) | -0.514 | $3.7 \times 10^{-3}$ |
| Training Loss | -0.860 | $1.2 \times 10^{-9}$ |
| Validation Loss | **-0.924** | $\mathbf{3.3 \times 10^{-13}}$ |

Validation loss was immediately superior. But the true test is partial correlation: does the metric add *any* unique variance?

**Partial Correlation (The Kill Shot):**
| Partial Relationship | $r$ | p-value | Verdict |
|----------------------|-----|---------|---------|
| $\text{FIM}_{norm}$ vs. Acc $\mid$ Val Loss | **+0.216** | **0.25** | **FAILS (zero independent signal)** |
| Val Loss vs. Acc $\mid$ $\text{FIM}_{norm}$ | -0.900 | $1.3 \times 10^{-11}$ | Loss retains all power |

**Verdict:** FAIL. The relationship is strictly one-directional. $\text{FIM}_{norm}$ acts as a noisy, weaker shadow of the loss. 

### Stage 4: The Initialization Probe
To definitively prove the metric lacked an independent geometric signal, we evaluated it at initialization, where the loss is structurally flat for all models ($\mathcal{L} \approx 2.30$ for 10 classes). If $\text{FIM}_{norm}$ had a genuine geometric signal, it would shine here because the loss baseline cannot discriminate.

- **Test A (Heterogeneous conditions):** $\rho = -0.305, p=0.10$ (n.s.)
- **Test B (Fixed data, varying seeds):** $\rho = +0.377, p=0.10$ (n.s., wrong sign)

**Verdict:** FAIL. The metric is dead. It carries no coherent geometric signal independent of the loss.

---

## 6. Mechanistic Autopsy

Why did $\text{FIM}_{norm}$ pass the acid tests and track generalization at all? 

We initially hypothesized it measured the intrinsic dimensionality of learned gradient directions. To verify this, we unit-normalized the per-sample gradients—destroying magnitude while preserving purely directional geometry. 

When we ran this, the predictive signal vanished entirely (the capacity correlation flipped from $-0.924$ to $+0.374$).

This revealed that $\text{FIM}_{norm}$ is fundamentally **magnitude-driven**. It measures the effective concentration of gradient *energy*. High-loss (hard or noisy) examples produce large gradients that dominate the Gram matrix spectrum, driving the effective rank up. The metric is essentially a participation-ratio statistic of the loss distribution, which is why it collapses exactly when the loss collapses (e.g., during memorization in over-parameterized ResNets).

---

## 7. Conclusion

Gradient effective rank ($\text{FIM}_{norm}$) is a robust, normalization-immune proxy for the concentration of gradient energy. However, it provides **no predictive value beyond the validation loss at any training checkpoint**. Practitioners should rely on validation loss, which is computationally free and strictly superior.

More importantly, this case study demonstrates the critical necessity of the `metric-audit` protocol. As AI safety increasingly relies on internal representation metrics, we must demand that proposed signals pass the four-stage validation sequence—specifically, they must demonstrate marginal predictive value beyond trivial baselines via partial correlation. 

An internal representation metric that cannot beat validation loss is not a safety metric; it is an illusion.
