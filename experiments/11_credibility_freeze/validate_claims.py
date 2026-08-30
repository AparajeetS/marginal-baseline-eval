from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def _filtered(frame: pd.DataFrame, filters: dict[str, object]) -> pd.DataFrame:
    selected = frame
    for column, value in filters.items():
        if column not in selected:
            raise ValueError(f"missing assertion column: {column}")
        if isinstance(value, bool):
            normalized = selected[column].astype(str).str.lower().map(
                {"true": True, "false": False}
            )
            selected = selected.loc[normalized == value]
        else:
            selected = selected.loc[selected[column] == value]
    return selected


def validate_check(root: Path, check: dict[str, object]) -> None:
    path = root / str(check["path"])
    if not path.is_file():
        raise FileNotFoundError(path)
    kind = check["type"]
    if kind == "file_exists":
        return
    if kind == "json_equals":
        payload = json.loads(path.read_text(encoding="utf-8"))
        observed: object = payload
        for component in str(check["field"]).split("."):
            if not isinstance(observed, dict) or component not in observed:
                raise ValueError(f"missing JSON assertion field: {check['field']}")
            observed = observed[component]
        if observed != check["value"]:
            raise AssertionError(
                f"{path}: observed {check['field']}={observed!r}, "
                f"expected {check['value']!r}"
            )
        return
    frame = pd.read_csv(path)
    selected = _filtered(frame, dict(check.get("filters", {})))
    if selected.empty:
        raise AssertionError(f"claim check selected no rows in {path}")
    if kind == "csv_max":
        observed = float(selected[str(check["column"])].max())
        if observed > float(check["value"]):
            raise AssertionError(f"{path}: observed max {observed} exceeds {check['value']}")
    elif kind == "csv_min":
        observed = float(selected[str(check["column"])].min())
        if observed < float(check["value"]):
            raise AssertionError(f"{path}: observed min {observed} is below {check['value']}")
    elif kind == "csv_count_equals":
        observed = int((selected[str(check["column"])] == check["equals"]).sum())
        if observed != int(check["value"]):
            raise AssertionError(f"{path}: observed count {observed}, expected {check['value']}")
    else:
        raise ValueError(f"unknown check type: {kind}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Fail when public MBE claims outrun evidence.")
    parser.add_argument("ledger", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    ledger = json.loads(args.ledger.read_text(encoding="utf-8"))
    valid_statuses = {"supported", "provisional", "blocked", "withdrawn"}
    for claim in ledger["claims"]:
        if claim["status"] not in valid_statuses:
            raise ValueError(f"invalid status for {claim['id']}")
        if claim["status"] == "supported" and not claim.get("checks"):
            raise ValueError(f"supported claim {claim['id']} has no machine check")
        for check in claim.get("checks", []):
            validate_check(root, check)
    counts = pd.Series([claim["status"] for claim in ledger["claims"]]).value_counts()
    print(counts.to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
