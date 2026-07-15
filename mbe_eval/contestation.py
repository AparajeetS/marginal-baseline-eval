from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pandas as pd

from .claim_card import audit_benchmark_claim


CONTESTATION_SCHEMA_VERSION = "mbe-benchmark-contestation-bundle/0.1"


def _specification_name(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("specification names must be non-empty strings")
    return value.strip()


def _estimand_states(card: Mapping[str, object]) -> dict[str, str]:
    evidence = card.get("evidence")
    if not isinstance(evidence, Mapping):
        raise RuntimeError("claim-card result is missing evidence")
    states: dict[str, str] = {}
    for estimand in ("E0", "E1", "E2", "E3", "E4"):
        result = evidence.get(estimand)
        if not isinstance(result, Mapping) or not isinstance(result.get("state"), str):
            raise RuntimeError(f"claim-card result is missing {estimand} state")
        states[estimand] = str(result["state"])
    return states


def compare_benchmark_claim_specs(
    df: pd.DataFrame,
    specifications: Mapping[str, Mapping[str, object]],
    *,
    common: Mapping[str, object] | None = None,
) -> dict[str, object]:
    """Run named alternative claim specifications and expose conclusion changes.

    ``common`` holds arguments shared by every call to
    :func:`audit_benchmark_claim`. Each named specification overrides those
    arguments. The returned bundle includes the complete claim card for every
    specification so a reviewer can inspect, reproduce, and challenge the
    differences rather than seeing only a collapsed verdict.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")
    if not isinstance(specifications, Mapping) or len(specifications) < 2:
        raise ValueError("specifications must contain at least two named alternatives")
    if common is None:
        shared: dict[str, Any] = {}
    elif isinstance(common, Mapping):
        shared = dict(common)
    else:
        raise TypeError("common must be a mapping")
    if "df" in shared:
        raise ValueError("df must be supplied only as the first function argument")

    cards: dict[str, dict[str, object]] = {}
    summaries: dict[str, dict[str, object]] = {}
    for raw_name, overrides in specifications.items():
        name = _specification_name(raw_name)
        if name in cards:
            raise ValueError(f"duplicate normalized specification name: {name!r}")
        if not isinstance(overrides, Mapping):
            raise TypeError(f"specification {name!r} must be a mapping")
        if "df" in overrides:
            raise ValueError("df cannot be overridden by a specification")
        arguments = {**shared, **dict(overrides)}
        card = audit_benchmark_claim(df, **arguments)
        states = _estimand_states(card)
        cards[name] = card
        summaries[name] = {
            "evidence_state": card["evidence_state"],
            "estimand_states": states,
            "claim": card["claim"],
            "declarations": card["declarations"],
        }

    names = list(cards)
    reference = names[0]
    reference_summary = summaries[reference]
    reference_signature = (
        reference_summary["evidence_state"],
        tuple(reference_summary["estimand_states"].items()),  # type: ignore[union-attr]
    )
    changed: list[str] = []
    for name in names[1:]:
        summary = summaries[name]
        signature = (
            summary["evidence_state"],
            tuple(summary["estimand_states"].items()),  # type: ignore[union-attr]
        )
        if signature != reference_signature:
            changed.append(name)

    distinct_overall_states = sorted(
        {str(summary["evidence_state"]) for summary in summaries.values()}
    )
    return {
        "schema_version": CONTESTATION_SCHEMA_VERSION,
        "method_status": "experimental",
        "reference_specification": reference,
        "conclusion_changed": bool(changed),
        "overall_evidence_state_changed": len(distinct_overall_states) > 1,
        "changed_specifications": changed,
        "distinct_overall_evidence_states": distinct_overall_states,
        "specifications": summaries,
        "claim_cards": cards,
        "limitations": [
            "This bundle compares only the supplied specifications.",
            "An unchanged outcome does not show robustness to untested alternatives.",
            "A changed outcome identifies specification sensitivity for review; it does "
            "not choose which specification is preferable.",
        ],
    }


__all__ = ["CONTESTATION_SCHEMA_VERSION", "compare_benchmark_claim_specs"]
