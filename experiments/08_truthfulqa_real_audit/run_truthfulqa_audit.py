from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Iterable

import pandas as pd


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from mbe_eval.claim_card import audit_benchmark_claim, write_claim_card  # noqa: E402


SOURCE_COMMIT = "d71c110897f5d31c5d7f309e7bc316c152f6f031"
PROTOCOL_FREEZE_COMMIT = "5db33e4d8afadd9e1df730c7ea006d48902af4b1"
QUESTION_RELATIVE_PATH = Path("data/v1/TruthfulQA.csv")
LABEL_RELATIVE_PATH = Path("data/finetune_truth.jsonl")
EXPECTED_QUESTION_SHA256 = (
    "967b82fb1fb6274e4971c6c80caa9d04f844c512b1033c146f26c78270cd384b"
)
EXPECTED_LABEL_SHA256 = (
    "9fd94fc943a2dc08f1dc028d2b6f353ae85fae5169a536ae6489236db2f30b64"
)
EXPECTED_QUESTION_ROWS = 817
EXPECTED_LABEL_ROWS = 22_434
TOKEN_PATTERN = re.compile(r"[^\W_]+(?:'[^\W_]+)?", flags=re.UNICODE)
PROMPT_PATTERN = re.compile(r"^Q: (.*?)\nA: (.*?)\nTrue:$", flags=re.DOTALL)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require_source_contract(source_root: Path) -> tuple[Path, Path]:
    question_path = source_root / QUESTION_RELATIVE_PATH
    label_path = source_root / LABEL_RELATIVE_PATH
    for path in (question_path, label_path):
        if not path.is_file():
            raise FileNotFoundError(f"required TruthfulQA source file not found: {path}")

    observed = {
        question_path: _sha256(question_path),
        label_path: _sha256(label_path),
    }
    expected = {
        question_path: EXPECTED_QUESTION_SHA256,
        label_path: EXPECTED_LABEL_SHA256,
    }
    mismatches = [
        f"{path}: expected {expected[path]}, found {observed[path]}"
        for path in observed
        if observed[path] != expected[path]
    ]
    if mismatches:
        raise ValueError("TruthfulQA source hash mismatch:\n" + "\n".join(mismatches))

    head = subprocess.run(
        ["git", "-C", str(source_root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if head != SOURCE_COMMIT:
        raise ValueError(
            f"TruthfulQA checkout must be at {SOURCE_COMMIT}; found {head}"
        )
    return question_path, label_path


def _tokens(text: str) -> list[str]:
    return TOKEN_PATTERN.findall(text.casefold())


def _unigram_f1(candidate: Iterable[str], reference: Iterable[str]) -> float:
    candidate_tokens = list(candidate)
    reference_tokens = list(reference)
    if not candidate_tokens and not reference_tokens:
        return 1.0
    if not candidate_tokens or not reference_tokens:
        return 0.0
    overlap = sum((Counter(candidate_tokens) & Counter(reference_tokens)).values())
    if overlap == 0:
        return 0.0
    precision = overlap / len(candidate_tokens)
    recall = overlap / len(reference_tokens)
    return 2.0 * precision * recall / (precision + recall)


def _reference_list(value: object) -> list[str]:
    references = [part.strip() for part in str(value).split(";") if part.strip()]
    if not references:
        raise ValueError("encountered an empty TruthfulQA reference list")
    return references


def _max_reference_f1(answer_tokens: list[str], references: list[str]) -> float:
    return max(_unigram_f1(answer_tokens, _tokens(reference)) for reference in references)


def _parse_labelled_prompt(prompt: object, row_number: int) -> tuple[str, str]:
    if not isinstance(prompt, str):
        raise ValueError(f"label row {row_number} has a non-string prompt")
    match = PROMPT_PATTERN.fullmatch(prompt)
    if match is None:
        raise ValueError(f"label row {row_number} does not match the frozen prompt format")
    return match.group(1), match.group(2)


def _hash_uniform(question: str, answer: str) -> float:
    digest = hashlib.sha256(
        (question + "\x00" + answer).encode("utf-8")
    ).digest()
    return int.from_bytes(digest[:8], "big") / float(2**64)


def build_derived_ledger(question_path: Path, label_path: Path) -> pd.DataFrame:
    questions = pd.read_csv(question_path)
    required = {"Category", "Question", "Correct Answers", "Incorrect Answers"}
    missing = sorted(required.difference(questions.columns))
    if missing:
        raise ValueError(f"question CSV is missing columns: {', '.join(missing)}")
    if len(questions) != EXPECTED_QUESTION_ROWS:
        raise ValueError(
            f"expected {EXPECTED_QUESTION_ROWS} questions, found {len(questions)}"
        )
    if questions["Question"].duplicated().any():
        raise ValueError("question text must be unique for the frozen exact-text join")

    metadata: dict[str, dict[str, object]] = {}
    for question_index, row in questions.reset_index(drop=True).iterrows():
        question = str(row["Question"])
        correct = _reference_list(row["Correct Answers"])
        incorrect = _reference_list(row["Incorrect Answers"])
        metadata[question] = {
            "question_id": f"truthfulqa-{question_index + 1:04d}",
            "category": str(row["Category"]),
            "question_length_tokens": len(_tokens(question)),
            "correct_references": correct,
            "incorrect_references": incorrect,
            "correct_reference_count": len(correct),
            "incorrect_reference_count": len(incorrect),
        }

    rows: list[dict[str, object]] = []
    with label_path.open("r", encoding="utf-8") as handle:
        for source_row, line in enumerate(handle, start=1):
            record = json.loads(line)
            question, answer = _parse_labelled_prompt(record.get("prompt"), source_row)
            label = str(record.get("completion", "")).strip().casefold()
            if label not in {"yes", "no"}:
                raise ValueError(f"label row {source_row} has unexpected label {label!r}")
            if question not in metadata:
                raise ValueError(
                    f"label row {source_row} has no exact match in TruthfulQA v1: {question!r}"
                )

            item = metadata[question]
            answer_tokens = _tokens(answer)
            correct_f1 = _max_reference_f1(
                answer_tokens, item["correct_references"]  # type: ignore[arg-type]
            )
            incorrect_f1 = _max_reference_f1(
                answer_tokens, item["incorrect_references"]  # type: ignore[arg-type]
            )
            hash_noise = _hash_uniform(question, answer)
            answer_length = len(answer_tokens)
            rows.append(
                {
                    "source_row": source_row,
                    "question_id": item["question_id"],
                    "category": item["category"],
                    "human_truth_label": 1 if label == "yes" else 0,
                    "reference_overlap_diff": correct_f1 - incorrect_f1,
                    "max_correct_reference_f1": correct_f1,
                    "max_incorrect_reference_f1": incorrect_f1,
                    "answer_length_tokens": answer_length,
                    "question_length_tokens": item["question_length_tokens"],
                    "correct_reference_count": item["correct_reference_count"],
                    "incorrect_reference_count": item["incorrect_reference_count"],
                    "length_proxy_control": answer_length + (hash_noise - 0.5) * 1e-6,
                    "hash_noise_control": hash_noise,
                }
            )

    ledger = pd.DataFrame(rows)
    if len(ledger) != EXPECTED_LABEL_ROWS:
        raise ValueError(f"expected {EXPECTED_LABEL_ROWS} labels, found {len(ledger)}")
    if ledger["question_id"].nunique() != EXPECTED_QUESTION_ROWS:
        raise ValueError(
            f"expected labels for {EXPECTED_QUESTION_ROWS} questions, found "
            f"{ledger['question_id'].nunique()}"
        )
    return ledger


def _fmt(value: object) -> str:
    return "n/a" if value is None else f"{float(value):+.4f}"


def _results_markdown(card: dict[str, object]) -> str:
    evidence = card["evidence"]  # type: ignore[assignment]
    e1 = evidence["E1"]  # type: ignore[index]
    e2 = evidence["E2"]  # type: ignore[index]
    e1_result = e1["result"]
    e2_result = e2["result"]
    outcome = card.get("evidence_state", card.get("claim_status", "unavailable"))
    return "\n".join(
        [
            "# TruthfulQA Reference-Overlap Pilot Results",
            "",
            f"**Predeclared test outcome:** `{outcome}`",
            "",
            str(card["interpretation"]),
            "",
            "## Frozen Estimands",
            "",
            "| Estimand | Threshold state | Relative out-of-fold MSE improvement | 95% CI for absolute MSE improvement |",
            "|---|---|---:|---:|",
            f"| E1, increment beyond declared baselines | {e1['state']} | {_fmt(e1_result['relative_mse_improvement'])} | [{_fmt(e1_result['delta_mse_ci_low'])}, {_fmt(e1_result['delta_mse_ci_high'])}] |",
            f"| E2, aggregate category holdout | {e2['state']} | {_fmt(e2_result['relative_mse_improvement'])} | [{_fmt(e2_result['delta_mse_ci_low'])}, {_fmt(e2_result['delta_mse_ci_high'])}] |",
            "",
            "The practical threshold was fixed at 1% for each estimand before the score was computed. E0 is descriptive only. E3 and E4 were not run.",
            "",
            "## Interpretation Boundary",
            "",
            "This is a method demonstration on released human-labelled answers. It tests whether this transparent lexical score predicts those labels beyond the named proxies under the frozen grouping and category-holdout procedures. It is not a fresh validation set, a model-family audit, a causal result, a construct-validity result, an official TruthfulQA metric evaluation, or certification of a benchmark or model.",
            "",
            "The exact protocol was committed before the analysis at `5db33e4d8afadd9e1df730c7ea006d48902af4b1`. See `claim_card.md` for controls, assumptions, and complete limitations.",
            "",
        ]
    )


def run(source_root: Path, output_dir: Path) -> dict[str, object]:
    question_path, label_path = _require_source_contract(source_root.resolve())
    ledger = build_derived_ledger(question_path, label_path)
    card = audit_benchmark_claim(
        ledger,
        claim_id="truthfulqa-reference-overlap-pilot-v1",
        claim_text=(
            "On TruthfulQA's released human-labelled generation examples, a "
            "transparent reference-overlap score adds held-out information about "
            "the released human truth labels beyond declared length and "
            "reference-set proxies, and that increment transports in aggregate "
            "across TruthfulQA question categories."
        ),
        metric="reference_overlap_diff",
        target="human_truth_label",
        baselines=[
            "answer_length_tokens",
            "question_length_tokens",
            "correct_reference_count",
            "incorrect_reference_count",
        ],
        environment="category",
        unit="question_id",
        deceptive_control="length_proxy_control",
        negative_controls=["hash_noise_control"],
        min_relative_mse_improvement=0.01,
        min_transport_relative_mse_improvement=0.01,
        n_splits=5,
        degree=2,
        ridge=0.001,
        permutations=199,
        bootstrap=499,
        seed=20260716,
    )
    card["provenance"] = {
        "source_repository": "https://github.com/sylinrl/TruthfulQA",
        "source_commit": SOURCE_COMMIT,
        "license": "Apache-2.0",
        "question_file": QUESTION_RELATIVE_PATH.as_posix(),
        "question_file_sha256": EXPECTED_QUESTION_SHA256,
        "label_file": LABEL_RELATIVE_PATH.as_posix(),
        "label_file_sha256": EXPECTED_LABEL_SHA256,
        "protocol_file": "experiments/08_truthfulqa_real_audit/PROTOCOL.md",
        "protocol_freeze_commit": PROTOCOL_FREEZE_COMMIT,
    }
    card["score_definition"] = {
        "name": "reference_overlap_diff",
        "formula": (
            "max unigram multiset-F1 against supplied correct references minus "
            "max unigram multiset-F1 against supplied incorrect references"
        ),
        "official_truthfulqa_metric": False,
    }
    specific_limitations = [
        "The labels and answer pool are released data, not a fresh confirmatory holdout.",
        "The transparent reference-overlap score is a pilot metric, not an official TruthfulQA BLEU, ROUGE, BLEURT, or GPT-judge score.",
        "Answer-generator or model-family identities are unavailable here, so this pilot cannot test cross-model-family transport or control general model capability.",
        "TruthfulQA categories are broad and uneven; E2 is an environment-equal aggregate that can hide individual-category failures.",
        "Reference overlap can reward surface similarity and does not by itself establish truthfulness or construct validity.",
    ]
    card["limitations"] = specific_limitations + list(card.get("limitations", []))

    output_dir.mkdir(parents=True, exist_ok=True)
    ledger.to_csv(output_dir / "derived_ledger.csv", index=False, float_format="%.12g")
    write_claim_card(card, output_dir / "claim_card")
    (output_dir / "RESULTS.md").write_text(
        _results_markdown(card), encoding="utf-8"
    )
    manifest = {
        "protocol_freeze_commit": PROTOCOL_FREEZE_COMMIT,
        "truthfulqa_source_commit": SOURCE_COMMIT,
        "rows": len(ledger),
        "questions": int(ledger["question_id"].nunique()),
        "categories": int(ledger["category"].nunique()),
        "positive_labels": int(ledger["human_truth_label"].sum()),
        "negative_labels": int((1 - ledger["human_truth_label"]).sum()),
        "generated_files": [
            "derived_ledger.csv",
            "claim_card.json",
            "claim_card.md",
            "RESULTS.md",
        ],
    }
    (output_dir / "run_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return card


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the protocol-frozen TruthfulQA real-data pilot."
    )
    parser.add_argument(
        "--truthfulqa-root",
        required=True,
        type=Path,
        help="Checkout of sylinrl/TruthfulQA at the protocol-pinned commit.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "artifacts",
    )
    args = parser.parse_args()
    card = run(args.truthfulqa_root, args.output_dir)
    outcome = card.get("evidence_state", card.get("claim_status", "unavailable"))
    print(f"predeclared test outcome: {outcome}")
    print(f"artifacts: {args.output_dir.resolve()}")


if __name__ == "__main__":
    main()
