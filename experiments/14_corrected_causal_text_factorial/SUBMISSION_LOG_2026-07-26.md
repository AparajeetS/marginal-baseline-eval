# Kaggle Submission Log: Corrected Causal-Text Factorial

- Submitted: 2026-07-26 (Asia/Kolkata).
- Kaggle version 1: submitted the frozen 100-run factorial.
- Kaggle version 2: submitted while the first version was queued, adding the
  preregistered three-batch metric repeatability measurement. Version 2 is the
  authoritative execution.
- Kernel: <https://www.kaggle.com/code/aparajeetshadangi/mbe-2-corrected-causal-text-factorial>
- Script SHA-256: `ac866a358f46536ad69a985312aef7a212864c5fd2e1f8d945caa9b8297d7a4d`

## Frozen execution

- 2 causal Transformer sizes x 10 configurations x 5 seeds = 100 primary
  runs.
- 6,000 updates per run; WikiText-2 official train/validation/test splits.
- Three deterministic metric batches per completed model; batch standard
  deviations are written for all non-random metrics.
- Wall-clock limit: 11.5 hours, with 20-minute launch and 15-minute in-run
  reserves.
- Completed and failed rows are both retained. A restart resumes valid
  `run_id`s only.

## Scope guard

This run estimates within-environment metric reliability profiles for causal
language modelling. It cannot establish image-to-text transport or a universal
metric ranking; those require the separately frozen image and external-holdout
stages.
