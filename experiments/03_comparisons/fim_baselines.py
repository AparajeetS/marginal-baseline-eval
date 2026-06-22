"""
CEI v2 — Baselines comparison.

Justifies the choice of erank over other FIM-derived quantities.

Metrics compared on the dual acid test (all computed from same per-sample
gradients so comparison is fair):

  FIM_norm      = erank(F_dual) / N          [our metric]
  trace_norm    = trace(F_emp) / N            = mean squared gradient norm
  stable_rank   = trace(F_emp) / spectral(F_emp) = sum(sigma^2) / sigma_max^2
  spectral_norm = sigma_max(F_dual)           = largest gradient outer product
  grad_norm     = mean ||g_i||_2              = gradient magnitude
  weight_norm   = mean_l ||W_l||_F            = weight magnitude

All six computed simultaneously from the same model state.
Spearman rho with test_acc reported for both acid test experiments.
"""

import sys, math
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).parent))
from sci_tracker import effective_rank
from fim_full_study import MLP

SEED   = 42
OUT    = Path(__file__).parent
N_FIM  = 100
BATCH  = 64
EPOCHS = 200


# ------------------------------------------------------------------ #
#  All metrics from same gradient sample                              #
# ------------------------------------------------------------------ #

def all_metrics(model, X_pool, y_pool, n_samples=N_FIM):
    n     = len(X_pool)
    n_use = min(n_samples, n)
    idx   = np.random.choice(n, n_use, replace=False)
    G     = np.array([model._grad_single(X_pool[k], y_pool[k]) for k in idx])
    # G: (n_use, d)

    F_d   = (G @ G.T) / n_use          # dual Gram: (n_use, n_use)
    sv    = np.linalg.svd(F_d, compute_uv=False)
    sv    = sv[sv > 1e-10]

    # effective rank
    p     = sv / sv.sum()
    H     = -(p * np.log(p + 1e-12)).sum()
    er    = float(math.exp(H))
    fim_norm    = er / n_use

    # trace = sum of eigenvalues = sum of squared gradient norms / n_use
    trace_norm  = float(sv.sum()) / n_use

    # stable rank = trace / spectral_norm
    spectral    = float(sv[0]) if len(sv) > 0 else 1e-12
    stable_rank = float(sv.sum()) / spectral    # un-normalized

    # normalized stable rank (/ n_use so comparable to fim_norm)
    stable_rank_norm = stable_rank / n_use

    # spectral norm (max eigenvalue of F_dual)
    spectral_norm = spectral / n_use

    # gradient magnitude
    grad_norms = np.linalg.norm(G, axis=1)
    grad_norm  = float(grad_norms.mean())

    # weight norm
    weight_norm = float(np.mean([np.linalg.norm(W) for W in model.W]))

    return {
        "fim_norm":       fim_norm,
        "trace_norm":     trace_norm,
        "stable_rank_n":  stable_rank_norm,
        "spectral_n":     spectral_norm,
        "grad_norm":      grad_norm,
        "weight_norm":    weight_norm,
    }


# ------------------------------------------------------------------ #
#  Training                                                            #
# ------------------------------------------------------------------ #

def run_cond(X_tr, y_tr, X_te, y_te, l2=0.0, epochs=EPOCHS):
    model = MLP(l2=l2)
    n     = len(X_tr)
    for _ in range(epochs):
        idx = np.random.permutation(n)
        for s in range(0, n, BATCH):
            b = idx[s:s+BATCH]; model.step(X_tr[b], y_tr[b], 0.005)
    te_acc   = model.acc(X_te, y_te)
    metrics  = all_metrics(model, X_tr, y_tr)
    return te_acc, metrics


# ------------------------------------------------------------------ #
#  Main                                                                #
# ------------------------------------------------------------------ #

