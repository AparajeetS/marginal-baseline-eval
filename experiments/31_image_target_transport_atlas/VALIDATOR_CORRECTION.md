# Structural Validator Correction

The original post-run structural validator hardcoded claims that the SVHN
associations were unopened and that metric-target associations had not been
inspected. Filesystem validation cannot establish either fact.

The corrected validator removes those claims, recomputes the integrity record,
checks the manifest grid and split-hash shape, and verifies every frozen source
hash. The original validator hash remains in `FROZEN_SHA256SUMS`; the old and
corrected hashes are recorded in `VALIDATOR_CORRECTION.json` so the post-run
change is explicit rather than presented as part of the preregistered state.
