# V2 Ten-Repetition Development Results

Status: exploratory development evidence. This result cannot unlock protected
associations.

## Completion

- 6,720 of 6,720 planned cells completed.
- Estimability was 100% in every cell.
- Image used 48 independent configurations; text used 24.
- Synthetic frames were paired across candidates and baseline ladders.
- Inference used 999 multiplier draws and the recorded two-sided threshold
  0.005.
- The ledger, summary, manifest, diagnostic, and hashes are under
  `out_development_v2_10/`.

## What Changed From V1

V2 multiplied configuration-mean residuals rather than averaging rowwise
products, strengthened ridge regularization, paired simulations across methods,
and used the V1-developed threshold 0.005. V1 source and outputs remain
preserved.

## Diagnostic Result

The correction substantially improved raw null behavior but did not produce a
confirmable rule at ten repetitions. A ten-repetition cell with zero false
supports still has a Wilson 95% upper bound of about 27.8%, so no candidate can
meet the 10% uncertainty gate at this stage.

Strong-ridge degree-4 interactions were the best shared image/text candidate.
Across image baselines, worst-cell raw null support was 10-20% and mean
effect-0.50 power was 75%. Across text baselines, worst-cell raw null support
was 10% and mean effect-0.50 power was 35-45%.

Extra Trees was the cleanest null comparator. Several scope-baseline pairs had
zero raw false supports and the others had 10-20%, but its text effect-0.50
power averaged only 20-30%.

Additive candidates reached roughly 85-90% mean image power at effect 0.50 but
had worst-cell raw null support as high as 30-50%. They are not advanced to the
larger development run.

## Next Gate

Run 100 development repetitions for strong-ridge interactions and Extra Trees
on the unchanged V2 grid. A candidate is worth freezing only if the larger run
supports the recorded null and power thresholds. Candidate selection after
this run remains development; a later untouched-seed confirmation is required.
