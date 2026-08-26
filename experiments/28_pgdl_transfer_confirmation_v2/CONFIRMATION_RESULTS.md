# PGDL Transfer Confirmation V2 Results

Status: completed; global gate failed. Protected PGDL target-metric
associations remain sealed.

## Integrity

- 4,800 planned and observed rows; no duplicate task keys.
- 100 repetitions per cell; 240 independent groups per fit.
- Zero non-estimable rows.
- All frozen and generated-output hashes passed.
- Manifested method: degree-2 interaction ridge, penalty 0.1.
- No generalization target or checkpoint metric was read.

The first infrastructure-invalid attempt and its spawn-safe recovery are
recorded in `RECOVERY_PROVENANCE.md`; frozen hashes preserve its identity, and
the invalid raw bundle remains available from Git history.

## Frozen Gate

| Baseline | Worst null Wilson upper | Worst beta-0.50 power Wilson lower | Pass |
|---|---:|---:|---:|
| B1 design | 0.0545 | 0.5322 | Yes |
| B2 plus training loss | 0.0545 | 0.5628 | Yes |
| B3 plus training state | 0.0845 | 0.4920 | No |

Null control passed for all three baselines. B3 failed the power gate: at
reliability 0.30, 59 of 100 effect-0.50 repetitions had positive support,
giving a 95% Wilson lower bound of 0.4920 against the frozen 0.5000 minimum.

## Interpretation

Reduced nuisance shrinkage repaired the false-support failure observed in
experiment 26 and retained moderate-to-high power, but the all-baseline gate
was missed by a binding prespecified criterion. This is evidence of a real
calibration-power frontier, not authorization to round a near miss upward.

The next step is an estimand-aware comparator benchmark and further method
development on new known-truth data. Any later candidate requires another
disjoint confirmation before protected associations can be opened.
