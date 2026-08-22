# Corrected Image Factorial Preregistration

Frozen on 2026-08-11 before submission or inspection of any result from this
experiment.

## Question

How stable are training-metric reliability profiles in a balanced image
classification design with independent configuration units, repeated seeds,
a validation split separate from the protected test target, and a valid
per-run negative control?

## Design

- Dataset: CIFAR-10.
- Fixed split: 12,000 train, 3,000 validation, and 3,000 protected test
  examples selected by seed `20260811`.
- Architectures: CNN, CIFAR ResNet, and wide CIFAR ResNet.
- Factorial interventions: optimizer (AdamW or SGD), optimizer-specific low or
  high learning rate, weight decay (0 or 0.001), and dropout (0 or 0.2).
- Independent units: 48 hyperparameter/architecture configurations.
- Repeated runs: seeds `8111` and `8112`, giving 96 planned models.
- Training: 10 epochs, batch size 128.
- Diagnostics: three independently sampled metric batches per trained run;
  expensive Hessian diagnostics are measured on the first batch only.
- Negative control: one Gaussian value generated independently for each full
  `run_id` from a SHA-256-derived seed.

The run order is balanced across architectures. The notebook stops cleanly
before Kaggle's wall-clock limit and retains all failures.

## Outcomes And Controls

The primary target is protected `test_loss`; `test_acc` is secondary.
Prespecified design controls are architecture, optimizer, learning-rate level,
learning rate, weight decay, dropout, and seed. Training-state extensions add
final training-batch loss and then validation loss.

Metric families include Fisher/FIM, gradient, sharpness/Hessian, parameter and
update, representation geometry, confidence/calibration, task-proximal, and a
random negative control. No metric may be removed because its result is
unfavorable.

## Completion Gate

Primary analysis requires at least 90% of planned valid runs, all 48
configurations, both seeds for every included configuration, and all three
architectures. Failure of this gate makes the run descriptive only. Every
failed row remains in the ledger.

## Analysis Boundary

The raw ledger is frozen before target-metric associations are inspected.
Nuisance-family eligibility must be established using design-matched
known-truth calibration that does not use these real metric outcomes. Until
that gate exists, additive, interaction, and flexible-family results are
reported as components and the substantive metric verdict is an abstention.

This experiment can support CIFAR-10 image-design evidence. It cannot by
itself establish universal metric rankings or language-model transport.
