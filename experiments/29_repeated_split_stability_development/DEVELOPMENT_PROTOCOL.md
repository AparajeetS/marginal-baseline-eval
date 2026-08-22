# Repeated-Split Stability Development Protocol

Status: outcome-blind development protocol. This is not an opening gate for
any protected association and cannot amend experiments 21, 26, or 28.

## Question

Can an intersection rule across independently shuffled, configuration-blocked
cross-fit splits reduce false support at 24 and 48 independent configurations
without reducing effect-0.50 power below a useful floor?

The candidate estimator is a conditional rank-covariance score. It concludes
positive support only when every split has a positive score and a wild-bootstrap
`p` value at or below its candidate threshold. This produces no pooled p-value.
It is an empirical stability rule whose calibration must be measured here.

## New Known-Truth Geometries

The development data are generated from two new factor grids, independent of
the historical image/text artifact layouts and the PGDL design:

- `image48`: 48 configurations from four architecture families, three
  optimizers, two learning-rate bands, and two augmentation levels; two seeds
  per configuration.
- `text24`: 24 configurations from three width tiers, two context lengths, two
  learning-rate bands, and two dropout levels; two seeds per configuration.

Each geometry includes three baseline ladders, two group-ICC levels, five
known-null/proxy scenarios, and a genuine incremental signal at effects 0.35
and 0.50. New deterministic seeds are paired across candidates within each
simulation cell and are not reused by a subsequent confirmation.

## Candidates

All candidates use a pairwise-interaction polynomial ridge nuisance model.
The frozen development grid is:

| Candidate | Degree | Ridge | Repeated splits | Split alpha |
|---|---:|---:|---:|---:|
| `d2_r01_repeat3_a05` | 2 | 0.10 | 3 | 0.05 |
| `d2_r01_repeat3_a01` | 2 | 0.10 | 3 | 0.01 |
| `d2_r01_repeat5_a05` | 2 | 0.10 | 5 | 0.05 |
| `d4_r01_repeat3_a05` | 4 | 0.10 | 3 | 0.05 |
| `d4_r01_repeat3_a01` | 4 | 0.10 | 3 | 0.01 |
| `d4_r01_repeat5_a05` | 4 | 0.10 | 5 | 0.05 |

## Development Screen

The full screen uses 20 repetitions per cell and 999 wild-bootstrap draws.
A candidate is eligible for a new confirmation design only if, in every
scope-baseline pair:

- estimability is at least 98%;
- maximum raw known-null support is at most 5%; and
- minimum raw positive support at effect 0.50 is at least 50%.

Among eligible candidates, select the lowest `complexity_rank`. Ties are broken
by lower maximum known-null support, then higher minimum effect-0.50 power,
then lexical candidate id. The selection is development-only and authorizes no
protected metric or target read.

## Confirmation Boundary

If a candidate survives, a separate confirmation must use fresh simulation
geometries and seeds, 100 repetitions per cell, frozen Wilson thresholds, and
a preregistered sample-size-aware abstention rule. If no candidate survives,
the negative result is retained and the project does not tune on protected
image, text, or PGDL outcomes.
