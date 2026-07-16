from __future__ import annotations

import argparse
from pathlib import Path
import sys
import zipfile

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from inspect_remote_zip import HTTPRangeReader


ARCHIVES = {
    "public": "https://storage.googleapis.com/gresearch/pgdl/public_data.zip",
    "phase_one": "https://storage.googleapis.com/gresearch/pgdl/phase_one_data.zip",
    "phase_two": "https://storage.googleapis.com/gresearch/pgdl/phase_two_data.zip",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize PGDL archive bytes by task.")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    rows: list[dict[str, object]] = []
    for phase, url in ARCHIVES.items():
        reader = HTTPRangeReader(url)
        aggregates: dict[str, dict[str, int]] = {}
        with zipfile.ZipFile(reader) as archive:
            for info in archive.infolist():
                parts = info.filename.split("/")
                if len(parts) < 3 or parts[0] != "input_data" or not parts[1].startswith("task"):
                    continue
                task = parts[1]
                values = aggregates.setdefault(
                    task,
                    {
                        "checkpoint_members": 0,
                        "checkpoint_compressed_bytes": 0,
                        "checkpoint_uncompressed_bytes": 0,
                        "dataset_compressed_bytes": 0,
                    },
                )
                if info.filename.endswith(("weights.hdf5", "weights_init.hdf5")):
                    values["checkpoint_members"] += 1
                    values["checkpoint_compressed_bytes"] += info.compress_size
                    values["checkpoint_uncompressed_bytes"] += info.file_size
                elif "/dataset_" in info.filename and not info.is_dir():
                    values["dataset_compressed_bytes"] += info.compress_size
        for task, values in aggregates.items():
            rows.append(
                {
                    "phase": phase,
                    "task": task,
                    "archive_url": url,
                    "archive_etag": reader.etag,
                    **values,
                }
            )

    report = pd.DataFrame(rows).sort_values(["phase", "task"])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    report.to_csv(args.output, index=False)
    display = report.copy()
    for column in [
        "checkpoint_compressed_bytes",
        "checkpoint_uncompressed_bytes",
        "dataset_compressed_bytes",
    ]:
        display[column] = display[column] / (1024**3)
    print(display.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
