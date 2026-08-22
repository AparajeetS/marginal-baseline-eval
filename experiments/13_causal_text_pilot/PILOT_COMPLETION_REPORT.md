# Corrected Causal-LM Pipeline Pilot: Completion Record

Status: completed implementation gate; not inferential metric evidence.

## Result

Kaggle version 3 completed all 24 planned WikiText-2 runs after two retained
environment/data-encoding failures in earlier versions. The v3 data and model
pipeline passed its causal behavioral test:

| Check | Result |
|---|---:|
| Causal prefix-logit difference after future-token perturbation | `0.0` |
| Intentionally unmasked negative-control difference | `3.1988818645` |
| Valid training rows | `24 / 24` |
| CUDA device | Tesla P100-PCIE-16GB |
| Elapsed time | 0.322 hours |

## What This Clears

- explicit causal masking is active on the executed language-model path;
- the negative control fails as expected when the mask is removed;
- official WikiText-2 split hashes, independent configuration/seed IDs, row
  flushing, metric extraction, and resume behavior are functional.

## What This Does Not Claim

This pilot does not estimate metric-family reliability, MBE calibration,
transport, selector utility, or a language-model result. It only cleared the
implementation gate for the corrected factorial.

## Provenance

- Kaggle notebook: <https://www.kaggle.com/code/aparajeetshadangi/mbe-2-causal-text-pipeline-pilot>
- Executed v3 source SHA-256:
  `42b274585d1d08182a4a487edb8ca53b749e346e67ee9ee85e86b71778d29d2f`
- Downloaded raw pilot artifacts remain local-only because they include copied
  WikiText source files. Their fields and intended outputs are documented in
  [README.md](README.md) and [SUBMISSION_LOG_2026-07-17.md](SUBMISSION_LOG_2026-07-17.md).
