# Causal-Text Factorial Sequential Replication

This is a new, separately reported WikiText-2 causal-LM factorial. It was
created after the prior 100-run factorial completed cleanly but exposed two
evidence limitations: only 20 independent configuration interventions, and a
random negative control seeded by the repeated seed ID rather than the full
run identity.

## Frozen design

- Two causal Transformer sizes.
- A balanced `3 x 3 x 2` grid of learning rate, weight decay, and dropout.
- Five independent seeds per configuration.
- `2 x 18 x 5 = 180` primary runs.
- 6,000 updates per run on official WikiText-2 splits.
- Three deterministic diagnostic batches per completed model.

The grid, target, metric list, baseline ladder, and negative-control definition
are frozen before launch. The random control is a deterministic Gaussian draw
from a SHA256-derived full `run_id` seed, while metric-batch sampling remains
matched by seed block. Results are reported as a sequential replication, not
pooled with the earlier grid as if both designs were selected before outcomes.
