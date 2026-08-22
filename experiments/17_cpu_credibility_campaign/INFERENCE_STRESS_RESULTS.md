# Corrected Inference Stress: Completed Results

The amended eight-shard campaign completed successfully after removing the
invalid `n = 72` cell. The retained grid used sample sizes 100, 150, 200, and
300, 200 pooled repetitions per sample-by-scenario-by-nuisance cell, 199
full-refit bootstrap draws, and 199 residual permutations. The separate
block-null study used 2,000 repetitions and 999 permutations per structure.

## Integrity

- eight of eight shards exited with status zero;
- 8,000 refit-ledger rows and 8,000 block-ledger rows;
- exactly 200 refit repetitions per cell and 2,000 repetitions per block
  structure;
- zero duplicate refit or block keys;
- all frozen scenarios, sample sizes, and nuisance families retained.

## Full-Refit Predictive Decision

Across 6,400 null/proxy rows, the predictive interval supported an increment
16 times (0.25%) and the joint classification supported an increment eight
times (0.125%). The largest cell-level rates were 3.0% predictive support and
2.5% joint support.

Across 1,600 genuine-increment rows, predictive support was 1,600/1,600
(100%). Joint support was 1,597/1,600 (99.81%); the three misses occurred at
`n = 100`.

These results support the full-refit predictive interval in the named
known-truth designs. They are finite calibration evidence, not a universal
coverage guarantee.

## Residual-Permutation Diagnostic

| Null structure | Rejections | Rate | Wilson 95% interval |
|---|---:|---:|---:|
| Clustered | 139/2,000 | 6.95% | [5.92%, 8.15%] |
| Heteroskedastic | 106/2,000 | 5.30% | [4.40%, 6.37%] |
| Homoskedastic | 141/2,000 | 7.05% | [6.01%, 8.26%] |
| Unequal blocks | 145/2,000 | 7.25% | [6.19%, 8.47%] |

The expanded study does not resolve the earlier anti-conservative
block-permutation result. Three structures have Wilson intervals entirely
above the nominal 5% level; only the heteroskedastic interval includes 5%.
Residual permutation therefore remains a secondary diagnostic and cannot gate
the primary MBE decision.

The pooled ledgers and machine-readable summaries are in
[`out/pooled/`](out/pooled/).
