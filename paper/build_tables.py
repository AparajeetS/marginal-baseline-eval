from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent / "tables"


def markdown_table(frame: pd.DataFrame) -> str:
    columns = list(frame.columns)
    lines = [
        "| " + " | ".join(columns) + " |",
        "|" + "|".join("---" for _ in columns) + "|",
    ]
    for _, row in frame.iterrows():
        lines.append("| " + " | ".join(str(row[column]) for column in columns) + " |")
    return "\n".join(lines) + "\n"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    factorial = pd.read_csv(
        ROOT / "experiments/10_method_comparison/out/factorial_method_summary.csv"
    )[
        [
            "scenario",
            "mbe_additive_support_rate",
            "mbe_interaction_support_rate",
            "raw_spearman_median",
            "jiang_cmi_median",
        ]
    ].round(3)
    factorial.columns = ["Scenario", "Additive MBE", "Interaction MBE", "Raw Spearman", "Jiang CMI"]
    (OUT / "method_comparison.md").write_text(markdown_table(factorial), encoding="utf-8")

    blocks = pd.read_csv(
        ROOT / "experiments/10_method_comparison/out/inference_stress_block_summary.csv"
    ).round(3)
    blocks.columns = ["Structure", "Repetitions", "Rejections", "Rate", "Wilson low", "Wilson high"]
    (OUT / "inference_calibration.md").write_text(markdown_table(blocks), encoding="utf-8")

    claims = json.loads(
        (ROOT / "experiments/11_credibility_freeze/claim_ledger.json").read_text(encoding="utf-8")
    )
    claim_frame = pd.DataFrame(
        [{"Claim": claim["id"], "Status": claim["status"], "Scope": claim["scope"]} for claim in claims["claims"]]
    )
    (OUT / "claim_ledger.md").write_text(markdown_table(claim_frame), encoding="utf-8")
    print(f"wrote paper tables to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
