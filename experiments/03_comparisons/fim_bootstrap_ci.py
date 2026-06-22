"""
CEI v2 — Bootstrap confidence intervals on Spearman rho.

For a paper, point estimates are not enough. This script computes 95% CIs
on the key Spearman correlations via 10,000 bootstrap resamples.

Reports CI for:
  - FIM_norm vs test_acc (noise probe + n_train probe, MLP + CNN)
  - Sharpness vs test_acc (same)
  - FIM_norm@ep20 vs final test_acc (leading indicator claim)

Output: fim_bootstrap_ci.txt (table for paper)
"""

import sys
import numpy as np
from pathlib import Path
from scipy.stats import spearmanr

SEED = 42
OUT  = Path(__file__).parent
np.random.seed(SEED)


def bootstrap_spearman_ci(x, y, n_boot=10000, ci=0.95):
    """Bootstrap CI for Spearman rho."""
    x, y = np.array(x), np.array(y)
    n    = len(x)
    rho_obs, _ = spearmanr(x, y)
    boot_rhos  = []
    for _ in range(n_boot):
        idx = np.random.randint(0, n, n)
        r, _ = spearmanr(x[idx], y[idx])
        boot_rhos.append(r)
    alpha = (1 - ci) / 2
    lo    = np.percentile(boot_rhos, 100 * alpha)
    hi    = np.percentile(boot_rhos, 100 * (1 - alpha))
    return rho_obs, lo, hi


