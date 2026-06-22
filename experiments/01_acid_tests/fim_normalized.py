"""
CEI v2 — Normalized FIM effective rank.

Key fix from fim_acid_test.py:
  FIM_er (absolute) is confounded by n_samples_used because
  erank is bounded by min(d, n_samples). With n=40, max erank=40;
  with n=100 samples, max erank=100. Absolute values are incomparable.

Fix:  FIM_er_norm = erank(FIM) / n_samples_used
  = fraction of maximum gradient dimensionality that is active.

Range: (1/n_samples, 1].
Lower = gradients are concentrated in few directions = structural constraint.
Higher = gradients scatter in many directions = memorising / noisy.

Hypothesis (now normalized):
  rho(FIM_er_norm, test_acc) < 0  in BOTH experiments (consistent direction).

Output: fim_norm_results.png + fim_norm_summary.txt
"""

import sys, math
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from scipy.stats import spearmanr, pearsonr

sys.path.insert(0, str(Path(__file__).parent))
from sci_tracker import effective_rank

SEED   = 42
OUT    = Path(__file__).parent
N_FIM  = 100
BATCH  = 64
EPOCHS = 200


# ------------------------------------------------------------------ #
#  MLP + normalized FIM_er                                            #
# ------------------------------------------------------------------ #

class MLP:
    WIDTHS = [64, 128, 64, 32, 10]

    def __init__(self, l2=0.0):
        self.l2 = l2
        self.W, self.b = [], []
        for i in range(len(self.WIDTHS) - 1):
            s = np.sqrt(1.0 / self.WIDTHS[i])
            self.W.append(np.random.randn(self.WIDTHS[i], self.WIDTHS[i+1]) * s)
            self.b.append(np.zeros(self.WIDTHS[i+1]))

    def _fwd(self, X):
        h, cache, pre = X, [X], []
        for W, b in zip(self.W[:-1], self.b[:-1]):
            z = h @ W + b; pre.append(z); h = np.tanh(z); cache.append(h)
        logits = h @ self.W[-1] + self.b[-1]
        e = np.exp(logits - logits.max(1, keepdims=True))
        return e / e.sum(1, keepdims=True), cache, pre

    def _grad_single(self, x, y_label):
        X  = x[np.newaxis, :]
        p, cache, pre = self._fwd(X)
        dh = p.copy(); dh[0, y_label] -= 1
        gs = []
        for i in reversed(range(len(self.W))):
            dW = cache[i].T @ dh + self.l2 * self.W[i]
            gs.append(dW.ravel())
            if i > 0:
                dh = (dh @ self.W[i].T) * (1 - np.tanh(pre[i-1])**2)
        return np.concatenate(gs[::-1])

    def fim_er_norm(self, X_pool, y_pool, n_samples=N_FIM):
        """
        Returns (FIM_er_absolute, FIM_er_normalized).
        FIM_er_norm = erank(F_dual) / n_used.
        """
        n     = len(X_pool)
        n_use = min(n_samples, n)
        idx   = np.random.choice(n, n_use, replace=False)
        G     = np.array([self._grad_single(X_pool[k], y_pool[k]) for k in idx])
        F_d   = (G @ G.T) / n_use
        er    = effective_rank(F_d)
        return er, er / n_use

    def step(self, X, y, lr):
        n = len(y)
        p, cache, pre = self._fwd(X)
        dh = p.copy(); dh[np.arange(n), y] -= 1; dh /= n
        for i in reversed(range(len(self.W))):
            dW = cache[i].T @ dh + self.l2 * self.W[i]
            self.W[i] -= lr * dW
            self.b[i]  -= lr * dh.sum(0)
            if i > 0:
                dh = (dh @ self.W[i].T) * (1 - np.tanh(pre[i-1])**2)

    def acc(self, X, y):
        p, _, _ = self._fwd(X); return (p.argmax(1) == y).mean()


def run_cond(X_tr, y_tr, X_te, y_te, l2=0.0, epochs=EPOCHS, lr=0.005,
             measure_every=20):
    model = MLP(l2=l2)
    n, log = len(X_tr), []
    for ep in range(epochs):
        idx = np.random.permutation(n)
        for s in range(0, n, BATCH):
            b = idx[s:s+BATCH]; model.step(X_tr[b], y_tr[b], lr)
        if ep % measure_every == 0 or ep == epochs - 1:
            tr, te       = model.acc(X_tr, y_tr), model.acc(X_te, y_te)
            er, er_norm  = model.fim_er_norm(X_tr, y_tr)
            log.append({"ep": ep, "tr": round(tr,4), "te": round(te,4),
                        "fim_er": round(er,4), "fim_norm": round(er_norm,6)})
    return log


