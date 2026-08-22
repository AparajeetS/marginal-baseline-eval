# Paired Refit-Draw Convergence: Results

The frozen study completed 4,000/4,000 rows with no estimation failures or
duplicate paired keys. It contains 100 repetitions for every combination of
five known-truth scenarios, two nuisance families, and 99, 199, 499, or 999
refit-bootstrap draws.

## Decision Agreement With 999 Draws

| Refit draws | Worst cell agreement | Mean cell agreement | Largest positive-to-negative flip rate | Largest negative-to-positive flip rate |
|---:|---:|---:|---:|---:|
| 99 | 98% | 99.7% | 1% | 1% |
| 199 | 97% | 99.6% | 2% | 1% |
| 499 | 100% | 100% | 0% | 0% |

The 999-draw result is a higher-draw Monte Carlo reference, not ground truth.
All observed disagreements were confined to borderline null/proxy cells.
Every draw count recovered the genuine increment in 100% of repetitions for
both nuisance families.

At 199 draws, disagreement occurred in two interaction-family cells:
heteroskedastic null agreement was 99%, and nonlinear-proxy agreement was 97%.
At 99 draws, two nonlinear-proxy cells had 98%-99% agreement. The 499-draw
decisions agreed with the 999-draw reference in all 1,000 paired
scenario-by-nuisance repetitions.

Median absolute movement of the lower confidence bound declined from
`0.000185` at 99 draws to `0.000124` at 199 and `0.000055` at 499. Rare maximum
movements were larger: `0.034357`, `0.015289`, and `0.006596`, respectively.

## Operational Consequence

The evidence supports 199 draws as a practical exploratory or screening
budget in these simulations, but 499 draws is the defensible
publication-quality default when a decision is near zero. This recommendation
is based on paired stability rather than which draw count produces more
positive findings. It does not establish interval coverage outside the tested
designs.

The transferred archive
`mbe_draw_convergence_complete_20260729_1630.tar.gz` had SHA-256
`3c928184136c09e72846cd636aef7df4643f2254ea0f321c9e09679072e7735c`.
