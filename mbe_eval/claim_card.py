from __future__ import annotations

import json
import math
from numbers import Integral, Real
from pathlib import Path
from typing import Mapping, Sequence

import numpy as np
import pandas as pd
from pandas.api.types import is_bool_dtype, is_numeric_dtype

from .core import audit_metric
from .crossfit import cross_fitted_audit
from .transport import leave_one_environment_out_audit


SCHEMA_VERSION = "mbe-benchmark-claim-card/0.2"
EVIDENCE_STATES = {
    "supports-claim-under-declared-tests",
    "does-not-support-claim-under-declared-tests",
    "unresolved-under-declared-tests",
}
ESTIMAND_STATES = {
    "meets-declared-threshold",
    "below-declared-threshold",
    "unresolved",
}

# Deprecated Python-level alias. Claim-card output never emits ``claim_status``.
CLAIM_STATUSES = EVIDENCE_STATES


def _require_name(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")
    return value.strip()


def _require_names(values: Sequence[str], label: str, *, allow_empty: bool) -> list[str]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        raise TypeError(f"{label} must be a sequence of column names")
    result = [_require_name(value, label) for value in values]
    if not allow_empty and not result:
        raise ValueError(f"{label} must contain at least one column")
    if len(set(result)) != len(result):
        raise ValueError(f"{label} must not contain duplicate columns")
    return result


def _require_non_negative_integer(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, Integral) or value < 0:
        raise ValueError(f"{label} must be a non-negative integer")
    return int(value)


def _require_positive_threshold(value: object, label: str) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{label} must be a finite positive number")
    value = float(value)
    if not np.isfinite(value) or value <= 0:
        raise ValueError(f"{label} must be a finite positive number")
    return value


def _finite(value: object) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _looks_like_direct_target_leakage(
    frame: pd.DataFrame, predictor: str, target: str
) -> bool:
    paired = frame[[predictor, target]].replace([np.inf, -np.inf], np.nan).dropna()
    if len(paired) < 3:
        return False
    predictor_values = paired[predictor].to_numpy(dtype=float)
    target_values = paired[target].to_numpy(dtype=float)
    return bool(np.allclose(predictor_values, target_values, rtol=0.0, atol=1e-12))


def _estimand_state(result: Mapping[str, object], threshold: float | None) -> str:
    if threshold is None:
        return "unresolved"
    baseline_mse = _finite(result.get("baseline_mse"))
    relative = _finite(result.get("relative_mse_improvement"))
    ci_low = _finite(result.get("delta_mse_ci_low"))
    ci_high = _finite(result.get("delta_mse_ci_high"))
    if baseline_mse is None or baseline_mse <= 0 or relative is None:
        return "unresolved"
    absolute_threshold = threshold * baseline_mse
    if relative >= threshold and ci_low is not None and ci_low >= absolute_threshold:
        return "meets-declared-threshold"
    if ci_high is not None and ci_high < absolute_threshold:
        return "below-declared-threshold"
    return "unresolved"


def _audit_score(
    frame: pd.DataFrame,
    *,
    score: str,
    target: str,
    baselines: Sequence[str],
    environment: str,
    unit: str,
    min_relative_mse_improvement: float | None,
    min_transport_relative_mse_improvement: float | None,
    n_splits: int,
    degree: int,
    ridge: float,
    permutations: int,
    bootstrap: int,
    seed: int,
) -> dict[str, object]:
    e1_controls = [*baselines, environment]
    descriptive = audit_metric(
        frame,
        score,
        target,
        e1_controls,
        group="pooled",
        bootstrap=0,
        seed=seed,
    )
    e1 = cross_fitted_audit(
        frame,
        score,
        target,
        e1_controls,
        group_col=unit,
        n_splits=n_splits,
        degree=degree,
        ridge=ridge,
        permutations=permutations,
        bootstrap=bootstrap,
        seed=seed,
    )
    e2 = leave_one_environment_out_audit(
        frame,
        score,
        target,
        baselines,
        environment=environment,
        degree=degree,
        ridge=ridge,
        permutations=permutations,
        bootstrap=bootstrap,
        seed=seed + 10_003,
    )
    e1_state = _estimand_state(e1, min_relative_mse_improvement)
    e2_state = _estimand_state(e2, min_transport_relative_mse_improvement)
    return {
        "E0": {
            "name": "unconditional-association",
            "state": "unresolved",
            "role": "descriptive-diagnostic",
            "n": descriptive["n"],
            "raw_rank_correlation": descriptive["raw_r"],
            "raw_p_value": descriptive["raw_p"],
            "descriptive_partial_rank_correlation": descriptive["partial_r"],
            "descriptive_classification": descriptive["classification"],
        },
        "E1": {
            "name": "incremental-utility-given-declared-baselines",
            "state": e1_state,
            "result": e1,
        },
        "E2": {
            "name": "aggregate-leave-one-environment-out-transport",
            "state": e2_state,
            "result": e2,
        },
    }


def _overall_evidence_state(
    evidence: Mapping[str, object],
    controls: Mapping[str, object],
    *,
    thresholds_declared: bool,
) -> tuple[str, str]:
    if not thresholds_declared:
        return (
            "unresolved-under-declared-tests",
            "No positive practical thresholds were declared before analysis, so the "
            "prototype does not issue a support judgment.",
        )

    e1_state = evidence["E1"]["state"]  # type: ignore[index]
    e2_state = evidence["E2"]["state"]  # type: ignore[index]
    control_support = []
    for name, control in controls.items():
        control_evidence = control["evidence"]  # type: ignore[index]
        if (
            control_evidence["E1"]["state"] == "meets-declared-threshold"
            or control_evidence["E2"]["state"] == "meets-declared-threshold"
        ):
            control_support.append(name)

    if control_support:
        return (
            "unresolved-under-declared-tests",
            "A declared deceptive or negative control also crossed a support "
            "threshold, so the implementation self-check did not clear.",
        )
    if (
        e1_state == "meets-declared-threshold"
        and e2_state == "meets-declared-threshold"
    ):
        return (
            "supports-claim-under-declared-tests",
            "The candidate crossed the predeclared E1 and aggregate E2 thresholds "
            "in these data while the supplied controls did not. This is conditional "
            "evidence, not certification or construct validity.",
        )
    if (
        e1_state == "below-declared-threshold"
        or e2_state == "below-declared-threshold"
    ):
        return (
            "does-not-support-claim-under-declared-tests",
            "At least one required estimand did not reach its predeclared practical "
            "threshold in these data.",
        )
    return (
        "unresolved-under-declared-tests",
        "The intervals do not resolve the candidate against every predeclared "
        "threshold and transport requirement.",
    )


def audit_benchmark_claim(
    df: pd.DataFrame,
    *,
    claim_id: str = "benchmark-claim",
    claim_text: str = "",
    metric: str,
    target: str,
    baselines: Sequence[str],
    environment: str,
    unit: str,
    deceptive_control: str | None = None,
    negative_controls: Sequence[str] = (),
    min_relative_mse_improvement: float | None = None,
    min_transport_relative_mse_improvement: float | None = None,
    n_splits: int = 5,
    degree: int = 2,
    ridge: float = 1e-3,
    permutations: int = 0,
    bootstrap: int = 0,
    seed: int = 0,
) -> dict[str, object]:
    """Create an experimental, scoped benchmark-claim audit card.

    The method implements selected E0-E2 checks from the candidate MBE 2.0
    specification. It does not validate MBE, certify a benchmark, identify a
    causal effect, or establish that the named score measures its construct.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")
    claim_id = _require_name(claim_id, "claim_id")
    if not isinstance(claim_text, str):
        raise TypeError("claim_text must be a string")
    metric = _require_name(metric, "metric")
    target = _require_name(target, "target")
    environment = _require_name(environment, "environment")
    unit = _require_name(unit, "unit")
    baseline_list = _require_names(baselines, "baselines", allow_empty=False)
    negative_list = _require_names(
        negative_controls, "negative_controls", allow_empty=True
    )
    deceptive = (
        _require_name(deceptive_control, "deceptive_control")
        if deceptive_control is not None
        else None
    )

    role_columns = [metric, target, environment, unit, *baseline_list]
    control_scores = [*([deceptive] if deceptive else []), *negative_list]
    all_declared = [*role_columns, *control_scores]
    if len(set(role_columns)) != len(role_columns):
        raise ValueError(
            "metric, target, environment, unit, and baselines must be distinct columns"
        )
    if len(set(all_declared)) != len(all_declared):
        raise ValueError("deceptive and negative controls must be distinct declared columns")
    missing = [column for column in all_declared if column not in df.columns]
    if missing:
        raise ValueError(f"missing required columns: {', '.join(missing)}")

    for column in [metric, target, *baseline_list, *control_scores]:
        if column in baseline_list and not is_numeric_dtype(df[column]):
            continue
        if column not in baseline_list and (
            not is_numeric_dtype(df[column]) or is_bool_dtype(df[column])
        ):
            raise ValueError(f"score/target column {column!r} must be numeric")

    min_increment = _require_positive_threshold(
        min_relative_mse_improvement, "min_relative_mse_improvement"
    )
    min_transport = _require_positive_threshold(
        min_transport_relative_mse_improvement,
        "min_transport_relative_mse_improvement",
    )
    n_splits = _require_non_negative_integer(n_splits, "n_splits")
    if n_splits < 2:
        raise ValueError("n_splits must be at least 2")
    if isinstance(degree, bool) or not isinstance(degree, Integral) or degree < 1:
        raise ValueError("degree must be a positive integer")
    if isinstance(ridge, bool) or not isinstance(ridge, Real):
        raise ValueError("ridge must be a finite non-negative number")
    ridge = float(ridge)
    if not np.isfinite(ridge) or ridge < 0:
        raise ValueError("ridge must be a finite non-negative number")
    permutations = _require_non_negative_integer(permutations, "permutations")
    bootstrap = _require_non_negative_integer(bootstrap, "bootstrap")
    if isinstance(seed, bool) or not isinstance(seed, Integral):
        raise ValueError("seed must be an integer")

    clean = df[all_declared].replace([np.inf, -np.inf], np.nan).dropna().copy()
    if len(clean) < 20:
        raise ValueError("benchmark claim audit requires at least 20 complete rows")
    if clean[unit].astype(str).nunique() < n_splits:
        raise ValueError("unit column must contain at least n_splits distinct units")
    if clean[environment].astype(str).nunique() < 3:
        raise ValueError("environment column must contain at least three environments")
    for predictor in [metric, *baseline_list, *control_scores]:
        if is_numeric_dtype(clean[predictor]) and _looks_like_direct_target_leakage(
            clean, predictor, target
        ):
            raise ValueError(
                f"column {predictor!r} duplicates the target and fails the leakage guard"
            )

    evidence = _audit_score(
        clean,
        score=metric,
        target=target,
        baselines=baseline_list,
        environment=environment,
        unit=unit,
        min_relative_mse_improvement=min_increment,
        min_transport_relative_mse_improvement=min_transport,
        n_splits=n_splits,
        degree=int(degree),
        ridge=ridge,
        permutations=permutations,
        bootstrap=bootstrap,
        seed=int(seed),
    )

    control_results: dict[str, object] = {}
    for offset, score in enumerate(control_scores, start=1):
        control_results[score] = {
            "kind": "deceptive" if score == deceptive else "negative",
            "evidence": _audit_score(
                clean,
                score=score,
                target=target,
                baselines=baseline_list,
                environment=environment,
                unit=unit,
                min_relative_mse_improvement=min_increment,
                min_transport_relative_mse_improvement=min_transport,
                n_splits=n_splits,
                degree=int(degree),
                ridge=ridge,
                permutations=permutations,
                bootstrap=bootstrap,
                seed=int(seed) + 100_003 * offset,
            ),
        }

    thresholds_declared = min_increment is not None and min_transport is not None
    evidence_state, interpretation = _overall_evidence_state(
        evidence, control_results, thresholds_declared=thresholds_declared
    )
    if evidence_state not in EVIDENCE_STATES:
        raise RuntimeError("internal error: unsupported evidence state")

    return _json_safe(
        {
            "schema_version": SCHEMA_VERSION,
            "method_status": "experimental",
            "independently_validated": False,
            "evidence_state": evidence_state,
            "interpretation": interpretation,
            "claim": {"id": claim_id, "text": claim_text.strip()},
            "declarations": {
                "metric": metric,
                "target": target,
                "declared_baselines_or_capability_proxies": baseline_list,
                "environment": environment,
                "independence_unit": unit,
                "minimum_relative_mse_improvement": min_increment,
                "minimum_transport_relative_mse_improvement": min_transport,
                "n_splits": n_splits,
                "polynomial_degree": int(degree),
                "ridge": ridge,
                "permutations": permutations,
                "bootstrap": bootstrap,
                "seed": int(seed),
            },
            "counts": {
                "input_rows": len(df),
                "complete_rows": len(clean),
                "dropped_rows": len(df) - len(clean),
                "independence_units": int(clean[unit].astype(str).nunique()),
                "environments": int(clean[environment].astype(str).nunique()),
            },
            "evidence": {
                **evidence,
                "E3": {
                    "name": "matched-intervention-consistency",
                    "state": "unresolved",
                    "reason": "not-implemented",
                },
                "E4": {
                    "name": "measurement-reliability-and-cost",
                    "state": "unresolved",
                    "reason": "not-implemented",
                },
            },
            "control_results": control_results,
            "limitations": [
                "Results are conditional on the named outcome, data, split, estimator, "
                "declared baselines, environments, and analysis settings.",
                "Declared capability proxies do not exhaust latent model capability or "
                "all possible confounding.",
                "Empirical rank transforms and numeric scaling are fitted within each "
                "training fold; results remain conditional on the chosen folds and "
                "finite-sample transformations.",
                "The E2 result is an environment-equal aggregate and can hide a failing "
                "individual environment.",
                "E3 interventions and E4 measurement reliability/cost are not implemented.",
                "Association and incremental prediction do not establish causality or "
                "construct validity and do not certify a benchmark or model.",
            ],
            "synthetic_control_caveat": (
                "Synthetic controls test implementation behavior under their chosen "
                "data-generating assumptions. Passing them does not validate MBE or its "
                "real-world benchmark use."
            ),
        }
    )


def _json_safe(value: object) -> object:
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if isinstance(value, np.ndarray):
        return [_json_safe(item) for item in value.tolist()]
    if isinstance(value, (np.integer, Integral)) and not isinstance(value, bool):
        return int(value)
    if isinstance(value, (np.floating, float)):
        number = float(value)
        return round(number, 12) if math.isfinite(number) else None
    if value is pd.NA:
        return None
    return value


def claim_card_json(card: Mapping[str, object]) -> str:
    """Render a deterministic, standards-compliant JSON claim card."""

    return json.dumps(
        _json_safe(card), indent=2, sort_keys=True, allow_nan=False, ensure_ascii=False
    ) + "\n"


def _format_number(value: object) -> str:
    number = _finite(value)
    return "n/a" if number is None else f"{number:+.4f}"


def claim_card_markdown(card: Mapping[str, object]) -> str:
    """Render a human-readable Markdown view of a benchmark claim card."""

    declarations = card["declarations"]
    evidence = card["evidence"]
    claim = card["claim"]
    lines = [
        "# MBE Benchmark Claim Card",
        "",
        "> Experimental research prototype. Not independently validated. This card is "
        "a scoped diagnostic, not certification.",
        "",
        f"**Predeclared test outcome:** `{card['evidence_state']}`",
        "",
        f"**Interpretation:** {card['interpretation']}",
        "",
        "## Scoped Claim",
        "",
        f"- ID: `{claim['id']}`",
        f"- Text: {claim['text'] or '(not supplied)'}",
        f"- Candidate score: `{declarations['metric']}`",
        f"- Named outcome: `{declarations['target']}`",
        "- Declared baselines or capability proxies: "
        + ", ".join(
            f"`{name}`"
            for name in declarations["declared_baselines_or_capability_proxies"]
        ),
        f"- Environment: `{declarations['environment']}`",
        f"- Independence unit: `{declarations['independence_unit']}`",
        "",
        "## Estimand Results",
        "",
        "| ID | Check | Predeclared test outcome | Main quantity |",
        "|---|---|---|---:|",
        "| E0 | Unconditional association | {status} | rho {rho} |".format(
            status=evidence["E0"]["state"],
            rho=_format_number(evidence["E0"]["raw_rank_correlation"]),
        ),
        "| E1 | Increment beyond declared baselines | {status} | relative MSE {value} |".format(
            status=evidence["E1"]["state"],
            value=_format_number(
                evidence["E1"]["result"]["relative_mse_improvement"]
            ),
        ),
        "| E2 | Aggregate environment holdout | {status} | relative MSE {value} |".format(
            status=evidence["E2"]["state"],
            value=_format_number(
                evidence["E2"]["result"]["relative_mse_improvement"]
            ),
        ),
        f"| E3 | Matched interventions | {evidence['E3']['state']} | n/a |",
        f"| E4 | Reliability and cost | {evidence['E4']['state']} | n/a |",
    ]

    controls = card.get("control_results", {})
    if controls:
        lines.extend(
            [
                "",
                "## Declared Control Results",
                "",
                "| Score | Kind | E1 | E2 |",
                "|---|---|---|---|",
            ]
        )
        for name, control in controls.items():
            control_evidence = control["evidence"]
            lines.append(
                f"| `{name}` | {control['kind']} | "
                f"{control_evidence['E1']['state']} | "
                f"{control_evidence['E2']['state']} |"
            )

    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {limitation}" for limitation in card.get("limitations", []))
    lines.extend(
        [
            "",
            "## Synthetic-Control Boundary",
            "",
            str(card["synthetic_control_caveat"]),
            "",
        ]
    )
    return "\n".join(lines)


def write_claim_card_markdown(
    card: Mapping[str, object], output: str | Path
) -> Path:
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(claim_card_markdown(card), encoding="utf-8")
    return path.resolve()


def write_claim_card(
    card: Mapping[str, object], output_prefix: str | Path
) -> tuple[Path, Path]:
    prefix = Path(output_prefix)
    prefix.parent.mkdir(parents=True, exist_ok=True)
    json_path = prefix.with_suffix(".json")
    markdown_path = prefix.with_suffix(".md")
    json_path.write_text(claim_card_json(card), encoding="utf-8")
    markdown_path.write_text(claim_card_markdown(card), encoding="utf-8")
    return json_path.resolve(), markdown_path.resolve()


__all__ = [
    "CLAIM_STATUSES",
    "EVIDENCE_STATES",
    "ESTIMAND_STATES",
    "SCHEMA_VERSION",
    "audit_benchmark_claim",
    "claim_card_json",
    "claim_card_markdown",
    "write_claim_card",
    "write_claim_card_markdown",
]