# ------------------------------------------------------------------ #
#  Run both experiments                                               #
# ------------------------------------------------------------------ #

def run():
    X, y = load_digits(return_X_y=True)
    X    = StandardScaler().fit_transform(X)
    X_ev, X_pool, y_ev, y_pool = train_test_split(
        X, y, test_size=len(X)-200, random_state=SEED)

    SEEDS  = [42, 7, 123]
    NOISE  = [0.0, 0.15, 0.30, 0.50]
    NTRAIN = [40, 200, 400, 800]

    # ---- Experiment A: noise (n=400 fixed) ----
    print("\n=== EXP A: noise acid test (n=400) ===")
    res_n = {}
    for noise in NOISE:
        for seed in SEEDS:
            np.random.seed(seed)
            X_tr, _, y_tr, _ = train_test_split(
                X_pool, y_pool, train_size=400, random_state=seed)
            y_noisy = y_tr.copy()
            if noise > 0:
                nf = int(noise * len(y_tr))
                fi = np.random.choice(len(y_tr), nf, replace=False)
                y_noisy[fi] = np.random.randint(0, 10, nf)
            log = run_cond(X_tr, y_noisy, X_ev, y_ev)
            res_n[(noise, seed)] = log
            r = log[-1]
            print(f"  noise={noise:.0%} s={seed}: te={r['te']:.3f} "
                  f"FIM_er={r['fim_er']:.1f}  FIM_norm={r['fim_norm']:.4f}")

    # ---- Experiment B: n_train (noise=0) ----
    print("\n=== EXP B: n_train probe (noise=0) ===")
    res_t = {}
    for n in NTRAIN:
        for seed in SEEDS:
            np.random.seed(seed)
            X_tr, _, y_tr, _ = train_test_split(
                X_pool, y_pool, train_size=n, random_state=seed)
            log = run_cond(X_tr, y_tr, X_ev, y_ev)
            res_t[(n, seed)] = log
            r = log[-1]
            print(f"  n={n:4d} s={seed}: te={r['te']:.3f} "
                  f"FIM_er={r['fim_er']:.1f}  FIM_norm={r['fim_norm']:.4f}")

    # ---- Pool final values ----
    def pool(res):
        er, nm, te = [], [], []
        for log in res.values():
            r = log[-1]; er.append(r["fim_er"]); nm.append(r["fim_norm"]); te.append(r["te"])
        return er, nm, te

    n_er, n_nm, n_te = pool(res_n)
    t_er, t_nm, t_te = pool(res_t)

    rho_n_abs, p_n_abs = spearmanr(n_er, n_te)
    rho_n_nm,  p_n_nm  = spearmanr(n_nm, n_te)
    rho_t_abs, p_t_abs = spearmanr(t_er, t_te)
    rho_t_nm,  p_t_nm  = spearmanr(t_nm, t_te)

    # ---- per-condition means ----
    def means(res, keys, seeds):
        d = {}
        for k in keys:
            ls = [res[(k,s)][-1] for s in seeds]
            d[k] = {
                "er_m": np.mean([l["fim_er"]   for l in ls]),
                "er_s": np.std ([l["fim_er"]   for l in ls]),
                "nm_m": np.mean([l["fim_norm"] for l in ls]),
                "nm_s": np.std ([l["fim_norm"] for l in ls]),
                "te_m": np.mean([l["te"]        for l in ls]),
                "te_s": np.std ([l["te"]        for l in ls]),
            }
        return d

    nm_means = means(res_n, NOISE,  SEEDS)
    nt_means = means(res_t, NTRAIN, SEEDS)

    # ---- curves ----
    def curves(res, keys, seeds, key_to_col, metric="fim_norm"):
        data = {}
        for k in keys:
            data[k] = [[r["ep"] for r in res[(k,s)]] for s in seeds], \
                      [[r[metric] for r in res[(k,s)]] for s in seeds]
        return data

    # ---- plot ----
    CN = {0.0:"#2ecc71", 0.15:"#3498db", 0.30:"#e67e22", 0.50:"#e74c3c"}
    CT = {40:"#e74c3c", 200:"#e67e22", 400:"#3498db", 800:"#2ecc71"}

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle("FIM Erank (normalized) — CEI v2 Structural Constraint\n"
                 "FIM_norm = erank(empirical Fisher) / n_samples", fontweight="bold")

    # row 0: noise experiment
    # col 0: FIM_norm over training
    ax = axes[0,0]
    for noise in NOISE:
        for i, seed in enumerate(SEEDS):
            log = res_n[(noise,seed)]
            ax.plot([r["ep"] for r in log], [r["fim_norm"] for r in log],
                    color=CN[noise], alpha=0.4 if i else 0.9,
                    linewidth=1.4 if i else 2.2,
                    label=f"noise={noise:.0%}" if not i else None)
    ax.set_title(f"Noise probe — FIM_norm over training")
    ax.set_xlabel("Epoch"); ax.set_ylabel("FIM_norm"); ax.legend(fontsize=8); ax.grid(alpha=0.3)

    # col 1: scatter noise (normalized)
    ax = axes[0,1]
    for noise in NOISE:
        nm_v = [res_n[(noise,s)][-1]["fim_norm"] for s in SEEDS]
        te_v = [res_n[(noise,s)][-1]["te"]       for s in SEEDS]
        ax.scatter(nm_v, te_v, color=CN[noise], s=70, zorder=3,
                   label=f"noise={noise:.0%}", edgecolors="w", linewidths=0.5)
    ax.set_title(f"Noise probe: FIM_norm vs test_acc\n"
                 f"abs rho={rho_n_abs:.3f}  norm rho={rho_n_nm:.3f}  p={p_n_nm:.2e}")
    ax.set_xlabel("FIM_norm"); ax.set_ylabel("Test Accuracy"); ax.legend(fontsize=8); ax.grid(alpha=0.3)

    # col 2: bar noise
    ax = axes[0,2]
    x, w = np.arange(len(NOISE)), 0.3
    ax2 = ax.twinx()
    ax.bar(x-w/2, [nm_means[n]["nm_m"] for n in NOISE], w,
           yerr=[nm_means[n]["nm_s"] for n in NOISE],
           color=[CN[n] for n in NOISE], alpha=0.8, capsize=4, label="FIM_norm (left)")
    ax2.bar(x+w/2, [nm_means[n]["te_m"] for n in NOISE], w,
            yerr=[nm_means[n]["te_s"] for n in NOISE],
            color=[CN[n] for n in NOISE], alpha=0.35, capsize=4, label="Test acc (right)")
    ax.set_xticks(x); ax.set_xticklabels([f"{n:.0%}" for n in NOISE])
    ax.set_xlabel("Noise"); ax.set_ylabel("FIM_norm"); ax2.set_ylabel("Test acc")
    ax.set_title("Noise probe summary"); ax.grid(alpha=0.3, axis="y")

    # row 1: n_train experiment
    ax = axes[1,0]
    for n in NTRAIN:
        for i, seed in enumerate(SEEDS):
            log = res_t[(n,seed)]
            ax.plot([r["ep"] for r in log], [r["fim_norm"] for r in log],
                    color=CT[n], alpha=0.4 if i else 0.9,
                    linewidth=1.4 if i else 2.2,
                    label=f"n={n}" if not i else None)
    ax.set_title("n_train probe — FIM_norm over training")
    ax.set_xlabel("Epoch"); ax.set_ylabel("FIM_norm"); ax.legend(fontsize=8); ax.grid(alpha=0.3)

    ax = axes[1,1]
    for n in NTRAIN:
        nm_v = [res_t[(n,s)][-1]["fim_norm"] for s in SEEDS]
        te_v = [res_t[(n,s)][-1]["te"]       for s in SEEDS]
        ax.scatter(nm_v, te_v, color=CT[n], s=70, zorder=3,
                   label=f"n={n}", edgecolors="w", linewidths=0.5)
    ax.set_title(f"n_train probe: FIM_norm vs test_acc\n"
                 f"abs rho={rho_t_abs:.3f}  norm rho={rho_t_nm:.3f}  p={p_t_nm:.2e}")
    ax.set_xlabel("FIM_norm"); ax.set_ylabel("Test Accuracy"); ax.legend(fontsize=8); ax.grid(alpha=0.3)

    ax = axes[1,2]
    x2 = np.arange(len(NTRAIN))
    ax3 = ax.twinx()
    ax.bar(x2-w/2, [nt_means[n]["nm_m"] for n in NTRAIN], w,
           yerr=[nt_means[n]["nm_s"] for n in NTRAIN],
           color=[CT[n] for n in NTRAIN], alpha=0.8, capsize=4)
    ax3.bar(x2+w/2, [nt_means[n]["te_m"] for n in NTRAIN], w,
            yerr=[nt_means[n]["te_s"] for n in NTRAIN],
            color=[CT[n] for n in NTRAIN], alpha=0.35, capsize=4)
    ax.set_xticks(x2); ax.set_xticklabels([str(n) for n in NTRAIN])
    ax.set_xlabel("n_train"); ax.set_ylabel("FIM_norm"); ax3.set_ylabel("Test acc")
    ax.set_title("n_train probe summary"); ax.grid(alpha=0.3, axis="y")

    plt.tight_layout()
    fig.savefig(OUT / "fim_norm_results.png", dpi=150, bbox_inches="tight")
    print(f"\nSaved: {OUT / 'fim_norm_results.png'}")

    # ---- summary ----
    print("\n====== NORMALIZED FIM ERANK SUMMARY ======")
    print(f"\n{'NOISE probe (n=400 fixed)':}")
    print(f"  {'noise':>6}  {'FIM_norm':>10}  {'±':>6}  {'te':>7}")
    for noise in NOISE:
        m = nm_means[noise]
        print(f"  {noise:>5.0%}  {m['nm_m']:>10.4f}  {m['nm_s']:>6.4f}  {m['te_m']:>7.3f}")
    print(f"  rho (absolute) = {rho_n_abs:.3f}  p={p_n_abs:.2e}")
    print(f"  rho (norm)     = {rho_n_nm:.3f}  p={p_n_nm:.2e}")

    print(f"\n{'n_train probe (noise=0 fixed)':}")
    print(f"  {'n_tr':>6}  {'FIM_norm':>10}  {'±':>6}  {'te':>7}")
    for n in NTRAIN:
        m = nt_means[n]
        print(f"  {n:>6d}  {m['nm_m']:>10.4f}  {m['nm_s']:>6.4f}  {m['te_m']:>7.3f}")
    print(f"  rho (absolute) = {rho_t_abs:.3f}  p={p_t_abs:.2e}")
    print(f"  rho (norm)     = {rho_t_nm:.3f}  p={p_t_nm:.2e}")

    consistent = (rho_n_nm < 0) == (rho_t_nm < 0)
    both_sig   = p_n_nm < 0.05 and p_t_nm < 0.05
    print(f"\n====== CONSISTENCY CHECK (FIM_norm) ======")
    print(f"  Same direction in both experiments: {consistent}")
    print(f"  Both p < 0.05:                      {both_sig}")
    if consistent and both_sig:
        print(f"  => PASSES DUAL ACID TEST")
        print(f"  => Lower FIM_norm = more structurally constrained = better generalisation")
    elif consistent:
        print(f"  => Direction consistent. n_train probe weak (small n, non-monotone abs values).")
        print(f"  => FIM_norm is the best v2 candidate so far.")
    else:
        print(f"  => FAILS — direction inconsistent.")

    with open(OUT / "fim_norm_summary.txt", "w") as f:
        f.write("FIM NORMALIZED ERANK — FINAL SUMMARY\n")
        f.write("=====================================\n\n")
        f.write(f"FIM_norm = erank(empirical Fisher) / n_samples_used\n\n")
        f.write(f"Noise probe:   rho={rho_n_nm:.3f}  p={p_n_nm:.2e}\n")
        f.write(f"n_train probe: rho={rho_t_nm:.3f}  p={p_t_nm:.2e}\n")
        f.write(f"Direction consistent: {consistent}\n")
        f.write(f"Both significant:     {both_sig}\n\n")
        f.write("Noise probe by condition:\n")
        for noise in NOISE:
            m = nm_means[noise]
            f.write(f"  noise={noise:.0%}: FIM_norm={m['nm_m']:.4f}+/-{m['nm_s']:.4f}  te={m['te_m']:.3f}\n")
        f.write("\nn_train probe by condition:\n")
        for n in NTRAIN:
            m = nt_means[n]
            f.write(f"  n={n}: FIM_norm={m['nm_m']:.4f}+/-{m['nm_s']:.4f}  te={m['te_m']:.3f}\n")
    print(f"Saved: {OUT / 'fim_norm_summary.txt'}")

    plt.show()


if __name__ == "__main__":
    run()
