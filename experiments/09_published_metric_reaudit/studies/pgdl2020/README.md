# PGDL External Benchmark Intake

The Predicting Generalization in Deep Learning corpus is the external
checkpoint benchmark for the next MBE phase.

- Official repository: <https://github.com/google-research/google-research/tree/master/pgdl>
- Paper: <https://arxiv.org/abs/2012.07976>
- License: Apache-2.0 for checkpoints and metadata; bundled datasets retain
  their original licenses.

## Selective Intake

The three official archives total 21.7 GB. `inspect_remote_zip.py` uses HTTP
range requests to read their ZIP directories and extract only the eight
`model_configs.json` ledgers. No checkpoints or training datasets were
downloaded during intake.

| Competition phase | Tasks | Models | Role |
|---|---|---:|---|
| Public | 1, 2 | 150 | Development |
| Public leaderboard | 4, 5 | 160 | Validation |
| Private leaderboard | 6, 7, 8, 9 | 240 | Protected transfer holdout |

The 550 models include train/test accuracy and loss plus every varying
hyperparameter. The archives do not contain precomputed complexity measures;
those must be calculated from checkpoints under the frozen plan in
`metric_plan.json`.

## Prepare Metadata

```bash
python experiments/09_published_metric_reaudit/prepare_pgdl.py \
  experiments/09_published_metric_reaudit/data \
  experiments/09_published_metric_reaudit/data/pgdl_model_ledger.csv
```

The unified ledger defines accuracy and loss generalization gaps and preserves
the original task-specific hyperparameters. It remains ignored until metric
extraction is complete; preparation code and source hashes are public.

`out/metadata_floor.csv` and `out/metadata_floor.md` record the pre-checkpoint
hyperparameter and training-loss floor. `INTAKE_RESULTS.md` records the intake
findings and frozen execution order.

## Checkpoint Pilot

`pilot_selection.csv` freezes an outcome-blind sample of 24 models from each
development task. Download only those checkpoint members, then extract and
validate the weight-only metrics:

```bash
python experiments/09_published_metric_reaudit/studies/pgdl2020/extract_pilot.py \
  experiments/09_published_metric_reaudit/studies/pgdl2020/pilot_selection.csv \
  --output-dir experiments/09_published_metric_reaudit/data/pgdl_pilot
pip install -e ".[checkpoint]"
python experiments/09_published_metric_reaudit/studies/pgdl2020/extract_weight_metrics.py \
  experiments/09_published_metric_reaudit/data/pgdl_pilot \
  experiments/09_published_metric_reaudit/studies/pgdl2020/pilot_selection.csv \
  experiments/09_published_metric_reaudit/data/pgdl_model_ledger.csv \
  experiments/09_published_metric_reaudit/studies/pgdl2020/out/pilot_weight_metrics.csv
python experiments/09_published_metric_reaudit/studies/pgdl2020/validate_pilot.py \
  experiments/09_published_metric_reaudit/studies/pgdl2020/out/pilot_weight_metrics.csv \
  --report experiments/09_published_metric_reaudit/studies/pgdl2020/out/PILOT_QA.md \
  --summary experiments/09_published_metric_reaudit/studies/pgdl2020/out/pilot_metric_summary.csv
```

The pilot checks extraction and numerical behavior only. Its descriptive
correlations are not used to classify metric survival or washout.

## Interpretation Boundary

PGDL is a successor benchmark, not the unreleased Jiang et al. (2020) model
population. Results must be cited as PGDL results. Holdout labels already exist
in public metadata, but the protocol treats Tasks 6–9 as protected: analysis
code and thresholds are frozen using Tasks 1–5 before holdout metric outputs are
inspected.
