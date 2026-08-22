# Submission Log: 2026-08-11

- Kaggle ref: `aparajeetshadangi/mbe-3-corrected-image-factorial`
- Submitted version: 1
- Initial status: `RUNNING`
- Script SHA-256: `8a60f289c936e307b35376a1151a2b3134847a1a79df78ba162c4eec5273caaa`
- Preregistration SHA-256: `b0557fb69d7de3d6abb53cf8908edf5e68a21d78412eb87ee4c7a8fd2369eeab`

The private kernel was submitted only after the local smoke test produced one
valid row from each frozen architecture with no errors or duplicate run IDs.

## Version 1 Infrastructure Failure

Version 1 stopped before dataset loading or training because Kaggle assigned a
Tesla P100 (`sm_60`) while its default PyTorch wheel supported only `sm_70`
and newer. No scientific output row was produced. Version 2 adds only the
previously proven PyTorch 2.4.1 + torchvision 0.19.1 CUDA 11.8 compatibility
bootstrap. The grid, seeds, outcomes, controls, and preregistration are
unchanged. Version-2 script SHA-256:
`84f65ff8e69ba30a442efb5bcc524cb8823e109af55331d93ee7702607b814c7`.

## Version 2 Completion

Version 2 completed in 1.984 P100-hours. All 96 planned rows were valid and the
preregistered structural completion gate passed. Outputs were downloaded to
`kaggle_downloads/v1` and independently validated without inspecting
target-metric associations.
