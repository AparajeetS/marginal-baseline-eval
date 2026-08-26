# Infrastructure Recovery Provenance

## Version 1 Failure

The first CIFAR-10 and CIFAR-100 submissions terminated before dataset loading,
model construction, training, or result-row creation. Kaggle materialized each
uploaded source file as `/kaggle/src/script.py`. The runner's local convenience
default inferred the dataset from `Path(__file__).stem`, which therefore
resolved to the unsupported value `script`.

The raw platform logs were omitted from the public tree because they contain
no dataset access, model construction, training, or scientific output.
`FAILED_V1_SHA256SUMS` retains the original uploaded-script hashes, and this
document preserves the complete recovery rationale.

## Corrective Change

Each already separate kernel copy now assigns its preregistered dataset name
as a literal: `cifar10`, `cifar100`, or `svhn`. No grid, seed, architecture,
training setting, target, metric, split rule, threshold, runtime cap, or access
boundary changed. The common runner and preregistration are unchanged. Version
2 is therefore an infrastructure-only recovery and not a scientific rerun.

Kaggle canonicalized the first two remote slugs to `cifar-10` and `cifar-100`.
The recovery metadata uses those canonical IDs so version 2 updates the
existing private kernels rather than attempting to create conflicting slugs.
