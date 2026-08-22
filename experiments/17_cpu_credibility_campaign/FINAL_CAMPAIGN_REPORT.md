# Final CPU Credibility Campaign Report

Completed: 2026-07-29

This campaign executed the frozen state machine in
`docs/CPU_CAMPAIGN_NEXT_48_HOURS.md`. All planned CPU lanes completed without
dropped cells or outcome-dependent changes to the experimental grids.

## Execution gates

| Lane | Gate result | Validated output |
| --- | --- | --- |
| Observed-design nuisance sensitivity | Pass | Degrees 1, 2, 3, 4, and 6; 9,000 ledger rows and 45 summary rows per degree |
| Corrected inference stress | Pass | 8,000 full-refit rows and 8,000 block-permutation rows |
| Generic-proxy complexity sweep | Pass | 19,200 new degree 1, 3, and 4 rows, interpreted with the frozen degree 2 and 6 results |
| Refit-draw convergence | Pass | 4,000 paired ledger rows, 40 summary rows, and 30 draw-count comparisons |
| Public-study reaudit | Pass | 9,700 runs, 1,000 configurations, and 32 metrics from the Dziugaite et al. artifact |
| Software verification | Pass | 49 tests, wheel and sdist build, isolated wheel install, and end-to-end demo |

Every completed lane passed its expected row-count, schema, duplication,
estimability, manifest, and SHA-256 gates. Scientific estimation failures were
retained as results; no unfavorable cells were removed.

## Main findings

1. Full refitting substantially improves inference calibration. Across the
   corrected null and generic-proxy simulations, predictive and joint false
   support were 0.25% and 0.125%, respectively, while signal support was
   100% and 99.81%.
2. Residual block permutation remains diagnostic rather than confirmatory.
   Its empirical null rejection rates ranged from 5.30% to 7.25%, including
   6.95% under clustered noise.
3. Nuisance complexity creates a real design tradeoff. Degrees 1 through 3
   retain high power in the observed design but fail the generic-proxy
   controls. Degree 6 controls those proxies but the interaction family has
   only about 1% support for the largest observed-design signal.
4. Consequently, no tested polynomial degree provides a universal mandatory
   two-family consensus rule that is both proxy-safe and adequately powered
   at 36 observed configurations. The frozen real-metric result is therefore
   an abstention, not evidence that the audited metrics are substantively
   null.
5. The paired convergence study found complete agreement with 999 draws at
   499 refit draws across all 1,000 paired decisions. The recommended defaults
   are 199 draws for screening and 499 for publication-quality decisions in
   this design.

## Protocol consequence

Prospective MBE analyses should freeze candidate nuisance families and
thresholds before protected outcomes are inspected, calibrate each candidate
on design-matched known-truth null, proxy, and signal controls, and permit only
eligible families to contribute to a claim. Agreement is required among the
eligible families; disagreement or the absence of an eligible family produces
an abstention. A nuisance family may not be selected because it gives a
favorable result on the real metrics.

The historical frozen rule remains the correct record for earlier analyses.
The calibration-gated rule is the prospective protocol motivated by this
campaign.

## Reproducibility and provenance

The final manifest is `FINAL_SHA256SUMS`. The principal transferred archives
have these SHA-256 digests:

| Archive | SHA-256 |
| --- | --- |
| Degree-2 observed-design sensitivity | `19d36c57d9bb32dfaabb41996a6aff2011dd5bde6191e0cad6f2756bae291201` |
| Corrected inference stress | `76d96ecaa95ab3431e09c742623ff23003aac091ae77d290c03c7d30fa3bb888` |
| Generic degree 1/3/4 sweep | `46aed13d38edea7cc689100cd4a6e8d83fdadd0f50a9ba590b9176b73e4004c4` |
| Refit-draw convergence | `3c928184136c09e72846cd636aef7df4643f2254ea0f321c9e09679072e7735c` |
| Observed-design degree 1/3/4 sweep | `4d575ef19331b4efb9102872c1ac0ed907009ed806dab88f3480dc6b0df5ba90` |

## Remaining publication gates

This campaign resolves important statistical and implementation questions, but
it is not by itself a JMLR-scale validation. Remaining gates include a locked
prospective image and language model atlas, a genuinely protected holdout,
independent reimplementation or replication, a second suitable public-study
reaudit with run-level artifacts, and external adversarial statistical review.
