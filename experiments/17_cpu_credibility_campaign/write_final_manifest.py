from __future__ import annotations

import hashlib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT = (
    REPO_ROOT
    / "experiments/17_cpu_credibility_campaign"
    / "FINAL_SHA256SUMS"
)
PATTERNS = (
    "docs/EVIDENCE_INDEX.md",
    "docs/MBE_CREDIBILITY_LEDGER.md",
    "docs/STATISTICAL_ESTIMAND_AND_INFERENCE.md",
    "paper/JMLR_MANUSCRIPT_SKELETON.md",
    "paper/tables/claim_ledger.md",
    "SUPPORTING_EVIDENCE.md",
    "experiments/08_protocol_calibration/out/CREDIBILITY_SUMMARY.md",
    "experiments/08_protocol_calibration/summarize_credibility.py",
    "experiments/16_causal_text_observed_design_power/*.md",
    "experiments/16_causal_text_observed_design_power/*.py",
    "experiments/16_causal_text_observed_design_power/*.sh",
    "experiments/16_causal_text_observed_design_power/out_primary/power_ledger.csv",
    "experiments/16_causal_text_observed_design_power/out_primary/power_summary.csv",
    "experiments/16_causal_text_observed_design_power/out_primary/reliability_tiers.csv",
    "experiments/16_causal_text_observed_design_power/out_primary/run_manifest.json",
    "experiments/16_causal_text_observed_design_power/out_sensitivity_degree*/power_ledger.csv",
    "experiments/16_causal_text_observed_design_power/out_sensitivity_degree*/power_summary.csv",
    "experiments/16_causal_text_observed_design_power/out_sensitivity_degree*/reliability_tiers.csv",
    "experiments/16_causal_text_observed_design_power/out_sensitivity_degree*/run_manifest.json",
    "experiments/16_causal_text_observed_design_power/vm_campaign_artifacts/complexity_*",
    "experiments/17_cpu_credibility_campaign/*.md",
    "experiments/17_cpu_credibility_campaign/*.py",
    "experiments/17_cpu_credibility_campaign/*.sh",
    "experiments/17_cpu_credibility_campaign/out/generic_complexity_status.tsv",
    "experiments/17_cpu_credibility_campaign/out/complexity_generic_*/*",
    "experiments/17_cpu_credibility_campaign/out/inference_shard_*/*",
    "experiments/17_cpu_credibility_campaign/out/pooled/inference_stress_*",
    "experiments/17_cpu_credibility_campaign/out/pooled/merge_manifest.json",
    "experiments/17_cpu_credibility_campaign/out/pooled/nuisance_complexity_ablation.csv",
    "experiments/17_cpu_credibility_campaign/vm_campaign_artifacts/logs/complexity_generic_*",
    "experiments/18_refit_draw_convergence/*.md",
    "experiments/18_refit_draw_convergence/*.py",
    "experiments/18_refit_draw_convergence/*.sh",
    "experiments/18_refit_draw_convergence/out/draw_convergence_ledger.csv",
    "experiments/18_refit_draw_convergence/out/draw_convergence_summary.csv",
    "experiments/18_refit_draw_convergence/out/draw_convergence_comparison.csv",
    "experiments/18_refit_draw_convergence/out/run_manifest.json",
    "experiments/18_refit_draw_convergence/vm_campaign_artifacts/*",
    "dist/mbe_eval-0.4.0-py3-none-any.whl",
    "dist/mbe_eval-0.4.0.tar.gz",
)


def digest(path: Path) -> str:
    checksum = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            checksum.update(chunk)
    return checksum.hexdigest()


def main() -> int:
    paths: set[Path] = set()
    for pattern in PATTERNS:
        paths.update(path for path in REPO_ROOT.glob(pattern) if path.is_file())
    paths.discard(OUTPUT)
    lines = [
        f"{digest(path)}  {path.relative_to(REPO_ROOT).as_posix()}"
        for path in sorted(paths, key=lambda item: item.as_posix())
    ]
    OUTPUT.write_text("\n".join(lines) + "\n", encoding="ascii")
    print(f"wrote {len(lines)} hashes to {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
