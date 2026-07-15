from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Iterable
import unicodedata

import numpy as np
import pandas as pd


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from mbe_eval.claim_card import (  # noqa: E402
    audit_benchmark_claim,
    claim_card_json,
    write_claim_card,
)
from mbe_eval.contestation import compare_benchmark_claim_specs  # noqa: E402


SOURCE_COMMIT = "d71c110897f5d31c5d7f309e7bc316c152f6f031"
PROTOCOL_FREEZE_COMMIT = "827e192729b1b26dd8c470ae70f028214c942090"
QUESTION_RELATIVE_PATH = Path("data/v0/TruthfulQA.csv")
TRUTH_RELATIVE_PATH = Path("data/finetune_truth.jsonl")
INFO_RELATIVE_PATH = Path("data/finetune_info.jsonl")
METRICS_RELATIVE_PATH = Path("truthfulqa/metrics.py")
EXPECTED_SHA256 = {
    QUESTION_RELATIVE_PATH: "f4fcc4a841d4474c46a4719c295c6df5f12eef14c187fbb9637a29e70d9ece00",
    TRUTH_RELATIVE_PATH: "9fd94fc943a2dc08f1dc028d2b6f353ae85fae5169a536ae6489236db2f30b64",
    INFO_RELATIVE_PATH: "5956ef2070055e3ae0020d510007f5b9eb841719c9e3320e38fd7e2ee340b69e",
    METRICS_RELATIVE_PATH: "0a4667429a13b2f75704af631ac001674a60c74c8e2955c8431d5b0faddb7b12",
}
EXPECTED_QUESTION_ROWS = 817
EXPECTED_LABEL_ROWS = 22_434
MIN_QUESTIONS_PER_ENVIRONMENT = 20
TOKEN_PATTERN = re.compile(r"[^\W_]+(?:'[^\W_]+)?", flags=re.UNICODE)
REFUSAL_OR_UNCERTAINTY_PHRASES = (
    "i have no comment",
    "i don't know",
    "i do not know",
    "unknown",
    "unclear",
    "not known",
    "no one knows",
    "cannot be determined",
    "can't be determined",
)
DECLARED_BASELINES = [
    "answer_length_tokens",
    "question_length_tokens",
    "refusal_or_uncertainty_flag",
    "question_type",
    "correct_reference_count",
    "incorrect_reference_count",
]
CLAIM_TEXT = (
    "Within the released TruthfulQA v0 human-labelled answer triples, after "
    "removing duplicated conflicts and exact benchmark-reference answers and "
    "grouping by question, a transparent ROUGE-1-style reference-difference "
    "score adds out-of-question predictive information for the original human "
    "binary truth judgments beyond the declared response and task proxies; the "
    "pilot separately tests whether that increment transports in aggregate "
    "across sufficiently represented question categories."
)


@dataclass(frozen=True)
class ParsedLabels:
    labels: dict[tuple[str, str], int]
    raw_rows: int
    unique_pairs: int
    duplicate_rows: int
    conflicting_pairs: int


@dataclass(frozen=True)
class PreparedCohort:
    main_ledger: pd.DataFrame
    eligible_ledger: pd.DataFrame
    category_summary: pd.DataFrame
    manifest: dict[str, object]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require_source_contract(source_root: Path) -> dict[Path, Path]:
    paths = {relative: source_root / relative for relative in EXPECTED_SHA256}
    for path in paths.values():
        if not path.is_file():
            raise FileNotFoundError(f"required TruthfulQA source file not found: {path}")

    mismatches = []
    for relative, path in paths.items():
        observed = _sha256(path)
        if observed != EXPECTED_SHA256[relative]:
            mismatches.append(
                f"{relative.as_posix()}: expected {EXPECTED_SHA256[relative]}, "
                f"found {observed}"
            )
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
    return paths


def _tokens(text: str) -> list[str]:
    normalized = unicodedata.normalize("NFKC", text).casefold()
    return TOKEN_PATTERN.findall(normalized)


def _leakage_normalize(text: str) -> str:
    value = unicodedata.normalize("NFKC", text).casefold()
    value = " ".join(value.split())
    if value.endswith("."):
        value = value[:-1].rstrip()
    return value


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


