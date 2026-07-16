# Synthetic Protocol Calibration

This work package tests MBE on data-generating processes where the reason a
metric appears predictive is known. It is a calibration of the audit, not
evidence about real neural-network metrics.

Run from the repository root:

```bash
python experiments/08_protocol_calibration/run_calibration.py
```

The frozen scenarios are:

| Scenario | Ground-truth role |
|---|---|
| `null_metric` | independent noise |
| `linear_proxy` | noisy copy of an observed baseline |
| `nonlinear_proxy` | U-shaped baseline proxy missed by linear partial ranks |
| `genuine_increment` | metric contains target information beyond the baseline |
| `heteroskedastic_null` | conditionally independent errors with shared baseline-dependent variance |
| `clustered_null` | independent configuration shocks with repeated rows per configuration |
| `simpson_increment` | environment pooling masks a within-environment increment |
| `post_treatment_control` | a mediator removes the total effect by construction |

The command writes the generated ledger, a machine-readable summary, and a
Markdown report under `out/`. A nonzero exit status means at least one frozen
calibration profile failed.

The cross-fitted implementation uses a frozen degree-six training-fold
polynomial nuisance model and configuration-group folds. The deliberately rich
basis is required to recover the U-shaped proxy after rank transformation. This
is the first reproducible MBE 2.0 reference path, not the final model-family
comparison specified in the research program.

## Repeated Calibration

The one-shot profiles are software checks. Error and power evidence comes from
the repeated grid:

```bash
python experiments/08_protocol_calibration/run_monte_carlo.py \
  --sample-sizes 150,300,600 \
  --degrees 2,4,6 \
  --repetitions 100 \
  --permutations 199 \
  --bootstrap 499
```

The joint increment decision requires both a residual permutation rejection
and a 95% Delta-MSE interval entirely above zero. Reports retain the residual
test rate separately so nuisance misspecification remains visible even when the
joint decision abstains.

This joint classifier is retained as a historical calibration and secondary
diagnostic. The protected MBE 2.0 primary rule is the full-refit predictive
interval with agreement across frozen nuisance families; see
`docs/STATISTICAL_ESTIMAND_AND_INFERENCE.md`.

`out/MONTE_CARLO_CALIBRATION.md` shows that low-degree nuisance adjustment can
be badly anti-conservative for proxy cases. It is retained as a documented
failure and sensitivity condition, not an acceptable primary default.

## PGDL Semi-Synthetic Calibration

The second repeated study preserves the actual Tasks 1-2 hyperparameter
geometry and sample sizes while injecting null, proxy, genuine-increment, and
opposite-sign task-specialist metrics:

```bash
python experiments/08_protocol_calibration/run_pgdl_semisynthetic.py \
  experiments/09_published_metric_reaudit/data/pgdl_model_ledger.csv \
  experiments/09_published_metric_reaudit/studies/pgdl2020/metric_plan.json \
  --degrees 2,4,6 \
  --repetitions 100 \
  --permutations 199 \
  --bootstrap 499 \
  --output-dir experiments/08_protocol_calibration/out
```

This uses development-task metadata only. It does not inspect validation or
protected-holdout checkpoint metrics. The balanced pooled specialist case has
real but opposite task-specific effects and is a heterogeneity diagnostic, not
a conditional-null test.

An interaction-capable sensitivity run uses the optional dependency:

```bash
pip install -e ".[flexible]"
python experiments/08_protocol_calibration/run_monte_carlo.py \
  --nuisance-model extra_trees --degrees 1
```

No nuisance learner is selected because it gives the most favorable real
metric result. Learner eligibility and disagreement rules must be frozen from
these known-ground-truth calibrations before PGDL metric inference.
