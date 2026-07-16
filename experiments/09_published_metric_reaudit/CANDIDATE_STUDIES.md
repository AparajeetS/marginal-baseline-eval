# Candidate Study Intake

This queue prioritizes studies with public run-level metadata or checkpoints.
Inclusion means that a study is relevant and potentially reproducible, not that
its conclusions are suspected to be wrong.

| Priority | Study | Why it matters | Intake status |
|---:|---|---|---|
| 1 | Jiang et al. (2020), *Fantastic Generalization Measures and Where to Find Them* | Large model population, many generalization measures, and conditional rank evaluation | No public run-level artifact located; intake blocked without reconstruction |
| 2 | Dziugaite et al. (2020), *In Search of Robust Measures of Generalization* | Environment interventions and robust sign-error provide a direct comparison estimand | Figure 1 source statistic and MBE reaudit complete |
| 3 | Predicting Generalization in Deep Learning competition / PGDL corpus | Independent public environments and a benchmark-oriented evaluation design | 550-model metadata intake complete; checkpoint metric extraction frozen |
| 4 | Jiang et al. (2019), *Predicting the Generalization Gap in Deep Networks with Margin Distributions* | Influential metric claim with a concrete intended direction | Run-level artifact availability required |

## Acceptance Criteria

A study enters the benchmark only when:

1. the primary paper and official artifact are identified;
2. licensing permits redistribution or a download script;
3. run IDs, targets, environments, and hyperparameters can be reconstructed;
4. the published headline score can be reproduced within a declared tolerance;
5. unavailable metrics and checkpoints are reported rather than imputed;
6. a study manifest is committed before the MBE result is interpreted.

Primary sources:

- https://openreview.net/forum?id=SJgIPJBFvH
- https://proceedings.neurips.cc/paper/2020/hash/86d7c8a08b4aaa1bc7c599473f5dddda-Abstract.html
- https://openreview.net/forum?id=HJlQfnCqKX
