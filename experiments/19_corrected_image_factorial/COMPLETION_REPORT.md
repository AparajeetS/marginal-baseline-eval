# Corrected Image Factorial Completion Report

Completed on Kaggle on 2026-08-11.

## Structural Result

- Kaggle ref: `aparajeetshadangi/mbe-3-corrected-image-factorial`
- Successful version: 2
- GPU: Tesla P100-PCIE-16GB
- Runtime: 1.984 GPU-hours
- Planned and valid rows: 96 / 96
- Independent configurations: 48
- Seeds per configuration: 2 / 2 for all 48 configurations
- Architecture balance: 32 CNN, 32 ResNet, 32 wide ResNet rows
- Optimizer balance: 48 AdamW and 48 SGD rows
- Error rows: 0
- Duplicate run IDs: 0
- Required nonfinite measurements: 0
- Frozen split hashes: matched
- Frozen source hashes: matched
- Preregistered primary completion gate: passed

Version 1 ended before dataset loading or training because the assigned P100
was incompatible with the default PyTorch wheel. Version 2 changed only the
runtime compatibility bootstrap; the grid, seeds, outcomes, controls, and
preregistration were unchanged. `FAILED_V1_SHA256SUMS` preserves the version-1
source identity.

The independent structural check is stored in
`kaggle_downloads/v1/STRUCTURAL_VALIDATION.json`. The recursive artifact ledger
is `kaggle_downloads/v1/ARTIFACT_SHA256SUMS`.

## Principal Artifact Hashes

| Artifact | SHA-256 |
| --- | --- |
| Raw CSV | `71f41e0fdafd6d6d405cb7faa4d2c7ee3d5ce7c378e899188c1b57a9f81fffb4` |
| Run manifest | `5457349468724f56ac22aa325dc5e7cd8c4a8f087b516bc157fef8f2480ee7b2` |
| Kernel integrity report | `4bfa1b82074961177b205910c00b9af384e46f44df8af3509909e79ba6f83f67` |
| Independent validation | `6652f215860329b53a0f5714407019af4ab6a785e72c380a6f39b7e95f2b6280` |

## Protected Analysis Boundary

No target-metric association was inspected or interpreted during download or
validation. Substantive analysis remains locked until the design-matched
known-truth nuisance-family calibration gate is frozen. This report establishes
artifact completeness and protocol compliance only.
