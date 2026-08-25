# Campaign Completion Report

All three environments completed on Kaggle and were structurally validated by
2026-08-25. Metric-target associations were not inspected during
synchronization or validation.

The campaign contains 360 / 360 valid trained-model rows, 72 independent
dataset/architecture/configuration blocks, five repeated seeds per block,
three architectures per dataset, zero error rows, and zero duplicate run IDs.
All three preregistered structural gates passed. Recorded execution totaled
8.09 P100 GPU-hours.

## CIFAR-10

- Kaggle kernel: `aparajeetshadangi/mbe-3-image-transport-cifar-10`
- Successful version: 2
- GPU: Tesla P100-PCIE-16GB
- Runtime: 2.78 GPU-hours
- Valid rows: 120 / 120
- Independent configurations: 24 / 24
- Seeds per configuration: 5 / 5
- Architectures: CNN, ResNet, wide ResNet
- Error rows: 0
- Duplicate run IDs: 0
- Structural completion gate: passed
- Ledger SHA-256:
  `bb8ee05ed22191f8e63509341f8b6be846d78aefaf2ccc71d6a32972813f0fc5`

## CIFAR-100

- Kaggle kernel: `aparajeetshadangi/mbe-3-image-transport-cifar-100`
- Successful version: 2
- GPU: Tesla P100-PCIE-16GB
- Runtime: 2.88 GPU-hours
- Valid rows: 120 / 120
- Independent configurations: 24 / 24
- Seeds per configuration: 5 / 5
- Architectures: CNN, ResNet, wide ResNet
- Error rows: 0
- Duplicate run IDs: 0
- Structural completion gate: passed
- Ledger SHA-256:
  `9a0de6d3f405103f649928d0a5e8e251093cd199635df4e318c56fb598d458c3`

## SVHN Prospective Transport Environment

- Kaggle kernel: `aparajeetshadangi/mbe-3-image-transport-svhn`
- Kaggle status: complete
- GPU: Tesla P100-PCIE-16GB
- Runtime: 2.43 GPU-hours
- Valid rows: 120 / 120
- Independent configurations: 24 / 24
- Seeds per configuration: 5 / 5
- Architectures: CNN, ResNet, wide ResNet
- Error rows: 0
- Duplicate run IDs: 0
- Structural completion gate: passed
- Ledger SHA-256:
  `5043042032c421512a89f67b1b87b4c25ca3da0e3e6a1849c02ff418de21e3a8`

The source runner, manifest, integrity summary, raw ledger, structural
validation record, and execution log were synchronized. Dataset cache files
and transient logs remain excluded from Git according to repository policy.

## Access Boundary

This campaign establishes that the preregistered collection and integrity
protocol can produce a complete multi-target, multi-environment real-model
ledger. It supplies a prospective benchmark for testing whether metric support
changes between clean loss, corruption loss, calibration, and environment.

It does not establish that MBE is calibrated, that any metric survives or
washes out, or that support transports to SVHN. Each environment has 24
independent configurations; repeated seeds improve measurement but do not
increase the inferential sample size. Experiment 30 found that, in its frozen
noisy-observable known-truth regime, even the observable oracle did not meet
the useful-power gate at 24 configurations. The current learned procedures
therefore have no authorization to interpret these protected associations.

SVHN remains sealed. Any opening requires a separately frozen rule that first
passes false-support and power gates at the relevant design size on disjoint
known-truth data. Until then, the strongest claim is artifact completion and
research feasibility, not metric reliability or transport.
