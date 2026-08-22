from __future__ import annotations

from pathlib import Path

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[2]
CAMPAIGN_OUT = REPO_ROOT / "experiments/17_cpu_credibility_campaign/out"
OBSERVED_ROOT = (
    REPO_ROOT / "experiments/16_causal_text_observed_design_power"
)
DEGREES = (1, 2, 3, 4, 6)
NUISANCE_MODELS = (
    "polynomial_ridge",
    "polynomial_ridge_interactions",
)
OBSERVED_DIRS = {
    1: "out_sensitivity_degree1",
    2: "out_sensitivity_degree2",
    3: "out_sensitivity_degree3",
    4: "out_sensitivity_degree4",
    6: "out_primary",
}


def load_generic() -> pd.DataFrame:
    frames = []
    for nuisance in NUISANCE_MODELS:
        existing = pd.read_csv(
            CAMPAIGN_OUT / f"monte_carlo_{nuisance}/monte_carlo_summary.csv"
        )
        frames.append(existing.loc[existing["polynomial_degree"].isin((2, 6))])
        for degree in (1, 3, 4):
            frames.append(
                pd.read_csv(
                    CAMPAIGN_OUT
                    / f"complexity_generic_{nuisance}_degree{degree}"
                    / "monte_carlo_summary.csv"
                )
            )
    return pd.concat(frames, ignore_index=True)


def load_observed() -> tuple[pd.DataFrame, pd.DataFrame]:
    ledgers = []
    summaries = []
    for degree, directory in OBSERVED_DIRS.items():
        ledger = pd.read_csv(OBSERVED_ROOT / directory / "power_ledger.csv")
        summary = pd.read_csv(OBSERVED_ROOT / directory / "power_summary.csv")
        ledger["degree"] = degree
        summary["degree"] = degree
        ledgers.append(ledger)
        summaries.append(summary)
    return pd.concat(ledgers, ignore_index=True), pd.concat(
        summaries, ignore_index=True
    )


def build_table() -> pd.DataFrame:
    generic = load_generic()
    observed, observed_summary = load_observed()
    rows = []
    for degree in DEGREES:
        strict_large = observed_summary.loc[
            observed_summary["degree"].eq(degree)
            & observed_summary["beta"].eq(0.5),
            "strict_support_rate",
        ].mean()
        for nuisance in NUISANCE_MODELS:
            generic_cell = generic.loc[
                generic["polynomial_degree"].eq(degree)
                & generic["nuisance_model"].eq(nuisance)
            ]
            observed_cell = observed.loc[
                observed["degree"].eq(degree)
                & observed["nuisance_model"].eq(nuisance)
                & observed["status"].eq("estimated")
            ]
            null = generic_cell.loc[~generic_cell["expected_signal"]]
            signal = generic_cell.loc[generic_cell["expected_signal"]]
            row = {
                "degree": degree,
                "nuisance_model": nuisance,
                "generic_max_null_proxy_joint_rate": null[
                    "joint_increment_decision_rate"
                ].max(),
                "generic_min_signal_joint_rate": signal[
                    "joint_increment_decision_rate"
                ].min(),
                "observed_strict_beta_0_5_rate": strict_large,
            }
            for effect in (0.0, 0.2, 0.3, 0.5):
                row[f"observed_predictive_beta_{str(effect).replace('.', '_')}_rate"] = (
                    observed_cell.loc[
                        observed_cell["beta"].eq(effect),
                        "predictive_supported",
                    ].mean()
                )
            rows.append(row)
    return pd.DataFrame(rows)


def write_markdown(table: pd.DataFrame, path: Path) -> None:
    labels = {
        "polynomial_ridge": "additive",
        "polynomial_ridge_interactions": "interactions",
    }
    lines = [
        "# Nuisance-Complexity Ablation",
        "",
        "This table combines two known-truth calibration axes. The generic axis",
        "tests null/proxy control and signal recovery. The observed-design axis",
        "tests full-refit power in the exact 36-configuration causal-text",
        "geometry. It is not a real-metric outcome comparison.",
        "",
        "| Degree | Family | Generic max null/proxy joint | Generic min signal joint | Observed beta=0 | beta=0.2 | beta=0.3 | beta=0.5 | Strict beta=0.5 |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in table.iterrows():
        lines.append(
            f"| {int(row['degree'])} | {labels[row['nuisance_model']]} | "
            f"{row['generic_max_null_proxy_joint_rate']:.1%} | "
            f"{row['generic_min_signal_joint_rate']:.1%} | "
            f"{row['observed_predictive_beta_0_0_rate']:.1%} | "
            f"{row['observed_predictive_beta_0_2_rate']:.1%} | "
            f"{row['observed_predictive_beta_0_3_rate']:.1%} | "
            f"{row['observed_predictive_beta_0_5_rate']:.1%} | "
            f"{row['observed_strict_beta_0_5_rate']:.1%} |"
        )
    lines.extend(
        [
            "",
            "## Reading The Result",
            "",
            "- Degrees 1-3 recover observed-design signal but reach 100% false",
            "  support in at least one generic null/proxy cell.",
            "- Degree 4 reduces the worst generic false support to 17% for the",
            "  additive family and 5% for the interaction family.",
            "- Degree 6 reduces the worst generic false support to 0% and 3%,",
            "  respectively, while retaining 98.3% additive power at beta=0.5.",
            "- The interaction family has only 1.0%-4.6% observed-design power",
            "  at beta=0.5 across every tested degree.",
            "- Consequently, mandatory two-family agreement has at most 4.6%",
            "  large-effect power in this 36-configuration design.",
            "",
            "There is no degree that makes the current universal two-family",
            "consensus both proxy-safe and adequately powered here. MBE must",
            "treat nuisance-family eligibility as design-specific calibration",
            "and abstain when no preregistered family passes both control and",
            "power gates. Choosing the most favorable degree after real-metric",
            "inspection is not permitted.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    table = build_table()
    output = CAMPAIGN_OUT / "pooled"
    output.mkdir(parents=True, exist_ok=True)
    table.to_csv(output / "nuisance_complexity_ablation.csv", index=False)
    write_markdown(
        table,
        REPO_ROOT
        / "experiments/17_cpu_credibility_campaign"
        / "NUISANCE_COMPLEXITY_ABLATION.md",
    )
    print(table.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
