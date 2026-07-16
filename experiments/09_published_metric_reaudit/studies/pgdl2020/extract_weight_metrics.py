from __future__ import annotations

import argparse
from pathlib import Path
import sys

try:
    import h5py
except ImportError as exc:  # pragma: no cover - exercised by users without the extra
    raise SystemExit("h5py is required: python -m pip install h5py") from exc
import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from mbe_eval.checkpoint_metrics import summarize_checkpoint_pair


def read_tensors(path: Path) -> list[tuple[str, np.ndarray]]:
    tensors: list[tuple[str, np.ndarray]] = []
    with h5py.File(path, "r") as checkpoint:
        def collect(name: str, item: object) -> None:
            if isinstance(item, h5py.Dataset):
                tensors.append((name, item[...]))

        checkpoint.visititems(collect)
    return tensors


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract frozen PGDL weight-only metrics.")
    parser.add_argument("pilot_root", type=Path)
    parser.add_argument("selection", type=Path)
    parser.add_argument("ledger", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--spectral-method", choices=("exact", "power"), default="exact")
    parser.add_argument("--spectral-iterations", type=int, default=48)
    parser.add_argument("--seed", type=int, default=2026)
    args = parser.parse_args()

    selection = pd.read_csv(args.selection, dtype={"model_key": str})
    ledger = pd.read_csv(args.ledger, dtype={"model_key": str})
    source_by_run = selection.set_index("run_id")["source_task"].to_dict()
    rows: list[dict[str, object]] = []
    for row_index, selected in selection.sort_values("run_id").reset_index(drop=True).iterrows():
        model_root = (
            args.pilot_root
            / "input_data"
            / str(selected["source_task"])
            / f"model_{selected['model_key']}"
        )
        final_path = model_root / "weights.hdf5"
        initial_path = model_root / "weights_init.hdf5"
        if not final_path.is_file() or not initial_path.is_file():
            raise FileNotFoundError(f"missing checkpoint pair under {model_root}")
        metrics = summarize_checkpoint_pair(
            read_tensors(final_path),
            read_tensors(initial_path),
            spectral_method=args.spectral_method,
            spectral_iterations=args.spectral_iterations,
            seed=args.seed + row_index * 100,
        )
        rows.append({"run_id": selected["run_id"], **metrics})
        print(f"[{row_index + 1:02d}/{len(selection)}] {selected['run_id']}")

    metrics = pd.DataFrame(rows)
    if metrics["run_id"].duplicated().any() or len(metrics) != len(selection):
        raise ValueError("metric output does not have one row per selected model")
    if not np.isfinite(metrics.select_dtypes(include="number").to_numpy()).all():
        raise ValueError("metric output contains a non-finite value")
    merged = selection[["run_id", "task", "source_task", "model_key"]].merge(
        metrics, on="run_id", validate="one_to_one"
    ).merge(
        ledger,
        on=["run_id", "task", "model_key"],
        how="left",
        validate="one_to_one",
        suffixes=("", "_ledger"),
    )
    if merged["generalization_gap_accuracy"].isna().any():
        raise ValueError("one or more pilot rows did not match the PGDL ledger")
    if any(source_by_run[run_id] != source for run_id, source in zip(merged.run_id, merged.source_task)):
        raise ValueError("source-task mismatch after ledger merge")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(args.output, index=False)
    print(f"wrote {len(merged)} rows to {args.output}")
    print(merged.groupby("task")[["parameter_count", "parameter_l2", "distance_from_initialization_l2"]].agg(["min", "median", "max"]).to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
