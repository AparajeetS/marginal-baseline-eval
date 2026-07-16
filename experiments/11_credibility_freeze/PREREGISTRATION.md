# MBE PGDL Development Freeze

Status: ready for timestamping; protected checkpoint-derived outcomes have not
been used to alter this protocol.

## Primary Estimand

For each task and metric, estimate learner-relative out-of-fold improvement in
rank-target mean squared error beyond the declared baseline ladder. Residual
rank dependence is a separate diagnostic and cannot establish increment alone.

## Primary Decision

`increment-supported` requires a full-refit 95% Delta-MSE interval above zero
for both the eligible additive degree-6 and degree-6 pairwise-interaction ridge
nuisance families. Disagreement produces abstention. Residual permutation is a
secondary diagnostic because clustered-null calibration remains mildly
anti-conservative.

## Development And Holdout

- Tasks 1-2: implementation and development only.
- Tasks 4-5: validation, opened once after the freeze manifest is committed.
- Tasks 6-9: protected transfer, opened once after validation reporting.

No threshold, metric implementation, nuisance family, or plot may be changed
because of protected-task favorability. Necessary implementation amendments
must be dated, justified, and applied without inspecting protected outcomes.

## Uncertainty

Primary uncertainty resamples configuration groups, rebuilds grouped folds,
and refits all nuisance models. Within-task residual permutation is reported as
a diagnostic; pooled sensitivity, if shown, permutes within task blocks.

## Comparators

Raw Spearman, Kendall tau-b, partial Spearman, Jiang granulated Kendall, Jiang
normalized CMI, and the source-faithful robust sign-error statistic are reported
under their own estimands. No comparator is forced into an MBE survival label.

## Abstention

Abstain when independent units are below 30, predictive intervals are missing,
eligible nuisance models disagree, refit-aware uncertainty fails, or the target
and controls do not match a frozen metric claim card.

## Integrity

`freeze_manifest.json` records SHA-256 hashes for the implementation, metric
plan, split, and protocol. `claim_ledger.json` is machine checked and blocked or
withdrawn claims remain visible.
