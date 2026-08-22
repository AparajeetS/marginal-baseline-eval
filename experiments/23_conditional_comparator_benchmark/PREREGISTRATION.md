# Conditional Comparator Benchmark

Frozen known-truth protocol. No protected metric association is used to choose
methods, tuning, thresholds, or simulations.

## Design

Use the experiment 21 image and text factorials with 48 and 24 independent
configurations, respectively, two rows per configuration, all three baseline
levels, five null families, reliability 0.30/0.80, and interaction increments
0.20/0.35/0.50. Run 100 paired repetitions per cell under a new seed namespace.
Evaluate both the synthetic metric and the random negative control.

## Methods

1. Raw configuration-mean Spearman (`alpha=0.05`), as a weak reference.
2. Cross-fitted residual Spearman (`alpha=0.05`).
3. Unweighted rank GCM with normal inference (`alpha=0.05`).
4. The degree-2/ridge-0.1 orthogonal wild score (`p <= 0.001`).
5. Single-split WGCM.est: 30% independent groups estimate the sign weight,
   with degree-2/ridge-0.1 interaction regression (`alpha=0.05`).
6. KCI from `causal-learn==0.1.4.8`, Gaussian kernels, median bandwidth,
   gamma approximation (`alpha=0.05`).
7. MBE grouped cross-fit residual permutation plus positive Delta-MSE interval
   using degree-2/ridge-0.1 interaction regression (`alpha=0.05`).
8. CRT is recorded as non-estimable because no validated sampler for the metric
   conditional on controls exists in these designs.

KCI, GCM, WGCM, and MBE target different conditional-dependence or predictive
estimands. Results are compared by null control, power, estimability, sign,
runtime, and assumptions; there is no global winner label.

Configuration-level comparators aggregate the two replicate rows and exclude
`seed_id`, which varies within a configuration. MBE and the orthogonal wild
score retain row-level data with configuration-group inference.

## Integrity

All methods receive paired simulations. Every method failure and abstention is
retained. The runner, source simulator, package implementations, protocol, and
dependency pins are hashed before the full run. Protected reads remain false.

Primary references:

- Shah and Peters (2020), GCM:
  https://doi.org/10.1214/19-AOS1857
- Scheidegger, Hoerrmann, and Buehlmann (2022), WGCM:
  https://www.jmlr.org/papers/v23/21-1328.html
- Zhang, Peters, Janzing, and Schoelkopf (2011), KCI:
  https://arxiv.org/abs/1202.3775
