# Experiment 31: Multi-Target Image Transport Atlas

This prospective 360-model campaign tests task- and target-specific metric
reliability across CIFAR-10, CIFAR-100, and a protected SVHN environment. Each
dataset has 24 independent configuration blocks and five repeated seeds.

The three private Kaggle kernels share one hash-frozen runner and differ only
in the dataset inferred from the code filename. Outputs are structurally
validated without inspecting metric-target associations.

The CIFAR development ledgers are public. The prospective SVHN raw ledger is
retained locally and excluded from Git because it contains the protected
metric-target associations. Its manifest, integrity summary, SHA-256, and
outcome-blind structural validation are public so custody can be verified
without opening the result.

## Completion

All 360 planned models completed: 120 each on CIFAR-10, CIFAR-100, and SVHN.
Every dataset retained all 24 independent configurations, five seeds per
configuration, and all three architectures, with zero error rows and zero
duplicate run IDs. The three structural validation records are in
`kaggle_downloads/<dataset>/v1/STRUCTURAL_VALIDATION.json`; the complete
provenance and claim boundary are in `DEVELOPMENT_COMPLETION_REPORT.md`.

Completion creates a prospective real-model transport artifact. It does not
authorize metric-target interpretation: the SVHN associations remain sealed
until a known-truth rule passes its frozen calibration and power gates at the
relevant 24-configuration design size.

```bash
python validate_outputs.py --dataset cifar10 --output-dir kaggle_downloads/cifar10/v1
python validate_outputs.py --dataset cifar100 --output-dir kaggle_downloads/cifar100/v1
python validate_outputs.py --dataset svhn --output-dir kaggle_downloads/svhn/v1
```

The SVHN command requires authorized access to the sealed raw ledger. Public
clones can verify its recorded hash and structural decision but cannot
reconstruct protected associations before the opening gate passes.

See `PREREGISTRATION.md` for the access boundary, independent-unit definition,
targets, and completion gates.