def _parse_prompt(prompt: object, suffix: str, row_number: int) -> tuple[str, str]:
    if not isinstance(prompt, str):
        raise ValueError(f"label row {row_number} has a non-string prompt")
    pattern = re.compile(
        rf"^Q: (.*?)\nA: (.*?)\n{re.escape(suffix)}:$", flags=re.DOTALL
    )
    match = pattern.fullmatch(prompt)
    if match is None:
        raise ValueError(
            f"label row {row_number} does not match the frozen {suffix!r} format"
        )
    return match.group(1), match.group(2)


def _parse_labels(path: Path, suffix: str) -> ParsedLabels:
    observed: dict[tuple[str, str], set[int]] = {}
    raw_rows = 0
    with path.open("r", encoding="utf-8") as handle:
        for raw_rows, line in enumerate(handle, start=1):
            record = json.loads(line)
            question, answer = _parse_prompt(record.get("prompt"), suffix, raw_rows)
            label = str(record.get("completion", "")).strip().casefold()
            if label not in {"yes", "no"}:
                raise ValueError(f"label row {raw_rows} has unexpected label {label!r}")
            observed.setdefault((question, answer), set()).add(1 if label == "yes" else 0)

    if raw_rows != EXPECTED_LABEL_ROWS:
        raise ValueError(f"expected {EXPECTED_LABEL_ROWS} labels, found {raw_rows}")
    conflicts = {pair for pair, labels in observed.items() if len(labels) > 1}
    labels = {
        pair: next(iter(values))
        for pair, values in observed.items()
        if pair not in conflicts
    }
    return ParsedLabels(
        labels=labels,
        raw_rows=raw_rows,
        unique_pairs=len(observed),
        duplicate_rows=raw_rows - len(observed),
        conflicting_pairs=len(conflicts),
    )


def _hash_bytes(question: str, answer: str) -> bytes:
    return hashlib.sha256((question + "\x00" + answer).encode("utf-8")).digest()


def _pair_id(question: str, answer: str) -> str:
    return _hash_bytes(question, answer).hex()


def _hash_uniform(question: str, answer: str) -> float:
    return int.from_bytes(_hash_bytes(question, answer)[:8], "big") / float(2**64)


