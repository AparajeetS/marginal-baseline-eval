# Multi-Corpus Causal-LM Atlas Completion Report

Completed on Kaggle on 2026-08-11.

## Structural Result

- Kaggle ref: `aparajeetshadangi/mbe-3-multi-corpus-text-atlas`
- Successful version: 2
- GPU: Tesla P100-PCIE-16GB
- Runtime: 1.264 GPU-hours
- Planned and valid rows: 144 / 144
- Independent configurations: 72
- Seeds per configuration: 2 / 2 for all 72 configurations
- Environment balance: 48 WikiText-2, 48 Penn Treebank, and 48 Tiny
  Shakespeare rows
- Complete configurations per environment: 24 / 24
- Error rows: 0
- Duplicate run IDs: 0
- Required nonfinite measurements: 0
- Downloaded dataset hashes: matched
- Frozen source hashes: matched
- Causal-mask leakage test: passed
- Unmasked negative control: passed
- Preregistered primary completion gate: passed

The independent structural check is stored in
`kaggle_downloads/v1/STRUCTURAL_VALIDATION.json`. The recursive artifact ledger
is `kaggle_downloads/v1/ARTIFACT_SHA256SUMS`.

## Principal Artifact Hashes

| Artifact | SHA-256 |
| --- | --- |
| Raw CSV | `63e6849749dabf5e218e345e8c268550cb97b16587a9a07d5b1188a822b32246` |
| Run manifest | `653f26f5876309190b068a4ab870297d1d16318bfd28b05d848e31337aee046c` |
| Kernel integrity report | `fd707343b38600cafe8a8f812d6bf440809b40028deef493b6ded3607694b512` |
| Independent validation | `887218fe28c7fce7a4b092c9fa427095cc1354d14b3352441bb348272f62eebb` |

## Protected Analysis Boundary

No target-metric association was inspected or interpreted during download or
validation. Substantive within-corpus and transport analysis remains locked
until the design-matched known-truth nuisance-family calibration gate is
frozen. This report establishes artifact completeness and protocol compliance
only.
