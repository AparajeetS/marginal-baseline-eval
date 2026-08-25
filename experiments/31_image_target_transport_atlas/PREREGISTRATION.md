# Multi-Target Image Transport Atlas Preregistration

Frozen before Kaggle submission and before inspection of any association
between a generated metric and a target from this campaign.

## Purpose

This campaign tests whether metric reliability is specific to the target and
environment. The same frozen metric battery is collected while the downstream
targets vary between clean generalization, controlled corruption robustness,
and calibration. It creates real-model evidence that complements, but cannot
replace, known-truth calibration.

## Environments and Access Boundary

- Development environments: CIFAR-10 and CIFAR-100.
- Prospective transport environment: SVHN.
- SVHN metric-target associations remain protected until a separately frozen
  known-truth rule authorizes opening. Structural validation, hashes, errors,
  and configuration balance may be inspected before that decision.
- Failure of an opening gate is binding and leaves SVHN sealed.

## Frozen Design Per Dataset

- Architectures: CNN, CIFAR ResNet, and wide CIFAR ResNet.
- Eight fractional-factorial settings covering optimizer, learning-rate band,
  weight decay, and dropout.
- Independent units: 24 dataset/architecture/configuration blocks.
- Repeated seeds: 8311--8315, producing 120 planned models per dataset.
- Total campaign: 360 models and 72 independent configuration blocks.
- Training: 15 epochs, batch size 128, 20,000 training examples.
- Validation: 5,000 fixed examples, disjoint from training.
- Protected test target: 5,000 fixed examples, disjoint from training and
  validation.
- Metric diagnostics: three deterministic training batches; Hessian metrics
  on the first batch only.
- Maximum runtime: 9.5 P100 hours per dataset kernel, 28.5 hours total.

Seeds are repeated measurements, not independent configurations. Primary
uncertainty must be configuration-blocked, and pooled analyses must retain
dataset as an environment rather than treating 360 rows as exchangeable.

## Frozen Targets

Primary target: clean test loss.

Secondary targets:

- mean loss under Gaussian noise, 3x3 average blur, and low contrast;
- clean test expected calibration error;
- clean test Brier score;
- accuracies are descriptive counterparts.

The corruption suite is deterministic from the full run ID. It is a controlled
stress suite, not a claim of equivalence to CIFAR-C or natural distribution
shift.

## Metrics and Baselines

The inherited metric battery covers Fisher/FIM, gradients, Hessian/sharpness,
weights and updates, representation geometry, confidence/calibration,
task-proximal measurements, and a SHA-256-seeded Gaussian negative control.
No metric may be dropped because of missing, null, negative, or sign-flipped
results.

Baseline ladders are:

1. architecture and frozen factorial design;
2. design plus final training state;
3. design and training state plus validation loss.

Targets remain separate. A metric may be informative for robustness and
uninformative for clean loss without contradiction.

## Completion and Claim Gates

Each dataset is structurally complete only if:

- at least 108 of 120 planned runs are valid;
- all 24 independent configurations are represented;
- every represented configuration has at least four valid seeds;
- all three architectures are present;
- there are no duplicate run IDs; and
- split and source hashes match.

Before substantive interpretation, the selected audit rule must have passed
its separately frozen known-truth calibration and power gate at the relevant
24-configuration sample size. This campaign alone cannot establish universal
metric trust, causal importance, production readiness, or cross-modality
transport.