def prepare_cohort(paths: dict[Path, Path]) -> PreparedCohort:
    questions = pd.read_csv(paths[QUESTION_RELATIVE_PATH])
    required = {
        "Type",
        "Category",
        "Question",
        "Correct Answers",
        "Incorrect Answers",
    }
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
        if "I have no comment." not in correct:
            correct.append("I have no comment.")
        incorrect = _reference_list(row["Incorrect Answers"])
        metadata[question] = {
            "question_id": f"truthfulqa-v0-{question_index + 1:04d}",
            "category": str(row["Category"]),
            "question_type": str(row["Type"]),
            "question_length_tokens": len(_tokens(question)),
            "correct_references": correct,
            "incorrect_references": incorrect,
            "correct_reference_count": len(correct),
            "incorrect_reference_count": len(incorrect),
            "normalized_references": {
                _leakage_normalize(reference) for reference in [*correct, *incorrect]
            },
        }

    truth = _parse_labels(paths[TRUTH_RELATIVE_PATH], "True")
    info = _parse_labels(paths[INFO_RELATIVE_PATH], "Helpful")
    unmatched_pairs = 0
    exact_reference_pairs = 0
    rows: list[dict[str, object]] = []
    for (question, answer), truth_label in truth.labels.items():
        if question not in metadata:
            unmatched_pairs += 1
            continue
        item = metadata[question]
        if _leakage_normalize(answer) in item["normalized_references"]:
            exact_reference_pairs += 1
            continue

        answer_tokens = _tokens(answer)
        correct_f1 = _max_reference_f1(
            answer_tokens, item["correct_references"]  # type: ignore[arg-type]
        )
        incorrect_f1 = _max_reference_f1(
            answer_tokens, item["incorrect_references"]  # type: ignore[arg-type]
        )
        hash_noise = _hash_uniform(question, answer)
        answer_length = len(answer_tokens)
        normalized_answer = _leakage_normalize(answer)
        pair = (question, answer)
        rows.append(
            {
                "pair_id": _pair_id(question, answer),
                "question_id": item["question_id"],
                "category": item["category"],
                "question_type": item["question_type"],
                "human_truth_label": truth_label,
                "human_informativeness_label": info.labels.get(pair, np.nan),
                "reference_overlap_diff": correct_f1 - incorrect_f1,
                "max_correct_reference_f1": correct_f1,
                "max_incorrect_reference_f1": incorrect_f1,
                "answer_length_tokens": answer_length,
                "question_length_tokens": item["question_length_tokens"],
                "refusal_or_uncertainty_flag": int(
                    any(
                        phrase in normalized_answer
                        for phrase in REFUSAL_OR_UNCERTAINTY_PHRASES
                    )
                ),
                "correct_reference_count": item["correct_reference_count"],
                "incorrect_reference_count": item["incorrect_reference_count"],
                "length_proxy_control": answer_length + (hash_noise - 0.5) * 1e-6,
                "hash_noise_control": hash_noise,
            }
        )

    eligible = pd.DataFrame(rows).sort_values("pair_id").reset_index(drop=True)
    if eligible["pair_id"].duplicated().any():
        raise RuntimeError("internal error: prepared pair IDs are not unique")
    environment_coverage = eligible.groupby("category")["question_id"].nunique()
    retained_categories = sorted(
        environment_coverage[
            environment_coverage >= MIN_QUESTIONS_PER_ENVIRONMENT
        ].index.tolist()
    )
    main = (
        eligible[eligible["category"].isin(retained_categories)]
        .copy()
        .reset_index(drop=True)
    )
    category_summary = (
        eligible.groupby("category", sort=True)
        .agg(
            rows=("pair_id", "size"),
            questions=("question_id", "nunique"),
            truth_label_prevalence=("human_truth_label", "mean"),
            mean_reference_overlap_diff=("reference_overlap_diff", "mean"),
        )
        .reset_index()
    )
    category_summary["included_in_main_e2"] = category_summary["category"].isin(
        retained_categories
    )

    manifest: dict[str, object] = {
        "protocol_freeze_commit": PROTOCOL_FREEZE_COMMIT,
        "truthfulqa_source_commit": SOURCE_COMMIT,
        "truth_labels": {
            "raw_rows": truth.raw_rows,
            "unique_question_answer_pairs": truth.unique_pairs,
            "duplicate_rows_collapsed": truth.duplicate_rows,
            "conflicting_pairs_excluded": truth.conflicting_pairs,
        },
        "informativeness_labels": {
            "raw_rows": info.raw_rows,
            "unique_question_answer_pairs": info.unique_pairs,
            "duplicate_rows_collapsed": info.duplicate_rows,
            "conflicting_pairs_excluded": info.conflicting_pairs,
        },
        "cohort_exclusions": {
            "truth_pairs_without_exact_v0_question_match": unmatched_pairs,
            "exact_benchmark_reference_pairs": exact_reference_pairs,
        },
        "eligible_before_category_rule": {
            "rows": len(eligible),
            "questions": int(eligible["question_id"].nunique()),
            "categories": int(eligible["category"].nunique()),
        },
        "main_cohort": {
            "minimum_questions_per_environment": MIN_QUESTIONS_PER_ENVIRONMENT,
            "rows": len(main),
            "questions": int(main["question_id"].nunique()),
            "categories": int(main["category"].nunique()),
            "retained_categories": retained_categories,
            "positive_truth_labels": int(main["human_truth_label"].sum()),
            "negative_truth_labels": int((1 - main["human_truth_label"]).sum()),
            "informativeness_matched_rows": int(
                main["human_informativeness_label"].notna().sum()
            ),
        },
    }
    return PreparedCohort(main, eligible, category_summary, manifest)


def _audit_arguments(*, baselines: list[str], claim_id: str) -> dict[str, object]:
    return {
        "claim_id": claim_id,
        "claim_text": CLAIM_TEXT,
        "metric": "reference_overlap_diff",
        "target": "human_truth_label",
        "baselines": baselines,
        "environment": "category",
        "unit": "question_id",
        "deceptive_control": "length_proxy_control",
        "negative_controls": ["hash_noise_control"],
        "min_relative_mse_improvement": 0.01,
        "min_transport_relative_mse_improvement": 0.01,
        "n_splits": 5,
        "degree": 2,
        "ridge": 0.001,
        "permutations": 199,
        "bootstrap": 499,
        "seed": 20260716,
    }


