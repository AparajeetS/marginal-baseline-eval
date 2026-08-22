# Artifact Integrity And Lineage

This repository preserves both current evidence and the failed or superseded
states that led to it. A SHA-256 file is therefore a point-in-time receipt, not
automatically a checksum of every file at its present-day path.

## How To Read The Hash Records

- Output-local `SHA256SUMS` files protect the canonical ledgers, summaries,
  manifests, and diagnostics produced by that run.
- `FROZEN_SHA256SUMS` records protect the preregistered code and protocol used
  when a campaign was launched.
- Files marked `FAILED`, `V1`, `RECOVERY`, or `LOCAL_SYNC` intentionally retain
  an earlier attempt. They must be interpreted with the adjacent recovery log
  or provenance record, not as validators for a later corrected output at the
  same path.
- Living documents and package code can change after a campaign. Historical
  campaign manifests retain their original hashes; source snapshots or the
  replication-packet amendment identify the exact historical implementation.
- A checksum file that includes its own path is retained as historical output,
  but its self-entry is not a meaningful verification gate.

## Current Verification Path

For a clean review, use the experiment-specific validator or output-local
checksum first, then read the preregistration and completion report. The main
entry points are indexed in [EVIDENCE_INDEX.md](EVIDENCE_INDEX.md) and the
cross-platform reproduction steps are in
[REPRODUCIBILITY.md](../REPRODUCIBILITY.md).

The independent-replication packet provides the smallest portable verification
surface. Its amendment maps the historical orthogonal-score implementation to
the committed source snapshot without rewriting the frozen campaign records.
See
[`PACKET_V2_AMENDMENT_2026-08-22.md`](../experiments/12_independent_replication/PACKET_V2_AMENDMENT_2026-08-22.md).

Git remains the release-level content-addressed record. The repository forces
research text, source, and tabular artifacts to LF line endings so a Windows
checkout does not silently invalidate hashes created on Linux.
