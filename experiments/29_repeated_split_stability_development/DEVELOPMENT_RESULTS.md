# Repeated-Split Stability Development Results

Status: completed development screen. No candidate advances to confirmation and
no protected association was read or authorized.

## Integrity

- 10,080 planned and observed rows; 504 cells with exactly 20 repetitions.
- Zero duplicate task keys, zero non-estimable rows, and 100% estimability.
- Frozen protocol, runner, and estimator hashes all match.
- The output manifest records no generalization-target or checkpoint-metric
  reads, and the diagnostic records no opening authorization.

## Result

The repeated-split intersection rule did not resolve the 24/48-configuration
calibration-power problem. No degree, alpha, or repeat-count candidate met the
development requirement of at most 5% support in every known-null/proxy cell
and at least 50% positive support in every effect-0.50 cell.

| Candidate | Worst null/proxy support | Weakest effect-0.50 positive support |
|---|---:|---:|
| `d2_r01_repeat3_a05` | 15% | 25% |
| `d2_r01_repeat3_a01` | 10% | 5% |
| `d2_r01_repeat5_a05` | 25% | 10% |
| `d4_r01_repeat3_a05` | 20% | 15% |
| `d4_r01_repeat3_a01` | 5% | 5% |
| `d4_r01_repeat5_a05` | 15% | 15% |

The most conservative candidate, degree four with three splits at alpha 0.01,
reached the null ceiling but retained only 5% minimum effect-0.50 power. The
higher-power candidates remained anti-conservative in at least one known-null
cell. This is a development rejection, not evidence for adjusting the
thresholds after the fact.

## Consequence

The experiment rules out this simple split-stability intersection family as a
primary 24/48-configuration opening rule under the tested known-truth
geometries. Future work must use fresh development data and a substantively
different estimator, calibration device, or sample-size-aware abstention
policy. Experiments 19, 20, 24, and the PGDL checkpoint associations remain
sealed.
