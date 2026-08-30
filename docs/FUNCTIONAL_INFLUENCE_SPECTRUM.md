# Functional Influence Spectrum

Status: experimental candidate. No superiority, generalization, mechanistic
faithfulness, or MBE-survival claim has been established.

## What It Measures

The Functional Influence Spectrum (FIS) describes which naturally varying
directions at a chosen hidden layer locally affect the model's output.

For hidden activations `h`, let `C` be their sample covariance. Let `J` be the
Jacobian of the output with respect to `h`, and let `W` define meaningful
distance in output space. The downstream sensitivity geometry is

```text
G = E[J' W J].
```

FIS is the eigenvalue spectrum of `C G`, computed through the symmetric matrix
`C^(1/2) G C^(1/2)`. It reports:

- functional mass: total naturally exercised output sensitivity;
- effective dimension: entropy-effective number of influential directions;
- participation ratio: a second effective-rank summary;
- active rank versus activation rank;
- top-k influence concentration;
- the full normalized spectrum;
- paired sample-bootstrap intervals when requested.

For classification logits, `W = diag(p) - p p'` uses the Fisher-Rao geometry of
the predictive distribution. Euclidean and custom positive-semidefinite output
geometries are also supported.

## Why It Is More Defensible Than A Raw Norm

Under an invertible hidden-coordinate change `h_new = A h`, the covariance and
sensitivity transform as

```text
C_new = A C A'
G_new = A^(-T) G A^(-1).
```

Therefore `C_new G_new = A (C G) A^(-1)`, which has the same eigenvalues. The
profile is invariant to consistent permutations, rotations, rescalings, and
general invertible linear changes of hidden coordinates. A raw activation,
gradient, or Fisher norm generally lacks this property.

FIS also separates directions with high activation variance from directions
that affect output. A high-variance but downstream-ignored direction receives
zero functional influence.

## What It Does Not Establish

FIS is local to the supplied input distribution and output geometry. It does
not uniquely reconstruct the network, attach semantics to directions, prove a
causal abstraction, identify a circuit, or establish that output sensitivity
is desirable. Local Jacobian sensitivity can miss saturation, thresholds, and
large nonlinear interventions.

The full profile should be retained. Reducing it to effective dimension alone
would recreate the lossy-scalar problem that motivated this work.

## Required Validation Program

Before presenting FIS as a new metric, freeze and execute:

1. exact invariance tests under function-preserving hidden reparameterizations;
2. known-mechanism synthetic networks with active, redundant, and irrelevant
   subspaces;
3. finite activation interventions to test whether spectral mass predicts
   actual output change;
4. saturation and nonlinear-threshold failure cases;
5. sample-size, batch, layer, and Jacobian-estimator reliability;
6. comparisons with activation rank, gradient/Fisher norms, CKA, SVCCA/PWCCA,
   probing, model stitching, and random controls;
7. architecture and task transport with explicit abstention;
8. MBE against architecture, width, loss, confidence, and activation-scale
   baselines;
9. a protected external model-family holdout;
10. independent implementation and intervention replication.

CKA is a strong representation-similarity baseline, but similarity does not by
itself establish functional or causal importance. Interchange interventions
test stronger causal-abstraction hypotheses. FIS occupies a narrower middle
ground: coordinate-invariant, functionally weighted internal dimensionality
that is cheaper than a full causal abstraction and more informative than a raw
norm.

## Current API

```python
from mbe_eval import functional_influence_spectrum

profile = functional_influence_spectrum(
    activations,          # [samples, hidden dimensions]
    output_jacobians,     # [samples, output dimensions, hidden dimensions]
    probabilities=probs, # [samples, output dimensions]
)
```

The NumPy core is framework-agnostic. A PyTorch hook/Jacobian collector should
be added only after the estimand and validation protocol are frozen.
