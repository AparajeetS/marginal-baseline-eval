from .core import (
    MBEEvaluator,
    MBEReport,
    audit_metric,
    audit_metrics,
    classify_effect,
    partial_rank_corr,
    spearman_corr,
)
from .reporting import audit_report_markdown, summarize_audit, write_markdown_report

__version__ = "0.4.0.dev0"

__all__ = [
    "__version__",
    "MBEEvaluator",
    "MBEReport",
    "audit_csv",
    "audit_claim_csv",
    "audit_benchmark_claim",
    "audit_report_markdown",
    "audit_metric",
    "audit_metrics",
    "classify_effect",
    "claim_card_json",
    "claim_card_markdown",
    "compare_benchmark_claim_specs",
    "cross_fitted_audit",
    "leave_one_environment_out_audit",
    "make_claim_demo",
    "make_demo_runs",
    "partial_rank_corr",
    "run_demo",
    "run_claim_demo",
    "summarize_audit",
    "spearman_corr",
    "simulate_mbe_evaluation",
    "write_markdown_report",
]


def __getattr__(name):
    if name == "simulate_mbe_evaluation":
        from .sample_eval import simulate_mbe_evaluation

        return simulate_mbe_evaluation
    if name == "audit_csv":
        from .cli import audit_csv

        return audit_csv
    if name == "audit_claim_csv":
        from .claim_cli import audit_claim_csv

        return audit_claim_csv
    if name in {"audit_benchmark_claim", "claim_card_json", "claim_card_markdown"}:
        from .claim_card import (
            audit_benchmark_claim,
            claim_card_json,
            claim_card_markdown,
        )

        return {
            "audit_benchmark_claim": audit_benchmark_claim,
            "claim_card_json": claim_card_json,
            "claim_card_markdown": claim_card_markdown,
        }[name]
    if name == "compare_benchmark_claim_specs":
        from .contestation import compare_benchmark_claim_specs

        return compare_benchmark_claim_specs
    if name == "cross_fitted_audit":
        from .crossfit import cross_fitted_audit

        return cross_fitted_audit
    if name == "leave_one_environment_out_audit":
        from .transport import leave_one_environment_out_audit

        return leave_one_environment_out_audit
    if name in {"make_claim_demo", "run_claim_demo"}:
        from .claim_demo import make_claim_demo, run_claim_demo

        return {"make_claim_demo": make_claim_demo, "run_claim_demo": run_claim_demo}[name]
    if name in {"make_demo_runs", "run_demo"}:
        from .demo import make_demo_runs, run_demo

        return {"make_demo_runs": make_demo_runs, "run_demo": run_demo}[name]
    raise AttributeError(f"module 'mbe_eval' has no attribute {name!r}")
