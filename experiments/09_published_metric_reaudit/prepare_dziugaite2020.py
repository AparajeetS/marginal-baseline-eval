from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd


EXPECTED_SHA256 = "1fc11e07bd3826cbf887004c1d5cbf5450102a34bd99d368f05a5c1cd603a9fc"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prepare the official Dziugaite et al. (2020) model ledger for MBE."
    )
    parser.add_argument("source", type=Path, help="Official nin.cifar10_svhn.csv file.")
    parser.add_argument("output", type=Path, help="Destination for the cleaned run ledger.")
    args = parser.parse_args()

    digest = hashlib.sha256(args.source.read_bytes()).hexdigest()
    if digest != EXPECTED_SHA256:
        raise ValueError(
            "source SHA-256 does not match the frozen official artifact: "
            f"expected {EXPECTED_SHA256}, got {digest}"
        )

    data = pd.read_csv(args.source)
    required = {
        "experiment_id",
        "repeat_id",
        "is.converged",
        "is.high_train_accuracy",
        "hp.lr",
        "hp.dataset",
    }
    missing = sorted(required - set(data.columns))
    if missing:
        raise ValueError(f"source is missing required columns: {', '.join(missing)}")

    input_rows = len(data)
    data = data.loc[data["is.converged"].astype(bool)].copy()
    converged_rows = len(data)
    data = data.loc[data["is.high_train_accuracy"].astype(bool)].copy()
    accurate_rows = len(data)
    data = data.replace([np.inf, -np.inf], np.nan).dropna().copy()
    finite_rows = len(data)

    # Match the upstream loader's device-tolerance normalization.
    data["hp.lr"] = data["hp.lr"].round(4)
    data["run_id"] = (
        data["experiment_id"].astype(str) + ":" + data["repeat_id"].astype(str)
    )
    data["config_id"] = data["experiment_id"].astype(str)
    if data["run_id"].duplicated().any():
        raise ValueError("prepared run_id values are not unique")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(args.output, index=False)
    print(f"source_sha256={digest}")
    print(
        "rows: "
        f"input={input_rows}, converged={converged_rows}, "
        f"high_train_accuracy={accurate_rows}, finite={finite_rows}"
    )
    print(
        f"prepared={args.output} rows={len(data)} "
        f"configs={data['config_id'].nunique()} datasets={data['hp.dataset'].nunique()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
