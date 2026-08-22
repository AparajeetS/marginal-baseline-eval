# PGDL Tasks 6-9 Transfer Calibration

Frozen before any checkpoint-derived metric association from PGDL Tasks 6-9
is computed or inspected.

## Purpose

Test whether the confirmed 192-group conditional-rank rule remains calibrated
on the actual pooled PGDL transfer geometry: 240 independent models across four
tasks, one row per model, unequal task sizes, task-specific hyperparameters,
and the declared baseline ladder.

The runner reads no generalization target and no checkpoint-derived metric. It
loads only run identity, task, frozen hyperparameters, training loss, and
training accuracy.

## Verified Geometry

- Task 6: 96 models.
- Task 7: 48 models.
- Task 8: 64 models.
- Task 9: 32 models.
- Pooled: 240 unique independent models.

Task-specific hyperparameters are mapped in their frozen order to six generic
slots and interacted with task identity by the nuisance model. Missing sixth
slots are fixed at zero. Baselines are B1 task plus hyperparameters, B2 plus
training loss, and B3 plus training accuracy.

Numeric controls retain their numeric values. Any nonnumeric task-specific
control is encoded by lexicographically sorted integer levels, with the exact
mapping recorded in the run manifest. This mapping uses allowed design metadata
only and does not inspect a generalization target or checkpoint metric.

## Fixed Method And Grid

Use configuration-mean cross-fitted rank residual products, degree-4 ridge with
pairwise interactions, ridge 10, five grouped folds, 4,999 studentized
Rademacher draws, and a two-sided threshold of 0.001.

Run 100 repetitions for reliability 0.30 and 0.80, five null families, and
positive effects 0.20, 0.35, and 0.50. Synthetic surfaces are generated solely
from the allowed baseline columns. Panel and analysis seeds use a new protocol
namespace disjoint from development and confirmation.

## Gate

Every baseline must have at least 98% estimability, largest null-support Wilson
95% upper bound at most 10%, and smallest effect-0.50 positive-power Wilson 95%
lower bound at least 50%. Global pass requires all three baselines.

A pass permits freezing a pooled PGDL transfer analysis packet. It does not by
itself permit metric extraction or outcome inspection. A failure preserves the
holdout and requires abstention.
