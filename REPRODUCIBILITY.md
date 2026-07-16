# Reproducibility

This page explains what can be reproduced locally from saved artifacts and what
requires fresh GPU compute.

## Local Setup

```bash
git clone https://github.com/AparajeetS/marginal-baseline-eval.git
cd marginal-baseline-eval
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
```

Run package tests:

```bash
python -m pytest -q
```

Run the complete CPU-only credibility smoke test:

```powershell
.\reproduce_credibility.ps1
```

On Linux or macOS, use `./reproduce_credibility.sh`. Both scripts write smoke
artifacts to the operating system's temporary directory, leaving the committed
full-calibration evidence unchanged.

The same check can run in the minimal reproduction container:

```bash
docker build -f Dockerfile.reproduction -t mbe-reproduction .
docker run --rm mbe-reproduction
```

Run the CPU-only package demo:

```bash
mbe-eval-demo --bootstrap 200
```

This writes `mbe_demo_report.md` and does not require GPU compute.

## Calibrate The Audit On Known Cases

Run the frozen synthetic calibration suite without GPU compute:

```bash
python experiments/08_protocol_calibration/run_calibration.py
```

This generates null, proxy, nonlinear-confounding, genuine-increment,
Simpson-pooling, and post-treatment-control cases. The command exits nonzero if
the declared audit profiles are not recovered.

The broader comparator, power, and refit-aware inference checks live in
`experiments/10_method_comparison/`. Protocol hashes, the machine-readable
claim ledger, preregistration draft, and external-review packet live in
`experiments/11_credibility_freeze/`.

Regenerate the full inference stress matrix with:

```bash
python experiments/10_method_comparison/run_inference_stress.py \
  --output-dir experiments/10_method_comparison/out
```

This is CPU-only but takes several minutes because every bootstrap draw refits
the nuisance models.

Regenerate manuscript tables with `python paper/build_tables.py`.

An eligible external reviewer can execute the frozen audit with:

```bash
python experiments/12_independent_replication/run_replication_audit.py \
  --reviewer "Full Name" \
  --conflict-statement "No prior contribution; no protected outcomes seen" \
  --output-dir external_replication_report
```

## Reaudit A Published Metric Study

Published studies are ingested through frozen JSON manifests:

```bash
python experiments/09_published_metric_reaudit/run_reaudit.py \
  path/to/study_manifest.json \
  --output-prefix path/to/results/study_reaudit
```

See `experiments/09_published_metric_reaudit/study_manifest.example.json` for
the schema. The runner fails on missing declared controls or duplicate row IDs.

The PGDL external-checkpoint intake and frozen pilot are documented in
`experiments/09_published_metric_reaudit/studies/pgdl2020/README.md`. HDF5
checkpoint extraction requires the optional `h5py` package but no GPU.

## Regenerate MBE Tables From Saved CSVs

The legacy pilot summaries are generated from four committed Kaggle CSV
outputs. Use the explicit paths below so the command reproduces the tracked
tables rather than accidentally auditing an empty directory:

```bash
python experiments/07_jmlr_scale/analyze_jmlr_scale.py \
  experiments/07_jmlr_scale/kaggle_downloads/image_v2/jmlr_scale_image_results.csv \
  experiments/07_jmlr_scale/kaggle_downloads/confirm_image/jmlr_confirm_image_results.csv \
  experiments/07_jmlr_scale/kaggle_downloads/text_v2/jmlr_scale_text_results.csv \
  experiments/07_jmlr_scale/kaggle_downloads/confirm_text/jmlr_confirm_text_results.csv \
  --out-prefix experiments/07_jmlr_scale/jmlr_full_confirmed_680_audit
```

For the strict validation-loss control audit:

```bash
python experiments/07_jmlr_scale/analyze_jmlr_scale.py \
  experiments/07_jmlr_scale/kaggle_downloads/image_v2/jmlr_scale_image_results.csv \
  experiments/07_jmlr_scale/kaggle_downloads/confirm_image/jmlr_confirm_image_results.csv \
  experiments/07_jmlr_scale/kaggle_downloads/text_v2/jmlr_scale_text_results.csv \
  experiments/07_jmlr_scale/kaggle_downloads/confirm_text/jmlr_confirm_text_results.csv \
  --covars lr,wd,dropout,optimizer,arch,task,seed,val_loss \
  --out-prefix experiments/07_jmlr_scale/jmlr_full_confirmed_680_strict_loss_mbe
```

