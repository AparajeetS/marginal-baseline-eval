from __future__ import annotations

import argparse
from hashlib import sha256
from pathlib import Path

import pandas as pd

from . import __version__
from .claim_card import (
    audit_benchmark_claim,
    claim_card_json,
    claim_card_markdown,
)


def _split_csv_arg(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


def audit_claim_csv(
    csv_path: str | Path,
    *,
    claim_id: str,
    claim_text: str,
    metric: str,
    target: str,
    baselines: list[str],
    environment: str,
    unit: str,
    deceptive_control: str | None = None,
    negative_controls: list[str] | None = None,
    min_relative_mse_improvement: float | None = None,
    min_transport_relative_mse_improvement: float | None = None,
    n_splits: int = 5,
    degree: int = 2,
    ridge: float = 1e-3,
    permutations: int = 0,
    bootstrap: int = 0,
    seed: int = 0,
    source_url: str = "",
    source_version: str = "",
    output_prefix: str | Path | None = "mbe_benchmark_claim",
) -> dict[str, object]:
    """Audit a benchmark claim from CSV and optionally write JSON/Markdown."""

    source_path = Path(csv_path)
    source_bytes = source_path.read_bytes()
    frame = pd.read_csv(source_path)
    card = audit_benchmark_claim(
        frame,
        claim_id=claim_id,
        claim_text=claim_text,
        metric=metric,
        target=target,
        baselines=baselines,
        environment=environment,
        unit=unit,
        deceptive_control=deceptive_control,
        negative_controls=negative_controls or (),
        min_relative_mse_improvement=min_relative_mse_improvement,
        min_transport_relative_mse_improvement=(
            min_transport_relative_mse_improvement
        ),
        n_splits=n_splits,
        degree=degree,
        ridge=ridge,
        permutations=permutations,
        bootstrap=bootstrap,
        seed=seed,
    )
    card["source"] = {
        "file": source_path.name,
        "sha256": sha256(source_bytes).hexdigest(),
        "url": source_url or None,
        "version": source_version or None,
    }

    if output_prefix:
        prefix = Path(output_prefix)
        prefix.parent.mkdir(parents=True, exist_ok=True)
        prefix.with_suffix(".json").write_text(
            claim_card_json(card), encoding="utf-8"
        )
        prefix.with_suffix(".md").write_text(
            claim_card_markdown(card), encoding="utf-8"
        )
    return card


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Create an experimental, scoped MBE benchmark-claim audit. "
            "Outputs are diagnostics, not certification."
        )
    )
    parser.add_argument("--version", action="version", version=f"mbe-eval {__version__}")
    parser.add_argument("--csv", required=True, help="CSV with one row per evaluation.")
    parser.add_argument("--claim-id", default="benchmark-claim", help="Stable claim identifier.")
    parser.add_argument(
        "--claim-text",
        default="",
        help="Exact scoped claim being audited.",
    )
    parser.add_argument("--metric", required=True, help="Candidate benchmark-score column.")
    parser.add_argument("--target", required=True, help="Named external outcome column.")
    parser.add_argument(
        "--baselines",
        "--controls",
        dest="baselines",
        required=True,
        help="Comma-separated declared baseline or capability-proxy columns.",
    )
    parser.add_argument(
        "--environment",
        required=True,
        help="Column defining held-out transport environments.",
    )
    parser.add_argument(
        "--unit",
        required=True,
        help="Configuration or model unit used to block repeated observations.",
    )
    parser.add_argument(
        "--deceptive-control",
        default="",
        help="Optional deliberately confounded score column.",
    )
    parser.add_argument(
        "--negative-controls",
        default="",
        help="Optional comma-separated negative-control columns.",
    )
    parser.add_argument(
        "--min-relative-improvement",
        type=float,
        default=None,
        help="Predeclared minimum E1 relative MSE improvement (must be positive).",
    )
    parser.add_argument(
        "--min-transport-relative-improvement",
        type=float,
        default=None,
        help="Predeclared minimum E2 relative MSE improvement (must be positive).",
    )
    parser.add_argument("--n-splits", type=int, default=5, help="Grouped E1 folds.")
    parser.add_argument("--degree", type=int, default=2, help="Polynomial nuisance degree.")
    parser.add_argument("--ridge", type=float, default=1e-3, help="Ridge penalty.")
    parser.add_argument("--permutations", type=int, default=0, help="Permutation draws.")
    parser.add_argument("--bootstrap", type=int, default=0, help="Block bootstrap draws.")
    parser.add_argument("--seed", type=int, default=0, help="Deterministic random seed.")
    parser.add_argument("--source-url", default="", help="Public source URL for the input.")
    parser.add_argument("--source-version", default="", help="Dataset/version identifier.")
    parser.add_argument(
        "--output-prefix",
        default="mbe_benchmark_claim",
        help="Output prefix for .json and .md files.",
    )
    args = parser.parse_args(argv)

    card = audit_claim_csv(
        args.csv,
        claim_id=args.claim_id,
        claim_text=args.claim_text,
        metric=args.metric,
        target=args.target,
        baselines=_split_csv_arg(args.baselines),
        environment=args.environment,
        unit=args.unit,
        deceptive_control=args.deceptive_control or None,
        negative_controls=_split_csv_arg(args.negative_controls),
        min_relative_mse_improvement=args.min_relative_improvement,
        min_transport_relative_mse_improvement=(
            args.min_transport_relative_improvement
        ),
        n_splits=args.n_splits,
        degree=args.degree,
        ridge=args.ridge,
        permutations=args.permutations,
        bootstrap=args.bootstrap,
        seed=args.seed,
        source_url=args.source_url,
        source_version=args.source_version,
        output_prefix=args.output_prefix,
    )
    print(f"Predeclared test outcome: {card['evidence_state']}")
    print(f"Wrote {Path(args.output_prefix).with_suffix('.json').resolve()}")
    print(f"Wrote {Path(args.output_prefix).with_suffix('.md').resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = ["audit_claim_csv", "main"]
