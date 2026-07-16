from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sys
import threading
import zipfile

import pandas as pd

EXPERIMENT_DIR = Path(__file__).resolve().parents[2]
if str(EXPERIMENT_DIR) not in sys.path:
    sys.path.insert(0, str(EXPERIMENT_DIR))

from inspect_remote_zip import HTTPRangeReader


PUBLIC_ARCHIVE = "https://storage.googleapis.com/gresearch/pgdl/public_data.zip"


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract the frozen PGDL pilot checkpoints.")
    parser.add_argument("selection", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()

    selection = pd.read_csv(args.selection, dtype={"model_key": str})
    members: list[str] = []
    for _, row in selection.iterrows():
        prefix = f"input_data/{row['source_task']}/model_{row['model_key']}"
        members.extend(
            [
                f"{prefix}/config.json",
                f"{prefix}/weights_init.hdf5",
                f"{prefix}/weights.hdf5",
            ]
        )

    metadata_reader = HTTPRangeReader(PUBLIC_ARCHIVE)
    with zipfile.ZipFile(metadata_reader) as archive:
        available = set(archive.namelist())
        missing = sorted(set(members) - available)
        if missing:
            raise ValueError(f"archive is missing selected members: {missing}")
        total_compressed = sum(archive.getinfo(name).compress_size for name in members)
        total_uncompressed = sum(archive.getinfo(name).file_size for name in members)
        print(
            f"members={len(members)} compressed_gib={total_compressed / 1024**3:.3f} "
            f"uncompressed_gib={total_uncompressed / 1024**3:.3f} etag={metadata_reader.etag}"
        )
        expected_sizes = {name: archive.getinfo(name).file_size for name in members}

    remaining: list[str] = []
    for name in members:
        destination = args.output_dir / name
        if destination.exists() and destination.stat().st_size == expected_sizes[name]:
            print(f"cached {name}")
        else:
            remaining.append(name)

    counter = len(members) - len(remaining)
    counter_lock = threading.Lock()

    def extract_chunk(chunk: list[str]) -> None:
        nonlocal counter
        reader = HTTPRangeReader(PUBLIC_ARCHIVE)
        with zipfile.ZipFile(reader) as archive:
            for name in chunk:
                destination = args.output_dir / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(archive.read(name))
                with counter_lock:
                    counter += 1
                    print(f"[{counter}/{len(members)}] extracted {name}", flush=True)

    worker_count = max(1, min(args.workers, len(remaining))) if remaining else 0
    if worker_count:
        chunks = [remaining[index::worker_count] for index in range(worker_count)]
        with ThreadPoolExecutor(max_workers=worker_count) as executor:
            list(executor.map(extract_chunk, chunks))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
