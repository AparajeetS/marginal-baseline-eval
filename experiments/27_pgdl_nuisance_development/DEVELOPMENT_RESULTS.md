# PGDL Nuisance Development Results

## Integrity

- 10,560 planned and observed rows; no duplicate task keys.
- Twenty repetitions per cell and 240 independent groups per fit.
- Zero non-estimable rows.
- All development and generated-output hashes passed.
- No generalization target or checkpoint metric was read.

## Result

Nine of eleven candidates met the exploratory screen across all three
baselines. This high survival count is not confirmation; with twenty
repetitions, the screen is intentionally coarse.

The finalist is `interactions_d2_r01`: degree-2 pairwise-interaction ridge with
penalty 0.1. Across all baselines its worst raw null-support rate was 5% and its
worst effect-0.50 positive-power rate was 70%. The ridge-1 degree-2 candidate
tied those aggregate rates, so the lower-complexity candidate was selected.

The finalist advances to an untouched 100-repetition confirmation with the
original strict Wilson gates. This development result does not authorize any
protected association.
