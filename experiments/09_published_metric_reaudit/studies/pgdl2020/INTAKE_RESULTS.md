# PGDL Intake Results

## Corpus

The official byte-range intake recovered complete configuration ledgers for
550 models across eight tasks without downloading checkpoints or training
datasets. Every run ID is unique and every train/test accuracy and loss field is
present. All 550 models have training accuracy above 95%.

The unified accuracy-gap target varies materially within every task. Mean gaps
range from 0.075 in Task 8 to 0.517 in Task 7, so pooled task identity would be a
strong but scientifically uninteresting predictor. Primary reporting must
therefore remain task-specific before any pooled synthesis.

## Metadata Floor

`out/metadata_floor.csv` measures final training loss beyond each task's frozen
hyperparameter controls under 24 prespecified sensitivity fits: additive
polynomial ridge at degrees 4 and 6, plus degree-6 polynomial ridge with
pairwise control interactions. No fit is classified as
`increment-supported`: every 95% Delta-MSE interval includes zero or lies below
it. Tasks 1, 7, and 8 contain some `residual-dependence-only` fits, showing why
a residual-association test is not used as the verdict by itself. Final
training loss is therefore not a reliable incremental predictor under the
current metadata-floor protocol. This is a baseline result, not evidence about
the checkpoint-derived metrics that remain to be evaluated.

Training loss is a declared B2 baseline variable rather than a primary
checkpoint metric. This metadata-only QA was run across all tasks before any
checkpoint-derived outputs existed. Tasks 6–9 remain protected against metric
development and threshold selection.

## Frozen Sequence

1. Extract a balanced Tasks 1–2 checkpoint pilot and implement weight-only
   metrics against saved HDF5 weights.
2. Freeze metric implementations and compute data-dependent metrics on a fixed
   training subset, including empirical Fisher trace and FIM norm.
3. Run development analyses only on Tasks 1–2.
4. Freeze control choices, thresholds, and plots, then run Tasks 4–5 once.
5. Amend the protocol only for implementation failures, never for unfavorable
   results.
6. Compute Tasks 6–9 once as the protected transfer evaluation.

CEI-R remains exploratory throughout and cannot determine MBE thresholds or
the primary narrative.

The pilot selection is outcome-blind: `select_pilot.py` samples 24 models per
development task using seed 2026 and fails unless every task-specific
hyperparameter level is represented. Its purpose is implementation validation,
not inferential evidence.

The exact pilot contains 48 complete checkpoint pairs (144 archive members),
2.37 GiB compressed and 2.58 GiB extracted. Initialization and final tensors
align by role and shape in every model even where Keras-generated layer names
differ. Exact-SVD spectral norms and nine additional weight/update summaries
are finite for all 48 rows. `out/PILOT_QA.md` records ranges and descriptive
smoke-check correlations without p-values or survival labels.

## Transfer Size

The exact compressed checkpoint total is 18.58 GiB, plus 1.62 GiB of task
datasets. Tasks 1–2 contain 8.16 GiB of checkpoints. A balanced 24-model sample
from each development task is expected to require roughly 2.5 GiB before
accounting for architecture-specific size variation. The complete benchmark is
small enough for staged cloud execution; downloading the original monolithic
archives in full is unnecessary.

Per-task values and immutable archive ETags are recorded in
`archive_sizes.csv`.
