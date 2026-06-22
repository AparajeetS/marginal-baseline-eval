# Metric Audit: Validating Internal Representations in Neural Networks

This repository contains the complete experimental code, raw results, and formal theory behind the negative result on the Configurational Exposure Index (CEI) and its parameter-space successor, Gradient Effective Rank ($\text{FIM}_{norm}$).

## The Premise
We set out to operationalize the **Structural Homeostasis Hypothesis (SHH)** for deep learning. We hypothesized that networks that generalize well maintain a bounded internal interaction complexity during training. We designed $\text{FIM}_{norm}$ to track this.

It passed every standard test—including rigorous orthogonal label-noise and capacity probes across MLPs, CNNs, and Transformers. **But it decisively failed a strict partial-correlation baseline control against early validation loss.**

This repository is an open case study in why AI safety metrics must be audited against trivial baselines.

## Repository Structure

### `metric_audit/`
Contains the core measurement logic.
- `sci_tracker.py`: Computes the effective rank of activation covariance (CEI) and gradient duals ($\text{FIM}_{norm}$) across network layers.

### `experiments/`
The 12-test validation suite that systematically validated, and then killed, the metric.
- **`01_acid_tests/`**: The dual acid test on MLPs (label noise vs. capacity) and stability analysis.
- **`02_architectures/`**: Cross-architecture tests to verify immunity to normalization artifacts (CNN+BatchNorm, Transformer+LayerNorm).
- **`03_comparisons/`**: Baseline comparisons against Trace Norm, Sharpness (SAM), and Bootstrap Confidence Intervals.
- **`04_falsification/`**: The decisive falsification tests. `fim_early_predictor.py` (Test 11) runs the loss-baseline partial correlation control. `fim_init_test.py` (Test 12) proves the metric is null at initialization.

### `docs/`
- `FINDINGS.md`: The master ledger of all experiments, falsifications, and the final conclusion.
- `RESULTS.md`: Raw numerical output, statistical correlations, and data tables for the 12 tests.
- `theory.md`: The mathematical derivations for $\text{FIM}_{norm}$, moving from activation space to parameter space.

## The `metric-audit` Methodology
We propose the validation sequence found in this repository as a standard for new internal metrics:
1. **Dual Acid Test:** Does the metric track capability (capacity) and degradation (noise) consistently?
2. **Cross-Architecture:** Does it survive normalization layers (BatchNorm/LayerNorm)?
3. **Loss-Baseline Partial Correlation:** Does it predict generalisation *beyond* what the validation loss already predicts?
4. **Initialization Probe:** Does the signal exist when the loss is flat?

If your metric fails step 3 or 4, it is a proxy, not a novel signal.

## Running the Code
The tracker relies on standard `numpy` and `torch` (for the PyTorch wrappers). All tests log to console and export data/images (e.g., `*.csv`, `*.png`) to the local directory.

```bash
# Example: Run the decisive Test 11 falsification
cd experiments/04_falsification
python fim_early_predictor.py
```
