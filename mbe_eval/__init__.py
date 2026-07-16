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
from .crossfit import (
    classify_increment_evidence,
    cross_fitted_audit,
    repeated_cross_fitted_audit,
)
from .calibration import make_calibration_ledger, run_calibration, run_monte_carlo_calibration
from .reaudit import run_manifest_reaudit, run_published_reaudit, validate_study_manifest
from .robust_sign_error import robust_sign_error_environments, robust_sign_error_summary
from .checkpoint_metrics import summarize_checkpoint_pair
from .selection import (
    coverage_regret_curve,
    leave_one_task_out_global_choice,
    score_recommendations,
)

__version__ = "0.3.2"

__all__ = [
    "__version__",
    "MBEEvaluator",
    "MBEReport",
    "audit_csv",
    "audit_report_markdown",
    "audit_metric",
    "audit_metrics",
    "classify_effect",
    "cross_fitted_audit",
    "classify_increment_evidence",
    "repeated_cross_fitted_audit",
    "make_demo_runs",
    "make_calibration_ledger",
    "partial_rank_corr",
    "run_demo",
    "run_calibration",
    "run_monte_carlo_calibration",
    "run_manifest_reaudit",
    "run_published_reaudit",
    "robust_sign_error_environments",
    "robust_sign_error_summary",
    "summarize_audit",
    "spearman_corr",
    "summarize_checkpoint_pair",
    "coverage_regret_curve",
    "leave_one_task_out_global_choice",
    "score_recommendations",
    "simulate_mbe_evaluation",
    "validate_study_manifest",
    "write_markdown_report",
]


def __getattr__(name):
    if name == "simulate_mbe_evaluation":
        from .sample_eval import simulate_mbe_evaluation

        return simulate_mbe_evaluation
    if name == "audit_csv":
        from .cli import audit_csv

        return audit_csv
    if name in {"make_demo_runs", "run_demo"}:
        from .demo import make_demo_runs, run_demo

        return {"make_demo_runs": make_demo_runs, "run_demo": run_demo}[name]
    raise AttributeError(f"module 'mbe_eval' has no attribute {name!r}")
