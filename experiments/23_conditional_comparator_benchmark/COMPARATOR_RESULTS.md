# Conditional Comparator Benchmark Results

Status: completed known-truth benchmark. No protected association was read.

## Integrity

- 9,600 paired synthetic datasets and 153,600 method rows.
- Exactly 100 repetitions per method cell; no duplicate keys.
- Seven methods were estimable in all 19,200 assigned rows each.
- CRT retained 19,200 principled abstentions because no validated conditional
  sampler was available.
- All frozen-input and generated-output SHA-256 checks passed.
- Official KCI dependencies were pinned at `causal-learn==0.1.4.8` and
  `momentchi2==0.1.8`.

## Worst-Cell Calibration And Power

| Method | Pooled synthetic-null support | Worst true-null cell | Median beta-0.50 power | Worst beta-0.50 power |
|---|---:|---:|---:|---:|
| MBE cross-fit joint rule | 0.017 | 0.080 | 0.070 | 0.010 |
| Orthogonal wild score | 0.022 | 0.080 | 0.130 | 0.030 |
| WGCM.est | 0.127 | 0.240 | 0.220 | 0.150 |
| Residual Spearman | 0.248 | 0.390 | 0.615 | 0.340 |
| GCM student | 0.269 | 0.390 | 0.610 | 0.370 |
| KCI | 0.390 | 0.590 | 0.620 | 0.380 |
| Raw Spearman | 0.511 | 0.910 | 0.955 | 0.790 |

True-null cells include the named synthetic nulls and every random
negative-control cell. Rates are support frequencies, not directly comparable
p-values: the orthogonal score uses `p <= 0.001`, while the other estimable
tests use `alpha=0.05` or MBE's joint 0.05 rule.

## Interpretation

No tested procedure simultaneously supplied strict worst-cell calibration and
useful worst-cell power at 24 and 48 independent configurations. Raw and broad
conditional-dependence procedures appeared powerful but were severely
anti-conservative in some nuisance or negative-control cells. MBE had the
lowest pooled false support relative to its 5% rule but was strongly
underpowered under its joint predictive-gain criterion. The orthogonal score
also had low absolute false support, yet 2.2% pooled support is
anti-conservative relative to its 0.1% nominal threshold.

This is evidence for an estimand- and sample-size-aware audit with explicit
abstention. It is not evidence that MBE dominates conditional-independence
tests, and it is not a universal ranking of statistical methods. GCM and WGCM
test residual covariance functionals, KCI tests broader conditional
dependence, and MBE tests learner-relative predictive gain.

Primary method references are the Shah-Peters GCM paper, the JMLR WGCM paper,
and the Zhang-Peters-Janzing-Schoelkopf KCI paper linked in the frozen
preregistration.
