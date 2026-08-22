# PGDL Transfer Calibration Results

Status: completed negative gate result. Protected PGDL checkpoint-metric and
generalization-target associations remain sealed.

## Integrity

- 4,800 planned and observed rows; 4,800 unique task keys.
- 100 repetitions in every cell and 240 independent model groups per fit.
- Zero non-estimable rows.
- All frozen input and generated-output SHA-256 checks passed.
- The runner read neither generalization-target columns nor checkpoint metrics.

## Frozen Gate

| Baseline | Worst null support, Wilson upper | Worst beta-0.50 positive-power, Wilson lower | Pass |
|---|---:|---:|---:|
| B1 design | 0.2667 | 0.8625 | No |
| B2 plus training loss | 0.1744 | 0.8625 | No |
| B3 plus training state | 0.1863 | 0.8500 | No |

All baselines had 100% estimability. Raw positive support at effect 0.50 was
92%-100%, depending on baseline and reliability. The primary failure was false
support under the heteroskedastic proxy null: the worst raw rate was 18% for B1
at reliability 0.80. The frozen maximum-null Wilson limit was 10%.

## Interpretation

The confirmed 192-group rule transfers with useful simulated power but not with
uniformly controlled false support on the pooled PGDL design. This localizes the
remaining methodological problem to nuisance robustness, especially under
heteroskedastic proxy structure, rather than sample size or estimability alone.

This result does not authorize opening any protected association. Further
development must use new synthetic seeds, preserve this failed packet, and earn
a separately frozen confirmation before any PGDL target-metric analysis.
