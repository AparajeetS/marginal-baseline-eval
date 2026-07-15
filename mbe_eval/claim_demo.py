from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from . import __version__
from .claim_card import audit_benchmark_claim, claim_card_json, claim_card_markdown


DEMO_ENVIRONMENTS = (
    "truthfulness_style",
    "sycophancy_style",
    "faithfulness_style",
    "distribution_shift",
)


def _modular_signal(index: np.ndarray, multiplier: int, offset: int) -> np.ndarray:
    return (((multiplier * index + offset) % 193) - 96) / 96


def make_claim_demo(n_units: int = 96) -> pd.DataFrame:
    """Create a deterministic known-ground-truth benchmark-audit fixture."""

    if n_units < 20:
        raise ValueError("n_units must be at least 20")
    unit_index = np.repeat(np.arange(n_units), len(DEMO_ENVIRONMENTS))
    environment_index = np.tile(np.arange(len(DEMO_ENVIRONMENTS)), n_units)
    row_index = np.arange(len(unit_index))

    capability = 0.55 + 0.24 * _modular_signal(unit_index, 37, 11)
    capability += 0.015 * environment_index
    latent_property = _modular_signal(unit_index, 83, 17)
    observation_noise = 0.08 * _modular_signal(row_index, 61, 23)

    benchmark_score = (
        latent_property
        + 0.16 * capability
        + 0.05 * _modular_signal(row_index, 107, 31)
    )
    deceptive_score = capability + 0.02 * _modular_signal(row_index, 127, 29)
    random_score = _modular_signal(row_index, 100, 41)
    external_outcome = 1.15 * capability + 0.85 * latent_property + observation_noise

    return pd.DataFrame(
        {
            "evaluation_id": [f"eval_{i:04d}" for i in row_index],
            "model_id": [f"model_{i:03d}" for i in unit_index],
            "environment": [DEMO_ENVIRONMENTS[i] for i in environment_index],
            "capability_proxy": capability,
            "benchmark_score": benchmark_score,
            "deceptive_score": deceptive_score,
            "random_score": random_score,
            "external_outcome": external_outcome,
        }
    )


def run_claim_demo(
    *,
    output_dir: str | Path = "mbe_claim_demo",
    n_units: int = 96,
    permutations: int = 99,
    bootstrap: int = 199,
    seed: int = 20260715,
) -> dict[str, object]:
    """Run the synthetic self-check and write its input and claim card."""

    frame = make_claim_demo(n_units=n_units)
    card = audit_benchmark_claim(
        frame,
        claim_id="synthetic-transfer-fixture",
        claim_text=(
            "In this known-ground-truth synthetic fixture, benchmark_score adds "
            "out-of-sample information about external_outcome beyond the declared "
            "capability_proxy and transfers across the four named environments."
        ),
        metric="benchmark_score",
        target="external_outcome",
        baselines=["capability_proxy"],
        environment="environment",
        unit="model_id",
        deceptive_control="deceptive_score",
        negative_controls=["random_score"],
        min_relative_mse_improvement=0.01,
        min_transport_relative_mse_improvement=0.005,
        degree=2,
        permutations=permutations,
        bootstrap=bootstrap,
        seed=seed,
    )
    card["source"] = {
        "file": "synthetic_benchmark_audit.csv",
        "kind": "deterministic-known-ground-truth-fixture",
        "generator": "mbe_eval.claim_demo.make_claim_demo",
    }

    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    frame.to_csv(directory / "synthetic_benchmark_audit.csv", index=False)
    (directory / "claim_card.json").write_text(claim_card_json(card), encoding="utf-8")
    (directory / "claim_card.md").write_text(claim_card_markdown(card), encoding="utf-8")
    return card


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run the deterministic MBE benchmark-audit prototype self-check. "
            "Synthetic success does not validate real-world use."
        )
    )
    parser.add_argument("--version", action="version", version=f"mbe-eval {__version__}")
    parser.add_argument("--output-dir", default="mbe_claim_demo")
    parser.add_argument("--n-units", type=int, default=96)
    parser.add_argument("--permutations", type=int, default=99)
    parser.add_argument("--bootstrap", type=int, default=199)
    parser.add_argument("--seed", type=int, default=20260715)
    args = parser.parse_args(argv)

    card = run_claim_demo(
        output_dir=args.output_dir,
        n_units=args.n_units,
        permutations=args.permutations,
        bootstrap=args.bootstrap,
        seed=args.seed,
    )
    print(f"Synthetic predeclared test outcome: {card['evidence_state']}")
    print(f"Wrote {Path(args.output_dir).resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = ["DEMO_ENVIRONMENTS", "make_claim_demo", "run_claim_demo", "main"]
