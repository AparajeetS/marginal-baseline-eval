"""
CEI v2 — FIM_norm sample-count stability test.

How many per-sample gradients do you actually need?
Tests N_FIM in {5, 10, 20, 50, 100, 200} on 3 trained models.

If FIM_norm is stable at N=50, it's practical for real training pipelines.
Output: fim_stability_results.png
"""

import sys, math
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).parent))
from sci_tracker import effective_rank
from fim_full_study import MLP, run_cond   # reuse numpy MLP

SEED = 42
OUT  = Path(__file__).parent


def fim_norm_at_n(model, X_pool, y_pool, n_samples, n_trials=20):
    """Run FIM estimation n_trials times with n_samples; return mean and std."""
    vals = []
    pool_n = len(X_pool)
    for _ in range(n_trials):
        n_use = min(n_samples, pool_n)
        idx   = np.random.choice(pool_n, n_use, replace=False)
        G     = np.array([model._grad_single(X_pool[k], y_pool[k]) for k in idx])
        F_d   = (G @ G.T) / n_use
        vals.append(effective_rank(F_d) / n_use)
    return float(np.mean(vals)), float(np.std(vals))


def run():
    X, y = load_digits(return_X_y=True)
    X    = StandardScaler().fit_transform(X)
    X_ev, X_pool, y_ev, y_pool = train_test_split(
        X, y, test_size=len(X)-200, random_state=SEED)

    np.random.seed(SEED)
    SAMPLE_COUNTS = [5, 10, 20, 50, 100, 200]

    # train 3 models: overfit, generalise, noisy
    configs = [
        {"n": 40,  "l2": 0.0,   "noise": 0.0,  "label": "overfit (n=40)"},
        {"n": 400, "l2": 0.0,   "noise": 0.0,  "label": "generalise (n=400)"},
        {"n": 400, "l2": 0.0,   "noise": 0.30, "label": "noisy 30% (n=400)"},
    ]
    COLS = ["#e74c3c", "#2ecc71", "#9b59b6"]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("FIM_norm Stability vs N_FIM (per-sample gradients)\n"
                 "20 trials per N, error bars = std across trials", fontweight="bold")

    ax_mean, ax_cv = axes

    for cfg, col in zip(configs, COLS):
        np.random.seed(SEED)
        X_tr, _, y_tr, _ = train_test_split(
            X_pool, y_pool, train_size=cfg["n"], random_state=SEED)
        y_use = y_tr.copy()
        if cfg["noise"] > 0:
            nf = int(cfg["noise"] * len(y_tr))
            fi = np.random.choice(len(y_tr), nf, replace=False)
            y_use[fi] = np.random.randint(0, 10, nf)
        _, log = run_cond(X_tr, y_use, X_ev, y_ev)
        # rebuild model from log — actually need final model; retrain
        np.random.seed(SEED)
        model_final = MLP(l2=cfg["l2"])
        for _ in range(200):
            idx = np.random.permutation(len(X_tr))
            for s in range(0, len(X_tr), 64):
                b = idx[s:s+64]
                model_final.step(X_tr[b], y_use[b], 0.005)

        means, stds, cvs = [], [], []
        for n_s in SAMPLE_COUNTS:
            n_s_eff = min(n_s, len(X_tr))
            m, s = fim_norm_at_n(model_final, X_tr, y_use, n_s_eff)
            means.append(m); stds.append(s)
            cvs.append(s / m if m > 0 else 0)
            print(f"  {cfg['label']}  N={n_s_eff:3d}: "
                  f"FIM_norm={m:.4f} ± {s:.4f}  CV={s/m:.3f}")

        ax_mean.errorbar(SAMPLE_COUNTS, means, yerr=stds, color=col,
                         marker="o", linewidth=2, capsize=4, label=cfg["label"])
        ax_cv.plot(SAMPLE_COUNTS, cvs, color=col, marker="s",
                   linewidth=2, label=cfg["label"])

    ax_mean.set_title("FIM_norm mean ± std vs N_FIM")
    ax_mean.set_xlabel("N_FIM (per-sample gradients)")
    ax_mean.set_ylabel("FIM_norm"); ax_mean.legend(); ax_mean.grid(alpha=0.3)
    ax_mean.set_xscale("log")

    ax_cv.axhline(0.05, color="gray", linestyle="--", linewidth=1,
                  label="CV=5% threshold")
    ax_cv.set_title("Coefficient of Variation vs N_FIM\n(CV < 5% = stable)")
    ax_cv.set_xlabel("N_FIM"); ax_cv.set_ylabel("CV = std/mean")
    ax_cv.legend(); ax_cv.grid(alpha=0.3)
    ax_cv.set_xscale("log")

    plt.tight_layout()
    fig.savefig(OUT / "fim_stability_results.png", dpi=150, bbox_inches="tight")
    print(f"\nSaved: {OUT / 'fim_stability_results.png'}")
    plt.show()


if __name__ == "__main__":
    run()
