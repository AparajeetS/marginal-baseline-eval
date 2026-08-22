# Corrected Causal-Text Factorial

Status: preregistered primary factorial, launched after the causal-language
pipeline pilot completed with 24 valid rows and a passing causal-mask negative
control.

## Frozen design

- Dataset and split: official WikiText-2 train/validation/test splits.
- Architectures: small (96d, 2 layers, 4 heads) and medium (160d, 4 layers,
  8 heads) causal Transformers.
- Training configurations: 10 frozen learning-rate, weight-decay, and dropout
  settings shared across sizes.
- Repeats: five independent initialization/data-order seeds per configuration.
- Primary total: `2 x 10 x 5 = 100` runs.
- Training budget: 6,000 updates per run, batch size 48, sequence length 64.

The runner writes rows atomically and resumes by `run_id`. It emits the causal
mask behavioral test, split hashes, configuration IDs, seed IDs, run UUIDs,
metrics, timing, and failed rows. Every non-random metric is measured on three
deterministic training batches, recording a within-model batch standard
deviation for later measurement-reliability reporting. The evidence is
restricted to this one environment until an independently frozen transfer
environment is run.
