# Functional Influence Spectrum Validation

Status: frozen before benchmark execution.

## Question

Does the Functional Influence Spectrum (FIS) recover functionally used hidden
subspaces more faithfully and robustly than existing inexpensive summaries?

This experiment can support only specific benchmark claims. It cannot establish
that FIS reveals semantic concepts, complete circuits, or a unique causal
description of a network.

## Candidate

At a chosen hidden layer, FIS is the eigenvalue spectrum of `C G`, where `C` is
activation covariance and `G = E[J' W J]` is downstream output-sensitivity
geometry. The implementation under test is
`mbe_eval.functional_influence_spectrum` and must not be changed after benchmark
outcomes are inspected without creating a new protocol version.

## Comparators

- activation covariance rank and participation ratio;
- activation norm and per-direction variance;
- gradient norm and gradient covariance rank;
- empirical Fisher trace and effective rank;
- linear CKA;
- SVCCA and PWCCA;
- linear probes;
- model stitching;
- finite activation interventions as the expensive reference measurement;
- random rankings and width-only predictions as negative controls.

CKA, SVCCA, probes, and stitching answer somewhat different questions. They are
included to test whether FIS adds useful information, not to declare one universal
ranking across incompatible estimands.

## Frozen Test Families

1. Linear networks with known active, redundant, correlated, and irrelevant
   hidden subspaces.
2. Function-preserving permutations, rotations, anisotropic rescalings, and
   dense invertible changes of hidden coordinates.
3. ReLU, tanh, sigmoid, and gated networks with saturation and threshold cases.
4. Networks with high-variance unused directions and low-variance decisive
   directions.
5. Redundant representations whose width changes without changing function.
6. Small trained image and text models evaluated across layers and seeds.
7. Finite interventions at multiple radii to expose failures of local Jacobians.

Synthetic generators will be seeded and will retain the true active subspace,
finite-intervention effects, and all failed or non-estimable cells.

## Primary Endpoints

- active-subspace rank error;
- principal-angle error against the known active subspace where a method returns
  directions;
- Spearman association with held-out finite-intervention output effects;
- invariance error under function-preserving coordinate changes;
- reliability across independent input samples;
- incremental prediction of intervention effects beyond width, activation scale,
  gradient scale, loss, and confidence baselines.

Uncertainty will be reported by generator-level bootstrap intervals. Comparisons
will use paired generator instances and will not treat samples from one network as
independent networks.

## Superiority Gate

FIS may be described as outperforming the tested inexpensive summaries only if:

1. its median coordinate-change invariance error is at most `1e-8` on linear
   networks and below every non-invariant scalar comparator;
2. its active-rank absolute error is lower than activation-rank and
   gradient/Fisher-rank baselines with a paired 95% interval excluding zero;
3. its held-out intervention association exceeds every inexpensive comparator
   by at least `0.05`, with a paired 95% interval excluding zero;
4. it adds held-out predictive value beyond the frozen nuisance baseline;
5. it does not lose more than `0.05` intervention association relative to the
   best comparator in any prespecified architecture family; and
6. all negative, saturation, abstention, and non-estimable cases are retained.

Failure of any gate prohibits a general superiority claim. Passing only selected
families supports a family-qualified claim.

## Leakage Controls

- Synthetic test seeds are disjoint from development seeds.
- Comparator settings are fixed from their source papers or a separate development
  split.
- No threshold may be selected on the protected test families.
- Aggregate outcomes are opened only after row-count, duplicate, balance, and
  integrity checks pass.
- The final external model family remains sealed until the method and analysis
  code are frozen.

## Required Outputs

- raw per-network and per-layer results;
- generator and environment manifests;
- comparator versions and settings;
- integrity report with row counts, duplicate keys, errors, and exclusions;
- paired estimates and confidence intervals for every primary endpoint;
- failure-case atlas;
- SHA-256 manifest;
- a claim ledger distinguishing passed, failed, and untested claims.