def run():
    # Load saved results from previous experiments
    # Re-run slim versions to get the arrays needed

    sys.path.insert(0, str(Path(__file__).parent))
    from sci_tracker import effective_rank
    from fim_full_study import MLP, run_cond
    import torch
    from fim_cnn_test import DigitsCNN, fim_norm_torch, train_cond as cnn_train
    from sklearn.datasets import load_digits
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler

    X, y = load_digits(return_X_y=True)
    X    = StandardScaler().fit_transform(X)
    X_ev, X_pool, y_ev, y_pool = train_test_split(
        X, y, test_size=len(X)-200, random_state=SEED)

    SEEDS  = [42, 7, 123]
    NOISE  = [0.0, 0.15, 0.30, 0.50]
    NTRAIN = [40, 200, 400, 800]

    def fim_norm_quick(model, X_tr, y_tr, N=100):
        from sci_tracker import effective_rank
        import math
        n    = len(X_tr)
        n_use = min(N, n)
        idx  = np.random.choice(n, n_use, replace=False)
        G    = np.array([model._grad_single(X_tr[k], y_tr[k]) for k in idx])
        F_d  = (G @ G.T) / n_use
        sv   = np.linalg.svd(F_d, compute_uv=False)
        sv   = sv[sv > 1e-10]
        if len(sv) == 0: return 1.0 / n_use
        p    = sv / sv.sum()
        H    = -(p * np.log(p + 1e-12)).sum()
        return math.exp(H) / n_use

    def sam_quick(model, X_tr, y_tr, rho=0.05):
        from fim_full_study import MLP as _MLP
        n   = min(100, len(X_tr))
        idx = np.random.choice(len(X_tr), n, replace=False)
        return model.sam_sharpness(X_tr[idx], y_tr[idx])

    print("Collecting MLP data for bootstrap CIs...")
    mlp_noise_fim, mlp_noise_sharp, mlp_noise_te = [], [], []
    mlp_ntrain_fim, mlp_ntrain_sharp, mlp_ntrain_te = [], [], []
    mlp_early_fim, mlp_early_sharp, mlp_final_te = [], [], []

    # MLP noise probe
    for noise in NOISE:
        for seed in SEEDS:
            np.random.seed(seed)
            X_tr, _, y_tr, _ = train_test_split(
                X_pool, y_pool, train_size=400, random_state=seed)
            y_use = y_tr.copy()
            if noise > 0:
                nf = int(noise * len(y_tr))
                fi = np.random.choice(len(y_tr), nf, replace=False)
                y_use[fi] = np.random.randint(0, 10, nf)
            _, log = run_cond(X_tr, y_use, X_ev, y_ev)
            r = log[-1]
            mlp_noise_fim.append(r["fim_norm"])
            mlp_noise_sharp.append(r["sharpness"])
            mlp_noise_te.append(r["te"])

    # MLP n_train probe + early predictor
    for n in NTRAIN:
        for seed in SEEDS:
            np.random.seed(seed)
            X_tr, _, y_tr, _ = train_test_split(
                X_pool, y_pool, train_size=n, random_state=seed)
            _, log = run_cond(X_tr, y_tr, X_ev, y_ev)
            r = log[-1]
            ep20 = next((x for x in log if x["ep"] >= 20), log[0])
            mlp_ntrain_fim.append(r["fim_norm"])
            mlp_ntrain_sharp.append(r["sharpness"])
            mlp_ntrain_te.append(r["te"])
            mlp_early_fim.append(ep20["fim_norm"])
            mlp_early_sharp.append(ep20["sharpness"])
            mlp_final_te.append(r["te"])

    print("Collecting CNN data for bootstrap CIs...")
    cnn_noise_fim, cnn_noise_te = [], []
    cnn_ntrain_fim, cnn_ntrain_te = [], []

    for noise in NOISE:
        for seed in SEEDS:
            np.random.seed(seed); torch.manual_seed(seed)
            X_tr, _, y_tr, _ = train_test_split(
                X_pool, y_pool, train_size=400, random_state=seed)
            y_use = y_tr.copy()
            if noise > 0:
                nf = int(noise * len(y_tr))
                fi = np.random.choice(len(y_tr), nf, replace=False)
                y_use[fi] = np.random.randint(0, 10, nf)
            log = cnn_train(X_tr, y_use, X_ev, y_ev)
            r   = log[-1]
            cnn_noise_fim.append(r["fim_norm"])
            cnn_noise_te.append(r["te"])

    for n in NTRAIN:
        for seed in SEEDS:
            np.random.seed(seed); torch.manual_seed(seed)
            X_tr, _, y_tr, _ = train_test_split(
                X_pool, y_pool, train_size=n, random_state=seed)
            log = cnn_train(X_tr, y_tr, X_ev, y_ev)
            r   = log[-1]
            cnn_ntrain_fim.append(r["fim_norm"])
            cnn_ntrain_te.append(r["te"])

    print("Computing bootstrap CIs (10,000 resamples)...")

    rows = [
        ("MLP noise    FIM_norm  ", mlp_noise_fim,   mlp_noise_te),
        ("MLP noise    Sharpness ", mlp_noise_sharp,  mlp_noise_te),
        ("MLP n_train  FIM_norm  ", mlp_ntrain_fim,  mlp_ntrain_te),
        ("MLP n_train  Sharpness ", mlp_ntrain_sharp, mlp_ntrain_te),
        ("MLP@ep20     FIM_norm  ", mlp_early_fim,   mlp_final_te),
        ("MLP@ep20     Sharpness ", mlp_early_sharp,  mlp_final_te),
        ("CNN noise    FIM_norm  ", cnn_noise_fim,   cnn_noise_te),
        ("CNN n_train  FIM_norm  ", cnn_ntrain_fim,  cnn_ntrain_te),
    ]

    print(f"\n{'Experiment + Metric':<32} {'rho':>7}  {'95% CI':>18}  {'n':>4}")
    print("  " + "-"*65)
    lines = []
    for label, x, y in rows:
        rho, lo, hi = bootstrap_spearman_ci(x, y)
        sig = "*" if (lo > 0 or hi < 0) else " "
        line = (f"  {label}  rho={rho:+.3f}  "
                f"[{lo:+.3f}, {hi:+.3f}]{sig}  n={len(x)}")
        print(line)
        lines.append(line)

    with open(OUT / "fim_bootstrap_ci.txt", "w") as f:
        f.write("FIM_norm Bootstrap 95% CI (10,000 resamples)\n")
        f.write("=" * 70 + "\n")
        f.write(f"{'Experiment + Metric':<32} {'rho':>7}  {'95% CI':>18}  {'n':>4}\n")
        f.write("-" * 65 + "\n")
        for line in lines:
            f.write(line + "\n")
        f.write("\n* = CI excludes zero (significant at alpha=0.05)\n")
    print(f"\nSaved: {OUT / 'fim_bootstrap_ci.txt'}")


if __name__ == "__main__":
    run()
