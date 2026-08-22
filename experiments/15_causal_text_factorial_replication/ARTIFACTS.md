# Causal-Text Factorial Sequential Replication: Artifact Record

Status: completed corrected training artifact; no metric passed the frozen
within-environment refit-increment rule.

## Frozen Execution

- 180 / 180 completed valid WikiText-2 causal-LM rows; zero error rows.
- 2 model sizes x 18 configurations x 5 seeds, for 36 independent
  configuration interventions.
- 6,000 updates per run and three deterministic metric batches per model.
- Causal prefix-logit perturbation passed (`0.0` difference); the unmasked
  negative control changed logits by `3.1988818645` as intended.
- Kaggle elapsed time: 9.185 P100-hours.

## Frozen Analysis Result

The configuration-blocked analysis used 199 full refit bootstraps for every
metric, baseline, and nuisance family. The protocol requires a positive lower
refit interval for both degree-six ridge families before labeling a metric as
increment-supported. No metric met that criterion for B1 (design), B2
(training-state), or B3 (validation) baselines. The full-run-ID random control
also received `no_consensus_increment` at every baseline.

This is a within-WikiText-2 result. It shows that raw and residual associations
can disappear under the frozen stability rule in this environment; it does not
establish a universal metric ranking, a cross-task transport result, or a
selector claim.

`fim_norm` in this artifact is normalized FIM effective rank
(`fim_erank / diagnostic_batch_size`), so it is a monotone rescaling of
`fim_erank` for this fixed diagnostic design. The two are not independent
metric tests and are reported separately only for continuity with the frozen
metric list.

## Committed Artifact Set

| Artifact | Role | SHA-256 |
|---|---|---|
| `mbe2_causal_text_factorial_replication.py` | executed factorial source | `c1afddee8e4becbc29799a3dd96a9a39e44bcbb57a8278a13fef284585a69429` |
| `analyze_replication.py` | frozen analysis and report generator | `7749fd8765027cdf31d1eda520806d0deee79bc5a47551425aca1e8bcb8cf98c` |
| `kaggle_downloads/v1/mbe2_causal_text_factorial_replication.csv` | raw 180-row ledger | `1bffd89562923d701141e502988f7b62072ee312786dc348f4861715328b5ef6` |
| `kaggle_downloads/v1/mbe2_causal_text_factorial_replication_manifest.json` | frozen grid, split hashes, and execution metadata | `9aad811c1c3f624dd78bf895e2e0aee7ff2a2c087f4a53128b81d2c5ee96bd91` |
| `kaggle_downloads/v1/causal_mask_leakage_test.json` | causal and unmasked-control behavior check | `a5bd3d189b1423be19c3c86bebaafdb6d4452563777985b5516aff6e03fe26cc` |
| `out_primary_199/INITIAL_REPORT.md` | scope, integrity, raw associations, stability, and consensus | `6aca9608cdd6fd3840db5ea2fb59fc1a717266959a5b627d19c76b884d816537` |
| `out_primary_199/refit_analysis.csv` | per-metric, per-baseline, per-nuisance-family refit results | `1693a8819e04e3a39b22ca500b024ba2704830367d0930b3c4f41409f801d326` |
| `out_primary_199/refit_consensus.csv` | frozen joint-rule verdicts | `45f5afc5725dc9a35e8713cbf8c5ea0792c0a05abab503b62fdc3b8b09882fc5` |

The downloaded WikiText source copies and transient Kaggle log are intentionally
excluded from version control. They are not needed to inspect the ledger or
reproduce the analysis from the committed CSV and manifest.

## Reproduce The Report

```bash
python experiments/15_causal_text_factorial_replication/analyze_replication.py \
  experiments/15_causal_text_factorial_replication/kaggle_downloads/v1/mbe2_causal_text_factorial_replication.csv \
  experiments/15_causal_text_factorial_replication/kaggle_downloads/v1/mbe2_causal_text_factorial_replication_manifest.json \
  --out-dir experiments/15_causal_text_factorial_replication/out_primary_199 \
  --refit-bootstrap 199
```

The script writes an integrity record, configuration-mean raw associations,
metric-batch stability, descriptive cross-fit diagnostics, per-family refit
results, and the frozen consensus table.
