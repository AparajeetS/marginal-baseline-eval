# V2 Hundred-Repetition Finalist Results

Status: completed development evidence. No candidate passed; protected
associations remain sealed.

## Integrity

- 19,200 of 19,200 planned cells completed.
- All task keys were unique and every cell had exactly 100 repetitions.
- Estimability was 100%; there were zero error rows.
- All recorded SHA-256 hashes match.
- The manifest records no protected-data read and no authorization to open it.
- Exact runner and estimator source are retained under the output directory.

## Binding Result

Neither strong-ridge degree-4 interactions nor Extra Trees met both the null
and power gates at decision threshold 0.005.

Extra Trees was closest to null control. Its worst raw null support was 5-8%
across scope-baseline pairs, with Wilson upper bounds 11.2-15.0%. Its weakest
effect-0.50 image power was 29-52%, and text power was 16-25%.

Strong-ridge interactions retained useful image power: weakest effect-0.50
power was 57%, 61%, and 66% across B1-B3. The corresponding lower bounds were
47.2%, 51.2%, and 56.3%. It remained anti-conservative, however: worst raw
image null support was 9-11%, with upper bounds 16.2-18.6%. Text power remained
weak at 26-33%, while worst raw null support was 6-8%.

The dominant failures were interaction-proxy and heteroskedastic-proxy nulls.
Low-ICC effect-0.50 cells were consistently the weakest signal cells.

## Threshold Frontier

Tightening the two-sided decision threshold reduced worst null support but
also removed useful power. At threshold 0.001, worst raw null support was at
most 5%, but strong-ridge interaction power fell to 28-39% in the weakest image
cells and 8-9% in the weakest text cells. Practical slope floors did not repair
this tradeoff.

## Conclusion

A single split and p-value threshold does not solve the 24/48-configuration
problem. V2 does not earn a confirmation run. The next development question is
whether a fixed repeated-split stability rule can reject nuisance artifacts
while preserving image power. If not, MBE must encode sample-size-aware
abstention and treat 24 configurations as insufficient for this claim class.
