# Independent Replication Workflow

This directory turns the replication protocol into an executable audit. It does
not make an internal run independent; the reviewer must satisfy
`docs/INDEPENDENT_REPLICATION_PROTOCOL.md` and sign the generated report.

```bash
python experiments/12_independent_replication/run_replication_audit.py \
  --reviewer "Full Name" \
  --conflict-statement "No prior contribution; no protected outcomes seen" \
  --output-dir external_replication_report
```

The command verifies frozen hashes, validates public claim gates, runs the test
suite, records the commit and dirty paths, and creates JSON and Markdown reports.
The reviewer then adds discrepancies and a signed conclusion regardless of
whether replication succeeds.

## Current V2 Packet

The current clean handoff validates the comparator and orthogonal/PGDL
calibration sequence without exposing protected associations:

```bash
python experiments/12_independent_replication/validate_packet_v2.py \
  --reviewer "EXTERNAL REVIEWER" \
  --conflict-statement "DISCLOSE CONFLICTS OR WRITE NONE" \
  --output-dir external_replication_v2 \
  --run-tests
```

This command verifies frozen inputs, generated artifact hashes, exact table
row counts, duplicate keys, the sealed opening decisions, and the full test
suite. `PACKET_V2_SHA256SUMS` seals the handoff files themselves. The packet is
prepared but has not yet been independently executed or signed.
