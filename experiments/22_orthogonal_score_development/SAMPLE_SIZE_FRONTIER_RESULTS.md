# Sample-Size Frontier Results

Status: completed development evidence. This result selected a rule for fresh
confirmation but does not itself authorize protected analysis.

## Integrity

- 16,800 of 16,800 planned cells completed.
- The ledger has unique keys, 50 repetitions per cell, and zero error rows.
- All hashes match and exact sources are retained under `out_frontier_50/`.
- A Windows checkpoint-replace lock interrupted the first process at 15,925
  rows. The complete checkpoint was retained and the identical remaining 875
  tasks resumed after adding retry-only checkpoint logic.

## Result

At 24 and 48 independent groups, no threshold provided both strict null control
and useful worst-cell power. At 96 groups, power improved substantially but
worst proxy-null support remained too high or uncertain.

At 192 groups, the strong-ridge interaction score at two-sided threshold 0.001
showed a different regime. Across both factorial geometries and B1-B3:

- worst raw null support was 0-4%;
- weakest effect-0.50 positive power was 88-100%;
- all cells were estimable.

Fifty repetitions are insufficient for the final Wilson gate whenever even one
false support occurs, so these results select rather than confirm the rule.

## Selected Confirmation Rule

- at least 192 independent groups;
- product of configuration-mean cross-fitted rank residuals;
- degree-4 polynomial ridge with pairwise interactions;
- ridge penalty 10;
- grouped five-fold cross-fitting;
- 4,999 Rademacher multiplier draws;
- two-sided support threshold 0.001;
- 100 fresh repetitions in every known-truth cell.

The rule must pass every design and baseline cell. It cannot authorize the
existing 24/48-group GPU associations. A pass makes it eligible for a separate
external evaluation with at least 192 verified independent units after
design-matched calibration and structural validation.
