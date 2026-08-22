# Repeated-Split Stability Results

Status: closed development branch. Protected associations remain sealed.

The 20-repetition screen completed 1,920 synthetic datasets and three grouped
cross-fit analyses per dataset. All rows were estimable and the output hashes
are recorded under `out_stability_20/`.

Unanimous split rules did not remove nuisance failures. Spearman correlations
between the three split p-values were 0.889-0.896, so changing folds largely
repeated the same small-sample nuisance error. Depending on the rule and
baseline, worst raw null support was 10-35%. Rules with strong image power had
the worst null behavior; stricter unanimous rules lost text power.

This branch is not advanced to 100 repetitions. Repeated split assignments do
not create new independent configurations and cannot substitute for them.
