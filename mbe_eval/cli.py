from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from .core import audit_metrics
from .reporting import summarize_audit, write_markdown_report
from . import __version__


def _split_csv_arg(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


def audit_csv(
    csv_path: str | Path,
    *,
    metrics: list[str],
    target: str,
    controls: list[str],
    groupby: list[str] | None = None,
    inference_unit_col: str | None = None,
    bootstrap: int = 0,
    seed: int = 0,
    include_pooled: bool = True,
    output: str | Path | None = None,
    results: str | Path | None = None,
) -> pd.DataFrame:
    """Audit metrics from a CSV training-run ledger."""

    df = pd.read_csv(csv_path)
    report = audit_metrics(
        df,
        metrics=metrics,
        target=target,
        controls=controls,
        groupby=groupby or None,
        inference_unit_col=inference_unit_col,
        bootstrap=bootstrap,
        seed=seed,
        include_pooled=include_pooled,
    )
    if output:
        write_markdown_report(
            report,
            output,
            title="MBE CSV Audit Report",
            target=target,
            controls=controls,
            notes=[f"Source CSV: `{csv_path}`"],
        )
    if results:
        results_path = Path(results)
        results_path.parent.mkdir(parents=True, exist_ok=True)
        if results_path.suffix.lower() == ".json":
            results_path.write_text(
                report.to_json(orient="records", indent=2), encoding="utf-8"
            )
        elif results_path.suffix.lower() == ".csv":
            report.to_csv(results_path, index=False)
        else:
            raise ValueError("results path must end in .csv or .json")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit training metrics from a CSV ledger.")
    parser.add_argument("--version", action="version", version=f"mbe-eval {__version__}")
    parser.add_argument("--csv", required=True, help="CSV with one row per trained run/model.")
    parser.add_argument("--metrics", required=True, help="Comma-separated candidate metric columns.")
    parser.add_argument("--target", required=True, help="Held-out target column.")
    parser.add_argument("--controls", required=True, help="Comma-separated baseline/control columns.")
    parser.add_argument(
        "--groupby",
        default="",
        help="Optional comma-separated stratification columns.",
    )
    parser.add_argument(
        "--inference-unit",
        default="",
        help="Optional column defining independent clusters for bootstrap inference.",
    )
    parser.add_argument("--bootstrap", type=int, default=0, help="Bootstrap resamples.")
    parser.add_argument("--seed", type=int, default=0, help="Bootstrap random seed.")
    parser.add_argument(
        "--no-pooled", action="store_true", help="Only emit grouped audit rows."
    )
    parser.add_argument("--output", default="", help="Optional markdown report path.")
    parser.add_argument(
        "--results", default="", help="Optional machine-readable .csv or .json results path."
    )
    args = parser.parse_args(argv)

    try:
        report = audit_csv(
            args.csv,
            metrics=_split_csv_arg(args.metrics),
            target=args.target,
            controls=_split_csv_arg(args.controls),
            groupby=_split_csv_arg(args.groupby),
            inference_unit_col=args.inference_unit or None,
            bootstrap=args.bootstrap,
            seed=args.seed,
            include_pooled=not args.no_pooled,
            output=args.output or None,
            results=args.results or None,
        )
    except (FileNotFoundError, ValueError) as error:
        parser.error(str(error))
    print(summarize_audit(report).to_string(index=False))
    if args.output:
        print(f"\nWrote {Path(args.output).resolve()}")
    if args.results:
        print(f"Wrote {Path(args.results).resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = ["audit_csv", "main"]
