from __future__ import annotations

import argparse
import hashlib
import json
import statistics
from collections import Counter
from pathlib import Path
from typing import Any


FILES = (
    "sycophancy_on_nlp_survey.jsonl",
    "sycophancy_on_philpapers2020.jsonl",
    "sycophancy_on_political_typology_quiz.jsonl",
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _normalize(text: str) -> str:
    return " ".join(text.split())


def _base_unit(filename: str, question: str) -> str:
    """Return a conservative repeated-source-question identifier.

    NLP and philosophy records contain stable source-question markers. The
    political records do not expose a separate source-question field, so their
    answer-choice block is used as the repeat identifier. This is sufficient
    to prevent generated biography variants from being treated as independent
    source questions, but it is not a claim that the extraction restores every
    word of the original Pew item.
    """

    if filename == "sycophancy_on_nlp_survey.jsonl":
        marker = "Do you agree or disagree with the following claim"
        start = question.find(marker)
        if start < 0:
            raise ValueError(f"NLP source-question marker missing: {question[:80]!r}")
        return _normalize(question[start:])

    if filename == "sycophancy_on_philpapers2020.jsonl":
        marker = "What is your view on the following topic:"
        start = question.find(marker)
        if start < 0:
            raise ValueError(
                f"PhilPapers source-question marker missing: {question[:80]!r}"
            )
        return _normalize(question[start:])

    choices_marker = "\n (A)"
    start = question.rfind(choices_marker)
    if start < 0:
        raise ValueError(f"Political answer-choice block missing: {question[:80]!r}")
    return _normalize(question[start:])


def _not_matching_values(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return value
    raise TypeError("answer_not_matching_behavior must be a string or list of strings")


def inspect_file(path: Path) -> dict[str, Any]:
    required = {
        "question",
        "answer_matching_behavior",
        "answer_not_matching_behavior",
    }
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSON") from exc
            missing = required.difference(row)
            if missing:
                raise ValueError(f"{path}:{line_number}: missing {sorted(missing)}")
            rows.append(row)

    questions = [str(row["question"]) for row in rows]
    base_units = [_base_unit(path.name, question) for question in questions]
    repeats = Counter(base_units)
    matching = Counter(str(row["answer_matching_behavior"]) for row in rows)
    not_matching_types = Counter(
        "list" if isinstance(row["answer_not_matching_behavior"], list) else "string"
        for row in rows
    )
    collisions = 0
    for row in rows:
        if str(row["answer_matching_behavior"]) in _not_matching_values(
            row["answer_not_matching_behavior"]
        ):
            collisions += 1

    affiliations = Counter(
        str(row["user_affiliation"])
        for row in rows
        if "user_affiliation" in row
    )
    repeat_counts = list(repeats.values())

    return {
        "path": f"sycophancy/{path.name}",
        "sha256": _sha256(path),
        "rows": len(rows),
        "unique_full_prompts": len(set(questions)),
        "exact_duplicate_prompts": len(rows) - len(set(questions)),
        "extracted_source_units": len(repeats),
        "generated_variants_per_source_unit": {
            "minimum": min(repeat_counts),
            "median": statistics.median(repeat_counts),
            "maximum": max(repeat_counts),
        },
        "matching_answer_counts": dict(sorted(matching.items())),
        "not_matching_field_types": dict(sorted(not_matching_types.items())),
        "matching_not_matching_collisions": collisions,
        "user_affiliation_counts": dict(sorted(affiliations.items())),
    }


def inspect_source(source_root: Path, source_commit: str) -> dict[str, Any]:
    sycophancy_root = source_root / "sycophancy"
    missing = [name for name in FILES if not (sycophancy_root / name).is_file()]
    if missing:
        raise FileNotFoundError(f"missing required source files: {missing}")

    files = [inspect_file(sycophancy_root / name) for name in FILES]
    return {
        "source": "https://github.com/anthropics/evals",
        "source_commit": source_commit,
        "inspection_scope": "released sycophancy prompt and label files only",
        "candidate_result_computed": False,
        "files": files,
        "totals": {
            "rows": sum(item["rows"] for item in files),
            "unique_full_prompts": sum(item["unique_full_prompts"] for item in files),
            "extracted_source_units": sum(
                item["extracted_source_units"] for item in files
            ),
        },
        "independence_warning": (
            "Rows are generated biography variants. They must not be treated as "
            "independent source questions in inference or random row-level splits."
        ),
        "data_gap": (
            "The release contains prompts and behavior-matching answer labels, "
            "but no model responses, token probabilities, model metadata, or "
            "external per-example outcome target."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Inspect the pinned Anthropic sycophancy source before any candidate "
            "benchmark result is computed."
        )
    )
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    report = inspect_source(args.source_root, args.source_commit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"Inspected {report['totals']['rows']} rows without computing a candidate result")
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

