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
