# Corrected Causal-Text Factorial v1: Artifact Record

Status: completed corrected training artifact; inference abstained.

## Frozen Execution

- 100 / 100 completed valid WikiText-2 causal-LM rows; zero error rows.
- 2 model sizes x 10 configurations x 5 seeds.
- 6,000 updates per run and three deterministic metric batches per model.
- Causal prefix-logit perturbation passed (`0.0` difference); the unmasked
  negative control failed as intended.
- Kaggle elapsed time: 5.318 P100-hours.

## Evidence Boundary

The factor has 20 independent configuration interventions, not 100 independent
models. The protocol requires at least 30 configuration/environment units for
an inferential MBE verdict. In addition, `random_metric` reused the seed ID and
was constant after configuration aggregation. This is a preserved negative-
control implementation failure. The artifact does not support survivor,
washout, or metric-family conclusions.

## Committed Artifact Set

| Artifact | Role | SHA-256 |
|---|---|---|
| `mbe2_causal_text_factorial.py` | executed factorial source | `ac866a358f46536ad69a985312aef7a212864c5fd2e1f8d945caa9b8297d7a4d` |
| `kaggle_downloads/v2/mbe2_corrected_causal_text_factorial.csv` | raw 100-row ledger | `3516dd05b8a627f6ee2655c184b61707f7223d993674fd98da69d3f7e0c1f0d9` |
| `kaggle_downloads/v2/mbe2_corrected_causal_text_factorial_manifest.json` | run grid, split hashes, execution metadata | `9287c652b9c77346d62f0b7d358aac9d9b7697da02c3a3c7b17da2e53cc5b6f8` |
| `out/INITIAL_REPORT.md` | integrity, raw configuration-level associations, stability, and abstention | `f3ce7efcf2874c2cb2daade3f8e33dde3518ff65376ea95584a73e4ae8e2de4f` |

The downloaded WikiText source copies and transient Kaggle log are intentionally
excluded from version control. They are not needed to inspect the ledger or
reproduce the analysis from the committed CSV and manifest.

## Reproduce The Report

```bash
python experiments/14_corrected_causal_text_factorial/analyze_factorial.py \
  experiments/14_corrected_causal_text_factorial/kaggle_downloads/v2/mbe2_corrected_causal_text_factorial.csv \
  experiments/14_corrected_causal_text_factorial/kaggle_downloads/v2/mbe2_corrected_causal_text_factorial_manifest.json \
  --out-dir experiments/14_corrected_causal_text_factorial/out
```

The script writes the integrity record, configuration-mean raw associations,
metric-batch stability table, and explicitly underpowered cross-fit diagnostics.
