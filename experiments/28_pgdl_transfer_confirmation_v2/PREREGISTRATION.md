# PGDL Transfer Confirmation V2

Frozen after experiment 27 development and before any confirmation outcome or
protected target-metric association is inspected.

## Selected Rule

- Pooled PGDL Tasks 6-9 geometry: 240 independent models.
- B1 design, B2 plus training loss, and B3 plus training state.
- Fold-local rank transforms and five-fold grouped cross-fitting.
- Degree-2 polynomial ridge with pairwise interactions and ridge penalty 0.1.
- Product of configuration-mean metric and target residuals.
- Studentized Rademacher inference with 4,999 draws.
- Two-sided support threshold `p <= 0.001`; positive power also requires a
  positive score.

The finalist was selected from experiment 27 by full estimability, worst raw
null support no greater than 5%, greatest worst effect-0.50 power, and then
lower prespecified complexity rank to resolve the tie.

## Untouched Confirmation Grid

Use a new protocol namespace and 100 repetitions for every combination of all
three baselines, five null families, reliability 0.30/0.80, and interaction
increments 0.20/0.35/0.50. The synthetic generator uses only allowed design
metadata and reads no generalization target or checkpoint metric.

## Gate

Every baseline must have at least 98% estimability, maximum null-support Wilson
95% upper bound at most 10%, and minimum effect-0.50 positive-power Wilson 95%
lower bound at least 50%. Global pass requires all three baselines.

A pass permits freezing a separate pooled PGDL real-analysis packet. It does
not itself authorize metric extraction or association inspection. Failure
preserves the holdout and returns the method to development or abstention.
