# Replication Packet V2 Provenance Amendment

Recorded: 2026-08-22. The orthogonal-source alias was recorded before the
initial evidence release. The Python 3.9 aliases were added immediately after
that release's public CI run exposed a compatibility error. No external
execution has occurred.

## Orthogonal-Score Lineage

Experiments 23-28 froze SHA-256
`4bdaa889b43d9661ed3f23e7906429d9323ae4c654861d4c4b1849961abad6aa`
for `mbe_eval/orthogonal.py`. Experiment 29 later added the repeated-split API
to that live module, changing its hash without changing the earlier estimator.
The exact frozen v2 source remained available at:

`experiments/22_orthogonal_score_development/out_development_v2_100_finalists/source_snapshot/orthogonal_v2.py`

That snapshot matches the earlier hash exactly. The packet validator now
resolves this one declared historical path to the immutable snapshot while
also reporting the hash of the current live module. No frozen experiment
manifest, result ledger, threshold, seed, or scientific conclusion was changed.

## Python 3.9 Portability

Public CI run `32584907286` showed that two frozen source files used
`zip(..., strict=True)`, which is unavailable on the package's advertised
Python 3.9 floor. Their exact pre-fix bytes are retained at:

- `experiments/23_conditional_comparator_benchmark/source_snapshot/comparators_frozen_v1.py`
- `experiments/21_design_matched_calibration/source_snapshot/run_calibration_frozen_v1.py`

The snapshots match the original frozen hashes
`caf9f24c76dbf495de08da4d3adaaa61a1f572b1d416a822118c96f5e662f421`
and
`d74c90dbdb8c2179342390bfe1a971584a9daf62ff3eb698b980db14b2139568`.
The live files now perform the same length checks explicitly before ordinary
`zip`, preserving behavior on Python 3.9. The packet validator resolves the
historical hashes to these snapshots and reports current live hashes
separately.

No experimental setting, row, threshold, seed, result, or interpretation was
changed. The packet envelope was rehashed after this amendment.
