# Replication Packet V2 Provenance Amendment

Recorded: 2026-08-22, before public release or external execution.

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
The packet envelope was rehashed after this amendment.