def _fmt(value: object) -> str:
    return "n/a" if value is None else f"{float(value):+.4f}"


def _results_markdown(card: dict[str, object], manifest: dict[str, object]) -> str:
    evidence = card["evidence"]  # type: ignore[assignment]
    e1 = evidence["E1"]  # type: ignore[index]
    e2 = evidence["E2"]  # type: ignore[index]
    e1_result = e1["result"]
    e2_result = e2["result"]
    main = manifest["main_cohort"]  # type: ignore[assignment]
    return "\n".join(
        [
            "# TruthfulQA Reference-Difference Pilot Results",
            "",
            f"**Predeclared test outcome:** `{card['evidence_state']}`",
            "",
            str(card["interpretation"]),
            "",
            "## Audited Cohort",
            "",
            f"The main cohort contains {main['rows']:,} unique, nonconflicting, non-reference answer pairs from {main['questions']:,} questions in {main['categories']} sufficiently represented categories.",
            "",
            "## Frozen Estimands",
            "",
            "| Estimand | Threshold state | Relative out-of-fold MSE improvement | 95% CI for absolute MSE improvement |",
            "|---|---|---:|---:|",
            f"| E1, increment beyond declared proxies | {e1['state']} | {_fmt(e1_result['relative_mse_improvement'])} | [{_fmt(e1_result['delta_mse_ci_low'])}, {_fmt(e1_result['delta_mse_ci_high'])}] |",
            f"| E2, aggregate category holdout | {e2['state']} | {_fmt(e2_result['relative_mse_improvement'])} | [{_fmt(e2_result['delta_mse_ci_low'])}, {_fmt(e2_result['delta_mse_ci_high'])}] |",
            "",
            "The practical threshold was fixed at 1% for each estimand before the score was computed. E0 is descriptive only. E3 and E4 were not run.",
            "",
            "## Interpretation Boundary",
            "",
            "This is a method demonstration on released TruthfulQA v0 human judgments after explicit leakage exclusions. It tests incremental prediction under the frozen proxies, question grouping, and category holdouts. It is not a fresh validation set, a model-family or capability-controlled audit, a causal or construct-validity result, an exact reproduction of TruthfulQA's T5 ROUGE metric, or certification of a benchmark or model.",
            "",
            f"The governing amended protocol was committed before analysis at `{PROTOCOL_FREEZE_COMMIT}`. See `claim_card.md`, `cohort_manifest.json`, and `category_summary.csv` for the controls, exclusions, and limitations.",
            "",
        ]
    )


def _sensitivity_markdown(bundle: dict[str, object], rows: int) -> str:
    specifications = bundle["specifications"]  # type: ignore[assignment]
    lines = [
        "# Human-Informativeness Baseline Sensitivity",
        "",
        f"This non-decisional sensitivity uses the {rows:,} main-cohort rows with a nonconflicting exact match to the released human informativeness labels.",
        "",
        "| Specification | Predeclared-test state on matched subset | E1 | E2 |",
        "|---|---|---|---|",
    ]
    for name, summary in specifications.items():  # type: ignore[union-attr]
        states = summary["estimand_states"]
        lines.append(
            f"| `{name}` | {summary['evidence_state']} | {states['E1']} | {states['E2']} |"
        )
    lines.extend(
        [
            "",
            f"**Did the complete estimand-state signature change?** `{str(bundle['conclusion_changed']).lower()}`",
            "",
            "Human informativeness shares the original annotation pipeline and is not a deployment-available capability proxy. This comparison is diagnostic and is not part of the primary pass/fail rule.",
            "",
        ]
    )
    return "\n".join(lines)


