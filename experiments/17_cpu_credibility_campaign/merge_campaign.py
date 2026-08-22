from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[2]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_shards(paths: list[Path], filename: str) -> pd.DataFrame:
    frames = []
    for path in paths:
        frame = pd.read_csv(path / filename)
        frame.insert(0, "shard", path.name)
        frames.append(frame)
    return pd.concat(frames, ignore_index=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--campaign-dir",
        type=Path,
        default=Path(__file__).parent / "out",
    )
    args = parser.parse_args()
    pooled = args.campaign_dir / "pooled"
    pooled.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, object] = {}

    factorial_dirs = sorted(args.campaign_dir.glob("factorial_shard_*"))
    if factorial_dirs:
        factorial = read_shards(factorial_dirs, "factorial_method_ledger.csv")
        duplicate_key = ["seed", "scenario"]
        if factorial.duplicated(duplicate_key).any():
            raise ValueError("duplicate factorial seed/scenario cells across shards")
        factorial_module = load_module(
            "mbe_factorial_benchmark",
            REPO_ROOT
            / "experiments/10_method_comparison/run_factorial_benchmark.py",
        )
        factorial_summary = factorial_module.summarize(factorial)
        factorial.to_csv(pooled / "factorial_method_ledger.csv", index=False)
        factorial_summary.to_csv(
            pooled / "factorial_method_summary.csv", index=False
        )
        manifest["factorial"] = {
            "shards": len(factorial_dirs),
            "rows": len(factorial),
            "repetitions_per_scenario": int(
                factorial.groupby("scenario").size().min()
            ),
        }

    monte_dirs = sorted(args.campaign_dir.glob("monte_carlo_*"))
    if monte_dirs:
        monte_ledgers = [
            pd.read_csv(path / "monte_carlo_ledger.csv") for path in monte_dirs
        ]
        monte_summaries = [
            pd.read_csv(path / "monte_carlo_summary.csv") for path in monte_dirs
        ]
        monte = pd.concat(monte_ledgers, ignore_index=True)
        monte_summary = pd.concat(monte_summaries, ignore_index=True).sort_values(
            [
                "scenario",
                "nuisance_model",
                "n",
                "polynomial_degree",
            ]
        )
        duplicate_key = [
            "scenario",
            "nuisance_model",
            "n",
            "polynomial_degree",
            "seed",
        ]
        if monte.duplicated(duplicate_key).any():
            raise ValueError("duplicate Monte Carlo cells")
        monte.to_csv(pooled / "monte_carlo_ledger.csv", index=False)
        monte_summary.to_csv(pooled / "monte_carlo_summary.csv", index=False)
        manifest["monte_carlo"] = {
            "nuisance_families": sorted(monte["nuisance_model"].unique().tolist()),
            "rows": len(monte),
            "repetitions_per_cell": int(
                monte.groupby(
                    ["scenario", "nuisance_model", "n", "polynomial_degree"]
                ).size().min()
            ),
        }

    inference_dirs = sorted(args.campaign_dir.glob("inference_shard_*"))
    complete_inference = [
        path
        for path in inference_dirs
        if (path / "inference_stress_refit_ledger.csv").is_file()
        and (path / "inference_stress_block_ledger.csv").is_file()
    ]
    if complete_inference:
        if len(complete_inference) != 8:
            raise ValueError(
                f"expected 8 complete inference shards, found {len(complete_inference)}"
            )
        inference_module = load_module(
            "mbe_inference_stress",
            REPO_ROOT
            / "experiments/10_method_comparison/run_inference_stress.py",
        )
        refit = read_shards(
            complete_inference, "inference_stress_refit_ledger.csv"
        )
        blocks = read_shards(
            complete_inference, "inference_stress_block_ledger.csv"
        )
        refit_summary = inference_module.summarize_refit(refit)
        block_summary = inference_module.summarize_blocks(blocks)
        refit.to_csv(pooled / "inference_stress_refit_ledger.csv", index=False)
        blocks.to_csv(pooled / "inference_stress_block_ledger.csv", index=False)
        refit_summary.to_csv(
            pooled / "inference_stress_refit_summary.csv", index=False
        )
        block_summary.to_csv(
            pooled / "inference_stress_block_summary.csv", index=False
        )
        manifest["inference_stress"] = {
            "shards": len(complete_inference),
            "refit_rows": len(refit),
            "block_rows": len(blocks),
            "repetitions_per_refit_cell": int(
                refit.groupby(
                    ["sample_size", "scenario", "nuisance_model"]
                ).size().min()
            ),
            "repetitions_per_block_structure": int(
                blocks.groupby("structure").size().min()
            ),
        }

    (pooled / "merge_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

