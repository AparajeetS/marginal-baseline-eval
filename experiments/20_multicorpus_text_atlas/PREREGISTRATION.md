# Multi-Corpus Causal-LM Atlas Preregistration

Frozen on 2026-08-11 before submission or inspection of any result from this
experiment.

## Question

Do training-metric reliability profiles replicate within and transport across
three causal language-model environments when architecture and training
interventions are balanced and test outcomes remain separate from validation?

## Environments

- WikiText-2 using its official train, validation, and test files.
- Penn Treebank using its public train, validation, and test files.
- Tiny Shakespeare using a frozen contiguous 80/10/10 split.

Dataset bytes and vocabulary sizes are hashed in the generated manifest. A
causal-mask leakage test and an unmasked negative control must pass before
training begins.

## Design

Within each environment:

- two Transformer sizes;
- learning rates 0.0002, 0.0006, and 0.0015;
- weight decay 0 or 0.01;
- dropout 0 or 0.2;
- 24 independent configurations;
- seeds `8201` and `8202`, giving 48 runs per environment.

The full atlas contains 72 configurations and 144 planned trained models.
Each run uses 2,000 optimization steps, sequence length 64, batch size 48, and
three independent diagnostic batches. A random negative control is generated
independently for every full `run_id`.

The run order is balanced across corpora. The notebook stops cleanly before
Kaggle's wall-clock limit and retains all failures.

## Outcomes And Controls

Primary targets are test token loss and perplexity; token accuracy is
secondary. Prespecified design controls are model size, learning rate, weight
decay, dropout, and seed. Training-state extensions add final training-batch
loss and then validation loss.

Environment-specific results are primary. Cross-environment heterogeneity is
reported directly; a single pooled universal ranking is not a primary claim.

## Completion Gate

Primary analysis requires at least 90% of planned valid runs and at least 20
complete two-seed configurations in every environment. Analyses use complete
configurations only, while all failed and incomplete rows remain visible.

## Analysis Boundary

Nuisance-family eligibility must be selected using design-matched known-truth
calibration without consulting real metric outcomes. Until that calibration
gate is frozen, model-family outputs are components and substantive metric
verdicts abstain.

This atlas can test corpus transport for small causal Transformers. It cannot
establish transport to instruction-tuned or frontier-scale language models.
