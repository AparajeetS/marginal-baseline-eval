from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


SOURCE_TASK = {"task1": "task1_v4", "task2": "task2_v1"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Select the frozen PGDL development pilot.")
    parser.add_argument("ledger", type=Path)
    parser.add_argument("plan", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--per-task", type=int, default=24)
    parser.add_argument("--seed", type=int, default=2026)
    args = parser.parse_args()

    ledger = pd.read_csv(args.ledger)
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    rng = np.random.default_rng(args.seed)
    selected: list[pd.DataFrame] = []
    for task in plan["splits"]["development"]:
        frame = ledger.loc[ledger["task"] == task].copy()
        if len(frame) < args.per_task:
            raise ValueError(f"{task} has fewer than {args.per_task} models")
        choice = rng.choice(frame.index.to_numpy(), size=args.per_task, replace=False)
        sample = frame.loc[choice].copy()
        for control in plan["task_controls"][task]:
            expected = set(frame[control].dropna().astype(str))
            observed = set(sample[control].dropna().astype(str))
            if observed != expected:
                raise ValueError(
                    f"seed {args.seed} does not cover every {task} level for {control}"
                )
        sample["source_task"] = SOURCE_TASK[task]
        selected.append(sample)

    pilot = pd.concat(selected, ignore_index=True).sort_values(["task", "model_key"])
    columns = [
        "run_id",
        "task",
        "source_task",
        "model_key",
        "architecture",
        "dataset",
        "hparams_json",
    ]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    pilot[columns].to_csv(args.output, index=False)
    print(pilot.groupby("task").size().to_string())
    print(f"selection={args.output} seed={args.seed} rows={len(pilot)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
