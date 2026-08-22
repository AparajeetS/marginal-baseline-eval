# Kaggle Submission Log: Causal-Text Factorial Sequential Replication

- Submitted: 2026-07-26 (Asia/Kolkata).
- Kernel: <https://www.kaggle.com/code/aparajeetshadangi/mbe-2-causal-text-factorial-replication>
- Script SHA-256: `c1afddee8e4becbc29799a3dd96a9a39e44bcbb57a8278a13fef284585a69429`

## Frozen execution

- Two causal Transformer sizes.
- 18 balanced learning-rate, weight-decay, and dropout configurations per
  size: a full `3 x 3 x 2` intervention grid.
- Five seeds per configuration: 180 runs and 36 independent configuration
  units.
- 6,000 updates per run; official WikiText-2 train/validation/test splits.
- Three deterministic diagnostic batches per completed model.
- One configuration-specific random negative-control value per full `run_id`.

## Relation to the first factorial

The earlier 100-run factorial remains public as a valid training-pipeline and
measurement-reliability artifact. It has 20 configuration units and a random
control that was constant after configuration aggregation because it reused
seed IDs. This run is a separately reported sequential replication, not a
post-hoc extension pooled with the earlier data.