def run(source_root: Path, output_dir: Path) -> dict[str, object]:
    paths = _require_source_contract(source_root.resolve())
    cohort = prepare_cohort(paths)
    card = audit_benchmark_claim(
        cohort.main_ledger,
        **_audit_arguments(
            baselines=DECLARED_BASELINES,
            claim_id="truthfulqa-v0-reference-difference-pilot-v1",
        ),
    )
    card["provenance"] = {
        "source_repository": "https://github.com/sylinrl/TruthfulQA",
        "source_commit": SOURCE_COMMIT,
        "license": "Apache-2.0",
        "files": {
            relative.as_posix(): {"sha256": digest}
            for relative, digest in EXPECTED_SHA256.items()
        },
        "protocol_file": "experiments/08_truthfulqa_real_audit/PROTOCOL.md",
        "protocol_freeze_commit": PROTOCOL_FREEZE_COMMIT,
    }
    card["score_definition"] = {
        "name": "reference_overlap_diff",
        "formula": (
            "maximum unigram multiset-F1 against supplied correct references plus "
            "the official no-comment reference, minus maximum unigram multiset-F1 "
            "against supplied incorrect references"
        ),
        "exact_official_t5_rouge_implementation": False,
    }
    specific_limitations = [
        "The labels and answer pool are released TruthfulQA v0 data, not a fresh confirmatory holdout.",
        "The same project produced the human judgments and reference framework, so the target is external to the automated score but not an independently constructed benchmark.",
        "Model identity, family, size, prompt, and general capability are unavailable; this pilot neither controls them nor tests model-family transport.",
        "The transparent lexical score follows the official reference-difference structure but is not the exact T5 ROUGE implementation or an official score.",
        "Exact reference answers, duplicate conflicts, poorly represented categories, and unmatched questions were excluded by the frozen rules; the result applies only to the resulting cohort.",
        "Categories are author-defined and unequal; aggregate E2 can hide individual-category failures, so category summaries are published separately.",
        "Reference overlap can reward surface similarity and does not by itself establish truthfulness or construct validity.",
    ]
    card["limitations"] = specific_limitations + list(card.get("limitations", []))

    info_matched = cohort.main_ledger.dropna(
        subset=["human_informativeness_label"]
    ).copy()
    info_matched["human_informativeness_label"] = info_matched[
        "human_informativeness_label"
    ].astype(int)
    sensitivity_common = _audit_arguments(
        baselines=DECLARED_BASELINES,
        claim_id="truthfulqa-v0-info-matched-sensitivity",
    )
    sensitivity_common.pop("baselines")
    sensitivity_common.pop("claim_id")
    sensitivity_bundle = compare_benchmark_claim_specs(
        info_matched,
        {
            "declared-proxies": {
                "claim_id": "truthfulqa-v0-info-matched-declared-proxies",
                "baselines": DECLARED_BASELINES,
            },
            "plus-human-informativeness": {
                "claim_id": "truthfulqa-v0-info-matched-plus-human-info",
                "baselines": [*DECLARED_BASELINES, "human_informativeness_label"],
            },
        },
        common=sensitivity_common,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    cohort.main_ledger.to_csv(
        output_dir / "derived_ledger.csv", index=False, float_format="%.12g"
    )
    cohort.category_summary.to_csv(
        output_dir / "category_summary.csv", index=False, float_format="%.12g"
    )
    write_claim_card(card, output_dir / "claim_card")
    (output_dir / "RESULTS.md").write_text(
        _results_markdown(card, cohort.manifest), encoding="utf-8"
    )
    (output_dir / "informativeness_sensitivity.json").write_text(
        claim_card_json(sensitivity_bundle), encoding="utf-8"
    )
    (output_dir / "INFORMATIVENESS_SENSITIVITY.md").write_text(
        _sensitivity_markdown(sensitivity_bundle, len(info_matched)), encoding="utf-8"
    )
    manifest = {
        **cohort.manifest,
        "generated_files": [
            "derived_ledger.csv",
            "category_summary.csv",
            "claim_card.json",
            "claim_card.md",
            "RESULTS.md",
            "informativeness_sensitivity.json",
            "INFORMATIVENESS_SENSITIVITY.md",
        ],
    }
    (output_dir / "cohort_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return card


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the protocol-frozen TruthfulQA v0 real-data pilot."
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
    print(f"predeclared test outcome: {card['evidence_state']}")
    print(f"artifacts: {args.output_dir.resolve()}")


if __name__ == "__main__":
    main()
