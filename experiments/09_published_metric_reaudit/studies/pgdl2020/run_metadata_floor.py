from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from mbe_eval import audit_metric, cross_fitted_audit


def main() -> int:
    parser = argparse.ArgumentParser(description="Measure the PGDL cheap-information floor.")
    parser.add_argument("ledger", type=Path)
    parser.add_argument("plan", type=Path)
    parser.add_argument("--output-prefix", type=Path, required=True)
    parser.add_argument("--permutations", type=int, default=199)
    parser.add_argument("--bootstrap", type=int, default=499)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--degrees", default="4,6")
    parser.add_argument(
        "--nuisance-models",
        default="polynomial_ridge,polynomial_ridge_interactions",
    )
    args = parser.parse_args()

    data = pd.read_csv(args.ledger)
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    degrees = tuple(int(value.strip()) for value in args.degrees.split(",") if value.strip())
    nuisance_models = tuple(
        value.strip() for value in args.nuisance_models.split(",") if value.strip()
    )
    rows: list[dict[str, object]] = []
    for task_index, (task, controls) in enumerate(plan["task_controls"].items()):
        frame = data.loc[data["task"] == task].copy()
        legacy = audit_metric(
            frame,
            "train_loss",
            plan["primary_target"],
            controls,
        )
        for model_index, nuisance_model in enumerate(nuisance_models):
            model_degrees = degrees if nuisance_model == "polynomial_ridge" else (6,)
            for degree in model_degrees:
                crossfit = cross_fitted_audit(
                    frame,
                    "train_loss",
                    plan["primary_target"],
                    controls,
                    degree=degree,
                    nuisance_model=nuisance_model,
                    permutations=args.permutations,
                    bootstrap=args.bootstrap,
                    seed=args.seed + task_index * 100 + model_index * 10 + degree,
                )
                rows.append(
                    {
                "task": task,
                "split": frame["split"].iloc[0],
                "n": len(frame),
                "nuisance_model": nuisance_model,
                "polynomial_degree": degree,
                "target": plan["primary_target"],
                "controls": ",".join(controls),
                "raw_train_loss_r": legacy["raw_r"],
                "partial_train_loss_r": legacy["partial_r"],
                "crossfit_train_loss_residual_r": crossfit["residual_r"],
                "crossfit_permutation_p": crossfit["residual_p"],
                "residual_ci_low": crossfit["residual_ci_low"],
                "residual_ci_high": crossfit["residual_ci_high"],
                "hyperparameter_baseline_mse": crossfit["baseline_mse"],
                "plus_train_loss_mse": crossfit["augmented_mse"],
                "train_loss_delta_mse": crossfit["delta_mse"],
                "delta_mse_ci_low": crossfit["delta_mse_ci_low"],
                "delta_mse_ci_high": crossfit["delta_mse_ci_high"],
                "relative_mse_improvement": crossfit["relative_mse_improvement"],
                "increment_classification": crossfit["increment_classification"],
                    }
                )

    report = pd.DataFrame(rows)
    args.output_prefix.parent.mkdir(parents=True, exist_ok=True)
    report.to_csv(args.output_prefix.with_suffix(".csv"), index=False)
    lines = [
        "# PGDL Metadata Baseline Floor",
        "",
        "This table measures final training loss beyond each task's declared hyperparameters. It contains no checkpoint-derived metric results and does not open the protected holdout metric evaluation.",
        "",
        "| Task | Split | Nuisance | Degree | n | Hyperparameter MSE | + train-loss MSE | Delta MSE [95% CI] | Residual rho [95% CI] | Evidence |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for _, row in report.iterrows():
        lines.append(
            f"| {row['task']} | {row['split']} | {row['nuisance_model']} | "
            f"{row['polynomial_degree']} | {row['n']} | "
            f"{row['hyperparameter_baseline_mse']:.4f} | {row['plus_train_loss_mse']:.4f} | "
            f"{row['train_loss_delta_mse']:.4f} [{row['delta_mse_ci_low']:.4f}, {row['delta_mse_ci_high']:.4f}] | "
            f"{row['crossfit_train_loss_residual_r']:.3f} [{row['residual_ci_low']:.3f}, {row['residual_ci_high']:.3f}] | "
            f"{row['increment_classification']} |"
        )
    lines.extend(
        [
            "",
            "Training accuracy is not tested as a candidate because it is part of the accuracy-gap target. Hyperparameter MSE is an out-of-fold rank-target error, so it is a benchmark floor rather than an estimate in original accuracy units.",
            "",
        ]
    )
    args.output_prefix.with_suffix(".md").write_text("\n".join(lines), encoding="utf-8")
    print(report.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
