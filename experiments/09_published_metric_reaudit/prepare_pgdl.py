from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd


TASK_METADATA = {
    "task1_v4": ("task1", "development", "vgg", "cifar10"),
    "task2_v1": ("task2", "development", "nin", "svhn"),
    "task4": ("task4", "validation", "fully_convolutional_bn", "cinic10"),
    "task5": ("task5", "validation", "fully_convolutional", "cinic10"),
    "task6": ("task6", "holdout", "nin", "oxford_flowers"),
    "task7": ("task7", "holdout", "nin_dense", "oxford_pets"),
    "task8": ("task8", "holdout", "vgg", "fashion_mnist"),
    "task9": ("task9", "holdout", "nin", "cifar10_augmented"),
}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a unified run ledger from selectively extracted PGDL configs."
    )
    parser.add_argument("data_root", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    rows: list[dict[str, object]] = []
    source_rows: list[dict[str, object]] = []
    for path in sorted(args.data_root.rglob("model_configs.json")):
        source_task = path.parent.name
        if source_task not in TASK_METADATA:
            continue
        task, split, architecture, dataset = TASK_METADATA[source_task]
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        records = json.loads(path.read_text(encoding="utf-8"))
        source_rows.append(
            {
                "task": task,
                "source_task": source_task,
                "models": len(records),
                "sha256": digest,
                "path": path.as_posix(),
            }
        )
        for model_key, record in records.items():
            metrics = record["metrics"]
            row: dict[str, object] = {
                "run_id": f"{task}:{model_key}",
                "task": task,
                "split": split,
                "architecture": architecture,
                "dataset": dataset,
                "model_key": str(model_key),
                "dev_name": record.get("dev_name", ""),
                "train_acc": metrics["train_acc"],
                "test_acc": metrics["test_acc"],
                "train_loss": metrics["train_loss"],
                "test_loss": metrics["test_loss"],
                "generalization_gap_accuracy": metrics["train_acc"] - metrics["test_acc"],
                "generalization_gap_loss": metrics["test_loss"] - metrics["train_loss"],
                "test_error": 1.0 - metrics["test_acc"],
            }
            hparams: dict[str, object] = {}
            for name, value in record["hparams"].items():
                current = value["current_value"]
                hparams[name] = current
                row[f"hp.{name}"] = current
            row["hparams_json"] = json.dumps(hparams, sort_keys=True, separators=(",", ":"))
            rows.append(row)

    ledger = pd.DataFrame(rows).sort_values(["task", "model_key"]).reset_index(drop=True)
    if len(ledger) != 550:
        raise ValueError(f"expected 550 PGDL models, found {len(ledger)}")
    if ledger["run_id"].duplicated().any():
        raise ValueError("PGDL run IDs are not unique")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    ledger.to_csv(args.output, index=False)
    provenance = args.output.with_name(f"{args.output.stem}_sources.csv")
    pd.DataFrame(source_rows).sort_values("task").to_csv(provenance, index=False)
    print(ledger.groupby(["split", "task"]).size().to_string())
    print(f"total={len(ledger)} output={args.output} provenance={provenance}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