def run():
    X, y = load_digits(return_X_y=True)
    X    = StandardScaler().fit_transform(X)
    X_ev, X_pool, y_ev, y_pool = train_test_split(
        X, y, test_size=len(X)-200, random_state=SEED)

    SEEDS  = [42, 7, 123]
    NOISE  = [0.0, 0.15, 0.30, 0.50]
    NTRAIN = [40, 200, 400, 800]
    METRIC_KEYS = ["fim_norm","trace_norm","stable_rank_n",
                   "spectral_n","grad_norm","weight_norm"]

    def run_exp(vary_key, vary_vals, fixed_noise=0.0, fixed_n=400):
        te_all = {k: [] for k in METRIC_KEYS}
        te_vals = []
        for val in vary_vals:
            for seed in SEEDS:
                np.random.seed(seed)
                n_use = val if vary_key == "n" else fixed_n
                X_tr, _, y_tr, _ = train_test_split(
                    X_pool, y_pool, train_size=n_use, random_state=seed)
                y_use = y_tr.copy()
                noise = val if vary_key == "noise" else fixed_noise
                if noise > 0:
                    nf = int(noise * len(y_tr))
                    fi = np.random.choice(len(y_tr), nf, replace=False)
                    y_use[fi] = np.random.randint(0, 10, nf)
                te, m = run_cond(X_tr, y_use, X_ev, y_ev)
                te_vals.append(te)
                for k in METRIC_KEYS:
                    te_all[k].append(m[k])
        return te_vals, te_all

    print("Running noise experiment...")
    te_n, m_n = run_exp("noise", NOISE)
    print("Running n_train experiment...")
    te_t, m_t = run_exp("n", NTRAIN)

    # Spearman rho for each metric
    print("\n====== BASELINES COMPARISON ======")
    results = {}
    for key in METRIC_KEYS:
        rho_n, p_n = spearmanr(m_n[key], te_n)
        rho_t, p_t = spearmanr(m_t[key], te_t)
        consistent = (rho_n < 0) == (rho_t < 0)
        both_sig   = p_n < 0.05 and p_t < 0.05
        results[key] = (rho_n, p_n, rho_t, p_t, consistent, both_sig)
        flag = "PASS" if (consistent and both_sig) else ("DIR" if consistent else "FAIL")
        print(f"  {key:<18} noise_rho={rho_n:+.3f}(p={p_n:.2e})  "
              f"ntrain_rho={rho_t:+.3f}(p={p_t:.2e})  [{flag}]")

    # ---- plot ----
    fig, axes = plt.subplots(2, len(METRIC_KEYS), figsize=(20, 8))
    fig.suptitle("All FIM-derived Metrics vs Test Accuracy\n"
                 "Top: noise probe | Bottom: n_train probe", fontweight="bold")

    for col, key in enumerate(METRIC_KEYS):
        rho_n, p_n, rho_t, p_t, consistent, both_sig = results[key]
        for row, (m_vals, te_vals, label) in enumerate([
            (m_n[key], te_n, f"Noise\nrho={rho_n:+.3f}"),
            (m_t[key], te_t, f"n_train\nrho={rho_t:+.3f}"),
        ]):
            ax = axes[row, col]
            color = "#2ecc71" if (consistent and both_sig) else (
                    "#3498db" if consistent else "#e74c3c")
            ax.scatter(m_vals, te_vals, alpha=0.6, s=25, color=color)
            ax.set_title(f"{key}\n{label}", fontsize=8)
            ax.set_xlabel(key, fontsize=7)
            if col == 0: ax.set_ylabel("Test Acc", fontsize=8)
            ax.grid(alpha=0.3)
            # border color
            for spine in ax.spines.values():
                spine.set_edgecolor(color)
                spine.set_linewidth(2)

    plt.tight_layout()
    fig.savefig(OUT / "fim_baselines_results.png", dpi=150, bbox_inches="tight")
    print(f"\nSaved: {OUT / 'fim_baselines_results.png'}")

    # ---- summary table ----
    print("\n  Summary table for paper:")
    print(f"  {'Metric':<20} {'noise rho':>10} {'n_train rho':>12} {'Consistent':>11} {'Both sig':>9}")
    print("  " + "-"*65)
    for key in METRIC_KEYS:
        rho_n, p_n, rho_t, p_t, c, s = results[key]
        print(f"  {key:<20} {rho_n:>+10.3f} {rho_t:>+12.3f} "
              f"{'YES' if c else 'NO':>11} {'YES' if s else 'NO':>9}")

    with open(OUT / "fim_baselines_summary.txt", "w") as f:
        f.write("BASELINES COMPARISON\n")
        f.write(f"{'Metric':<20} {'noise_rho':>10} {'ntrain_rho':>11} "
                f"{'Consistent':>11} {'Both_sig':>9}\n")
        f.write("-"*65 + "\n")
        for key in METRIC_KEYS:
            rho_n, p_n, rho_t, p_t, c, s = results[key]
            f.write(f"{key:<20} {rho_n:>+10.3f} {rho_t:>+11.3f} "
                    f"{'YES' if c else 'NO':>11} {'YES' if s else 'NO':>9}\n")
    print(f"Saved: {OUT / 'fim_baselines_summary.txt'}")
    plt.show()


if __name__ == "__main__":
    run()
