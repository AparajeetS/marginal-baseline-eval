# Orthogonal Score 192-Group Confirmation

Frozen after experiment 22 development and before any confirmation output or
protected metric association is inspected.

## Scope

This confirmation tests one sample-size-specific conditional-rank rule at 192
independent configuration groups. It does not test or authorize its use at 24,
48, or 96 groups.

## Fixed Rule

- cross-fitted metric and target ranks, adjusted separately for controls;
- product of configuration-mean residuals;
- degree-4 polynomial ridge with pairwise control interactions;
- ridge penalty 10;
- five folds assigned by configuration group;
- two-sided studentized Rademacher multiplier inference;
- 4,999 multiplier draws;
- support threshold 0.001.

## Fixed Truth Grid

Use two 192-group geometries: four independent copies of the 48-group image
factorial and eight independent copies of the 24-group text factorial. Panel
seeds are nested within a geometry but disjoint from all development protocol
namespaces. Retain B1 design, B2 training-state, and B3 validation baselines;
ICC 0.30 and 0.80; all five null families; and positive effects 0.20, 0.35,
and 0.50. Run 100 repetitions per cell.

## Gate

For every geometry and baseline pair:

1. minimum estimability is at least 98%;
2. the largest null-support Wilson 95% upper bound is at most 10%;
3. the smallest positive-power Wilson 95% lower bound at effect 0.50 is at
   least 50%.

Global confirmation passes only if all six geometry-baseline pairs pass. No
pair may be dropped after inspection.

## Consequence

A global pass establishes synthetic known-truth eligibility for external
datasets with at least 192 defensible independent units and comparable control
complexity. It does not open the protected 24/48-group image or text
associations. PGDL Task 6 still requires its own frozen intake validation,
metric extraction, multiplicity rule, and one-time external analysis.

Failure preserves abstention and becomes part of the paper.
