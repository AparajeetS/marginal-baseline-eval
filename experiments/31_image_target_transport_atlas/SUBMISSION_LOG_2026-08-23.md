# Submission Log: 2026-08-23

## Frozen Campaign

- Protocol: multi-target image transport atlas v1
- Planned models: 360
- Planned independent configuration blocks: 72
- Per dataset: 120 models, 24 configurations, five repeated seeds
- Per-kernel wall-clock cap: 9.5 hours
- Total GPU cap: 28.5 P100 hours
- Shared runner SHA-256:
  `bfb8271df133646cd59e79a7dae05771fff3a61222d1285c5dd820ca526e2da7`
- Preregistration SHA-256:
  `cf2d469a0afedfa29decf790bed235e7cc9f4713e91d66ecb0e3a4444178905a`

## Submitted Development Environments

- `aparajeetshadangi/mbe-3-image-transport-cifar-10`, version 1: RUNNING
- `aparajeetshadangi/mbe-3-image-transport-cifar-100`, version 1: RUNNING

Kaggle canonicalized `cifar10` and `cifar100` in the requested metadata IDs to
`cifar-10` and `cifar-100`. This changed only the remote URL slug. The uploaded
code and frozen dataset inference from each code filename are unchanged.

## Version 1 Infrastructure Failure

Both development kernels failed before dataset loading or result creation
because Kaggle renamed the uploaded file to `script.py`, defeating the local
filename-based dataset default. The frozen recovery replaces only that default
with the kernel's literal preregistered dataset name. Full logs and original
hashes are retained in `kaggle_failures` and `FAILED_V1_SHA256SUMS`.

## Version 2 Recovery Submission

- CIFAR-10 version 2: RUNNING
- CIFAR-100 version 2: RUNNING
- CIFAR-10 recovery script SHA-256:
  `80f42be3601c672cb1bff03ea6efd6cf7f875df4110e463bbd4e4173743fe274`
- CIFAR-100 recovery script SHA-256:
  `6408afbd161d6870aad2f352711dd44b425f65acc28fb676cb55976346246d80`

The version-1 failures occurred after roughly 2.5 minutes of environment setup
and before training, so their GPU-quota cost was negligible. SVHN remains
unsubmitted until one development slot reaches a terminal state.

## Development Completion And SVHN Submission

- CIFAR-10 version 2: COMPLETE, 120/120 valid, 0 errors, 2.78 P100-hours
- CIFAR-100 version 2: COMPLETE, 120/120 valid, 0 errors, 2.88 P100-hours
- Both 24-configuration structural gates passed independently.
- Metric-target associations inspected: no
- SVHN version 1: submitted after both development completions and currently
  RUNNING at `aparajeetshadangi/mbe-3-image-transport-svhn`

## Queued Protected Environment

- `aparajeetshadangi/mbe-3-image-transport-svhn`
- Submission is gated on one development kernel reaching a terminal state so
  no more than two GPU sessions are active.
- SVHN target-metric associations must not be inspected during submission,
  download, integrity validation, or before a separately frozen opening rule
  passes.
