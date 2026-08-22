# Nuisance-Complexity Ablation

This table combines two known-truth calibration axes. The generic axis
tests null/proxy control and signal recovery. The observed-design axis
tests full-refit power in the exact 36-configuration causal-text
geometry. It is not a real-metric outcome comparison.

| Degree | Family | Generic max null/proxy joint | Generic min signal joint | Observed beta=0 | beta=0.2 | beta=0.3 | beta=0.5 | Strict beta=0.5 |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | additive | 100.0% | 99.0% | 0.0% | 86.0% | 98.4% | 100.0% | 4.6% |
| 1 | interactions | 100.0% | 98.0% | 0.0% | 0.0% | 0.4% | 4.6% | 4.6% |
| 2 | additive | 100.0% | 97.0% | 0.0% | 65.4% | 92.2% | 99.3% | 1.6% |
| 2 | interactions | 100.0% | 98.0% | 0.0% | 0.0% | 0.1% | 1.6% | 1.6% |
| 3 | additive | 100.0% | 100.0% | 0.0% | 58.4% | 90.2% | 98.7% | 1.1% |
| 3 | interactions | 100.0% | 99.0% | 0.0% | 0.0% | 0.1% | 1.1% | 1.1% |
| 4 | additive | 17.0% | 100.0% | 0.0% | 49.0% | 87.0% | 98.2% | 1.0% |
| 4 | interactions | 5.0% | 100.0% | 0.0% | 0.0% | 0.2% | 1.0% | 1.0% |
| 6 | additive | 0.0% | 99.0% | 0.0% | 42.1% | 82.8% | 98.3% | 1.0% |
| 6 | interactions | 3.0% | 99.0% | 0.0% | 0.0% | 0.2% | 1.0% | 1.0% |

## Reading The Result

- Degrees 1-3 recover observed-design signal but reach 100% false
  support in at least one generic null/proxy cell.
- Degree 4 reduces the worst generic false support to 17% for the
  additive family and 5% for the interaction family.
- Degree 6 reduces the worst generic false support to 0% and 3%,
  respectively, while retaining 98.3% additive power at beta=0.5.
- The interaction family has only 1.0%-4.6% observed-design power
  at beta=0.5 across every tested degree.
- Consequently, mandatory two-family agreement has at most 4.6%
  large-effect power in this 36-configuration design.

There is no degree that makes the current universal two-family
consensus both proxy-safe and adequately powered here. MBE must
treat nuisance-family eligibility as design-specific calibration
and abstain when no preregistered family passes both control and
power gates. Choosing the most favorable degree after real-metric
inspection is not permitted.