Expected headline outputs include:

- `experiments/07_jmlr_scale/jmlr_image_combined_480_audit_summary.md`
- `experiments/07_jmlr_scale/jmlr_image_combined_480_strict_loss_mbe_summary.md`
- `experiments/07_jmlr_scale/jmlr_text_combined_200_audit_summary.md`
- `experiments/07_jmlr_scale/jmlr_text_combined_200_strict_loss_mbe_summary.md`
- `experiments/07_jmlr_scale/jmlr_full_confirmed_680_audit_summary.md`
- `experiments/07_jmlr_scale/jmlr_full_confirmed_680_strict_loss_mbe_summary.md`

The key raw result artifacts and SHA256 hashes are listed in
[`experiments/07_jmlr_scale/ARTIFACTS.md`](experiments/07_jmlr_scale/ARTIFACTS.md).
These commands reproduce the v1 summaries; they do not repair the scientific
validity limitations described in the evidence ledger.

## CPU-Only Uncertainty And Threshold Sensitivity

Bootstrap confidence intervals and threshold-sensitivity counts can be
regenerated from saved CSVs without GPU compute:

```bash
python experiments/07_jmlr_scale/no_compute_uncertainty.py --bootstrap 200
```

Expected outputs:

- `experiments/07_jmlr_scale/no_compute_outputs/headline_bootstrap_ci.csv`
- `experiments/07_jmlr_scale/no_compute_outputs/threshold_sensitivity.csv`
- `experiments/07_jmlr_scale/no_compute_outputs/NO_COMPUTE_UNCERTAINTY.md`

## Public Notebook

The public Kaggle walkthrough is:

https://www.kaggle.com/code/aparajeetshadangi/audit-ml-training-metrics-with-mbe

Its source is tracked at:

```text
kaggle/mbe_metric_audit/how_to_audit_ml_training_metrics_mbe.ipynb
```

Push a new notebook version with:

```bash
python -m kaggle kernels push -p kaggle\mbe_metric_audit
```

## GPU-Required Training Runs

The package and saved-analysis scripts do not require GPU. Fresh model-training
replications do.

Current large-scale training scripts live in:

```text
experiments/07_jmlr_scale/
```

Representative Kaggle push commands:

```bash
python -m kaggle kernels push -p experiments\07_jmlr_scale
```

Or use the helper scripts:

```powershell
.\experiments\07_jmlr_scale\push_image.ps1
.\experiments\07_jmlr_scale\push_text.ps1
```

The legacy pilot pool used:

- 480 image models: CNN, ResNet, ViT, WideResNet on CIFAR-10.
- 200 text-model rows from an invalid causal-LM setup, retained only for
  provenance and software regression checks.
- Default v1 controls: `lr`, `wd`, `dropout`, `optimizer`, `arch`, `task`, `seed`.
- Strict MBE controls: default controls plus `val_loss`.

## Evidence Files

Use these files when checking the research claims:

- `SUPPORTING_EVIDENCE.md`: run-by-run interpretation and washout lists.
- `RUN_PROGRESS_LOG_2026-06-28.md`: run ledger for the current large-scale pass.
- `experiments/07_jmlr_scale/ARTIFACTS.md`: artifact hashes and raw CSV references.
- `experiments/06_independent_audit/artifact_audit_report.md`: independent audit of older artifacts.

## Compute Gap

The repository is intentionally usable without fresh compute. Submission-grade
evidence requires both corrected methods and replication scale. The active
sequence is defined in [`docs/JMLR_MILESTONE_ROADMAP.md`](docs/JMLR_MILESTONE_ROADMAP.md):

1. freeze the MBE 2.0 protocol and claim ledger;
2. validate the implementation on synthetic controls and public corpora;
3. run corrected image and causally masked text pilots;
4. launch locked holdout replications only after the pilot gate passes;
5. publish raw artifacts, hashes, uncertainty, and all planned analyses.
