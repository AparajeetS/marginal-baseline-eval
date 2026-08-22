# Degree-2 Observed-Design Sensitivity

The post-primary degree-2 sensitivity completed all 4,500 simulated cells and
9,000 nuisance-family rows. All rows were estimable, every cell had exactly
two nuisance-family results, and the frozen manifest matched the planned 100
repetitions, 199 refits, 99 permutations, and seed `20260729`.

## Pooled Predictive Support

| Degree | Nuisance family | beta=0.0 | beta=0.1 | beta=0.2 | beta=0.3 | beta=0.5 |
|---:|---|---:|---:|---:|---:|---:|
| 2 | Additive polynomial ridge | 0.00% | 8.00% | 65.44% | 92.22% | 99.33% |
| 2 | Polynomial ridge with interactions | 0.00% | 0.00% | 0.00% | 0.11% | 1.56% |
| 6 | Additive polynomial ridge | 0.00% | 2.11% | 42.11% | 82.78% | 98.33% |
| 6 | Polynomial ridge with interactions | 0.00% | 0.00% | 0.00% | 0.22% | 1.00% |

Rates pool the equally sized reliability-tier and B1/B2/B3 cells. The strict
two-family consensus at degree 2 was 0% through `beta = 0.2`, 0.11% at
`beta = 0.3`, and 1.56% at `beta = 0.5`. The degree-6 consensus rates were
0%, 0.22%, and 1.00% for those same effects.

## Interpretation

Reducing polynomial degree improved the additive learner's moderate-effect
power but did not rescue the interaction learner or the mandatory consensus
rule. The interaction veto is therefore not explained by degree six alone. It
is more consistent with the interaction family being too data-hungry or
unstable for only 36 independent configurations.

This sensitivity does not replace the degree-6 primary result and does not
justify selecting degree 2 for the real-metric analysis. Degree 2 failed
nonlinear-proxy controls elsewhere. The full degrees 1-6 known-truth
complexity map must be interpreted before any nuisance-eligibility rule is
revised.

The transferred archive
`mbe_degree2_complete_20260729_1629.tar.gz` had SHA-256
`19d36c57d9bb32dfaabb41996a6aff2011dd5bde6191e0cad6f2756bae291201`.
