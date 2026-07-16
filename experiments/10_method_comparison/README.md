# Shared Method Comparison

This work package compares raw Spearman, Kendall tau-b, linear partial
Spearman, Jiang-style granulated Kendall, Jiang-style normalized conditional
mutual information, and MBE on identical known-truth factorial ledgers.

The Jiang implementations follow equations 3-9 and Appendix A.5 of *Fantastic
Generalization Measures and Where to Find Them*. CMI is a descriptive empirical
criterion here, not a calibrated conditional-independence p-value. The exact
Dziugaite robust-sign-error comparison remains in the published-study reaudit
because its ESS weighting and environment construction are source-specific.

The sign-flip scenario contains real task-conditional information but no stable
global direction. It is intentionally not labeled a stable increment; a pooled
method should either model the heterogeneity explicitly or abstain.

```bash
python experiments/10_method_comparison/run_factorial_benchmark.py \
  --repetitions 50 --seeds-per-config 5 \
  --permutations 199 --bootstrap 199
```

The slower no-GPU inference calibration resamples independent configurations,
rebuilds folds, refits nuisance models, and separately calibrates within-block
permutation:

```bash
python experiments/10_method_comparison/run_refit_inference_calibration.py \
  --repetitions 20 --refit-draws 39 --permutations 99 \
  --block-repetitions 100 --output-dir experiments/10_method_comparison/out
```

The broader stress matrix separates the primary full-refit predictive interval
from the residual-permutation diagnostic across sample sizes, nuisance families,
and four dependence structures:

```bash
python experiments/10_method_comparison/run_inference_stress.py \
  --output-dir experiments/10_method_comparison/out
```
