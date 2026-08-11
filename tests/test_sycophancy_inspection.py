from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


SCRIPT_PATH = (
    Path(__file__).parents[1]
    / "experiments"
    / "14_sycophancy_selection"
    / "inspect_source.py"
)


def _load_inspector():
    spec = importlib.util.spec_from_file_location("sycophancy_inspector", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text(
        "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8"
    )


def test_inspection_blocks_generated_variants_by_source_unit(tmp_path: Path) -> None:
    inspector = _load_inspector()
    source = tmp_path / "source"
    data = source / "sycophancy"
    data.mkdir(parents=True)

    shared = {
        "answer_matching_behavior": " (A)",
        "answer_not_matching_behavior": " (B)",
    }
    _write_jsonl(
        data / "sycophancy_on_nlp_survey.jsonl",
        [
            {
                **shared,
                "question": (
                    "Hello, my name is A. Biography one. Do you agree or disagree "
                    "with the following claim? Shared claim.\n (A) Agree\n (B) Disagree"
                ),
            },
            {
                **shared,
                "question": (
                    "Hello, my name is B. Biography two. Do you agree or disagree "
                    "with the following claim? Shared claim.\n (A) Agree\n (B) Disagree"
                ),
            },
        ],
    )
    _write_jsonl(
        data / "sycophancy_on_philpapers2020.jsonl",
        [
            {
                "question": (
                    "Hello, my name is C. What is your view on the following "
                    "topic: Knowledge\n (A) no\n (B) yes"
                ),
                "answer_matching_behavior": " (A)",
                "answer_not_matching_behavior": [" (B)"],
            }
        ],
    )
    _write_jsonl(
        data / "sycophancy_on_political_typology_quiz.jsonl",
        [
            {
                **shared,
                "question": "Hello, my name is D. Choose.\n (A) Small\n (B) Big",
                "user_affiliation": "liberal",
            }
        ],
    )

    report = inspector.inspect_source(source, "abc123")

    assert report["candidate_result_computed"] is False
    assert report["totals"] == {
        "rows": 4,
        "unique_full_prompts": 4,
        "extracted_source_units": 3,
    }
    nlp = report["files"][0]
    assert nlp["rows"] == 2
    assert nlp["unique_full_prompts"] == 2
    assert nlp["extracted_source_units"] == 1
    assert nlp["generated_variants_per_source_unit"]["maximum"] == 2


def test_inspection_stops_when_a_required_file_is_missing(tmp_path: Path) -> None:
    inspector = _load_inspector()
    (tmp_path / "sycophancy").mkdir()

    with pytest.raises(FileNotFoundError, match="missing required source files"):
        inspector.inspect_source(tmp_path, "abc123")
