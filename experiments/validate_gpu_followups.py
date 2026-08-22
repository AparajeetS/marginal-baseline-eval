from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[1]
IMAGE_ROOT = REPO_ROOT / "experiments/19_corrected_image_factorial"
TEXT_ROOT = REPO_ROOT / "experiments/20_multicorpus_text_atlas"
IMAGE_OUT = IMAGE_ROOT / "kaggle_downloads/v1"
TEXT_OUT = TEXT_ROOT / "kaggle_downloads/v1"

IMAGE_REQUIRED_MEASUREMENTS = {
    "test_loss",
    "test_acc",
    "val_loss",
    "final_train_batch_loss",
    "fim_norm",
    "fim_erank",
    "fisher_trace",
    "grad_norm",
    "sam_sharpness",
    "hessian_trace_hutchinson",
    "weight_l2",
    "distance_from_init_l2",
    "feature_erank",
    "confidence_mean",
    "metric_batch_loss",
    "random_metric",
}
TEXT_REQUIRED_MEASUREMENTS = {
    "test_loss",
    "test_perplexity",
    "test_token_accuracy",
    "val_loss",
    "final_train_batch_loss",
    "fim_norm",
    "fim_erank",
    "empirical_fisher_trace",
    "gradient_norm",
    "sharpness_random_perturbation",
    "parameter_l2",
    "distance_from_initialization_l2",
    "feature_erank",
    "prediction_confidence",
    "metric_batch_loss",
    "random_metric",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_rows(path: Path) -> tuple[list[dict[str, str]], set[str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        return rows, set(reader.fieldnames or [])


def finite_failures(rows: list[dict[str, str]], fields: set[str]) -> dict[str, int]:
    failures: dict[str, int] = {}
    for field in sorted(fields):
        count = 0
        for row in rows:
            try:
                value = float(row.get(field, ""))
            except (TypeError, ValueError):
                count += 1
                continue
            if not math.isfinite(value):
                count += 1
        failures[field] = count
    return failures


def frozen_hashes(root: Path) -> dict[str, str]:
    rows = {}
    for line in (root / "FROZEN_SHA256SUMS").read_text(encoding="ascii").splitlines():
        digest, name = line.split(maxsplit=1)
        rows[name.strip()] = digest
    return rows


def source_hash_check(root: Path) -> dict[str, bool]:
    return {
        name: (root / name).is_file() and sha256(root / name) == digest
        for name, digest in frozen_hashes(root).items()
    }


def artifact_hashes(root: Path) -> list[str]:
    excluded = {"ARTIFACT_SHA256SUMS"}
    paths = sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and path.name not in excluded
    )
    return [f"{sha256(path)}  {path.relative_to(root).as_posix()}" for path in paths]


def validate_image() -> dict[str, object]:
    csv_path = IMAGE_OUT / "mbe3_corrected_image_factorial.csv"
    manifest = json.loads(
        (IMAGE_OUT / "mbe3_corrected_image_factorial_manifest.json").read_text(
            encoding="utf-8"
        )
    )
    reported = json.loads(
        (IMAGE_OUT / "mbe3_corrected_image_factorial_integrity.json").read_text(
            encoding="utf-8"
        )
    )
    rows, columns = load_rows(csv_path)
    valid = [row for row in rows if not row.get("error")]
    run_ids = [row.get("run_id", "") for row in rows]
    manifest_run_ids = {row["run_id"] for row in manifest["grid"]}
    config_counts = Counter(row["config_id"] for row in valid)
    architecture_counts = Counter(row["arch"] for row in valid)
    optimizer_counts = Counter(row["optimizer"] for row in valid)
    seed_counts = Counter(row["seed_id"] for row in valid)
    train_idx, val_idx, test_idx = image_split_indices(
        manifest["n_train"], manifest["n_validation"], manifest["n_test"]
    )
    split_hashes = {
        "train_indices": hashlib.sha256(train_idx.tobytes()).hexdigest(),
        "validation_indices": hashlib.sha256(val_idx.tobytes()).hexdigest(),
        "test_indices": hashlib.sha256(test_idx.tobytes()).hexdigest(),
    }
    result = {
        "rows": len(rows),
        "valid_rows": len(valid),
        "error_rows": len(rows) - len(valid),
        "unique_run_ids": len(set(run_ids)),
        "duplicate_run_ids": len(run_ids) - len(set(run_ids)),
        "run_ids_match_manifest": set(run_ids) == manifest_run_ids,
        "configurations": len(config_counts),
        "all_configurations_have_two_seeds": all(
            count == 2 for count in config_counts.values()
        ),
        "architecture_counts": dict(sorted(architecture_counts.items())),
        "optimizer_counts": dict(sorted(optimizer_counts.items())),
        "seed_counts": dict(sorted(seed_counts.items())),
        "missing_required_columns": sorted(IMAGE_REQUIRED_MEASUREMENTS - columns),
        "nonfinite_required_values": finite_failures(
            valid, IMAGE_REQUIRED_MEASUREMENTS & columns
        ),
        "split_hashes_match": split_hashes == manifest["split_hashes"],
        "source_hashes_match": source_hash_check(IMAGE_ROOT),
        "reported_integrity_matches": (
            reported["rows"] == len(rows)
            and reported["valid_rows"] == len(valid)
            and reported["error_rows"] == len(rows) - len(valid)
            and reported["primary_gate_pass"] is True
        ),
    }
    result["pass"] = bool(
        result["rows"] == 96
        and result["valid_rows"] == 96
        and result["error_rows"] == 0
        and result["duplicate_run_ids"] == 0
        and result["run_ids_match_manifest"]
        and result["configurations"] == 48
        and result["all_configurations_have_two_seeds"]
        and result["architecture_counts"]
        == {"cnn": 32, "resnet": 32, "wide_resnet": 32}
        and result["optimizer_counts"] == {"adamw": 48, "sgd": 48}
        and result["seed_counts"] == {"8111": 48, "8112": 48}
        and not result["missing_required_columns"]
        and not any(result["nonfinite_required_values"].values())
        and result["split_hashes_match"]
        and all(result["source_hashes_match"].values())
        and result["reported_integrity_matches"]
    )
    return result


def image_split_indices(
    n_train: int, n_val: int, n_test: int
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(20260811)
    train_order = rng.permutation(50_000)
    test_order = rng.permutation(10_000)
    return (
        train_order[:n_train],
        train_order[n_train : n_train + n_val],
        test_order[:n_test],
    )


def validate_text() -> dict[str, object]:
    csv_path = TEXT_OUT / "mbe3_multicorpus_text_atlas.csv"
    manifest = json.loads(
        (TEXT_OUT / "mbe3_multicorpus_text_atlas_manifest.json").read_text(
            encoding="utf-8"
        )
    )
    reported = json.loads(
        (TEXT_OUT / "mbe3_multicorpus_text_atlas_integrity.json").read_text(
            encoding="utf-8"
        )
    )
    leakage = json.loads(
        (TEXT_OUT / "causal_mask_leakage_test.json").read_text(encoding="utf-8")
    )
    rows, columns = load_rows(csv_path)
    valid = [row for row in rows if not row.get("error")]
    run_ids = [row.get("run_id", "") for row in rows]
    manifest_run_ids = {row["run_id"] for row in manifest["grid"]}
    config_counts = Counter(row["config_id"] for row in valid)
    environment_counts = Counter(row["environment_id"] for row in valid)
    seed_counts = Counter(row["seed_id"] for row in valid)
    complete_by_environment = {}
    for environment in manifest["environments"]:
        counts = Counter(
            row["config_id"]
            for row in valid
            if row["environment_id"] == environment
        )
        complete_by_environment[environment] = sum(
            count == 2 for count in counts.values()
        )
    dataset_hashes_match = True
    for environment, hashes in manifest["dataset_hashes"].items():
        for split, expected in hashes.items():
            path = TEXT_OUT / "corpora" / environment / f"{environment}.{split}.txt"
            dataset_hashes_match &= path.is_file() and sha256(path) == expected
    result = {
        "rows": len(rows),
        "valid_rows": len(valid),
        "error_rows": len(rows) - len(valid),
        "unique_run_ids": len(set(run_ids)),
        "duplicate_run_ids": len(run_ids) - len(set(run_ids)),
        "run_ids_match_manifest": set(run_ids) == manifest_run_ids,
        "configurations": len(config_counts),
        "all_configurations_have_two_seeds": all(
            count == 2 for count in config_counts.values()
        ),
        "environment_counts": dict(sorted(environment_counts.items())),
        "complete_configurations_by_environment": complete_by_environment,
        "seed_counts": dict(sorted(seed_counts.items())),
        "missing_required_columns": sorted(TEXT_REQUIRED_MEASUREMENTS - columns),
        "nonfinite_required_values": finite_failures(
            valid, TEXT_REQUIRED_MEASUREMENTS & columns
        ),
        "dataset_hashes_match": dataset_hashes_match,
        "causal_mask_pass": leakage.get("causal_pass") is True,
        "unmasked_negative_control_pass": leakage.get("negative_control_pass") is True,
        "source_hashes_match": source_hash_check(TEXT_ROOT),
        "reported_integrity_matches": (
            reported["rows"] == len(rows)
            and reported["valid_rows"] == len(valid)
            and reported["error_rows"] == len(rows) - len(valid)
            and reported["primary_gate_pass"] is True
        ),
    }
    result["pass"] = bool(
        result["rows"] == 144
        and result["valid_rows"] == 144
        and result["error_rows"] == 0
        and result["duplicate_run_ids"] == 0
        and result["run_ids_match_manifest"]
        and result["configurations"] == 72
        and result["all_configurations_have_two_seeds"]
        and result["environment_counts"]
        == {"ptb": 48, "tinyshakespeare": 48, "wikitext2": 48}
        and result["complete_configurations_by_environment"]
        == {"wikitext2": 24, "ptb": 24, "tinyshakespeare": 24}
        and result["seed_counts"] == {"8201": 72, "8202": 72}
        and not result["missing_required_columns"]
        and not any(result["nonfinite_required_values"].values())
        and result["dataset_hashes_match"]
        and result["causal_mask_pass"]
        and result["unmasked_negative_control_pass"]
        and all(result["source_hashes_match"].values())
        and result["reported_integrity_matches"]
    )
    return result


def write_validation(root: Path, result: dict[str, object]) -> None:
    (root / "STRUCTURAL_VALIDATION.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    (root / "ARTIFACT_SHA256SUMS").write_text(
        "\n".join(artifact_hashes(root)) + "\n", encoding="ascii"
    )


def main() -> int:
    image = validate_image()
    text = validate_text()
    write_validation(IMAGE_OUT, image)
    write_validation(TEXT_OUT, text)
    print(json.dumps({"image": image, "text": text}, indent=2))
    return 0 if image["pass"] and text["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
