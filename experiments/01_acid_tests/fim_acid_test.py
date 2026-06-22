"""
CEI v2 — Fisher Information Matrix effective rank.

The FIM captures how many independent learning directions the network has.

  F = (1/N) sum_i  grad_i  grad_i^T       (empirical Fisher)

  FIM_erank = erank(F)

Via the dual: erank(G G^T) == erank(G^T G) for shared nonzero spectrum,
so we compute the N×N matrix G G^T (N=n_eval << d=18752 params) — cheap.

Hypothesis:
  Noisy labels  → gradients scatter in many independent directions → HIGH FIM_erank
  Clean labels  → gradients point in coherent directions → LOW FIM_erank
  rho(FIM_erank, test_acc) should be NEGATIVE

Acid test design: n_train=400, epochs=200, vary noise only.
Also run n_train probe: n_train varies, noise=0.

If direction is CONSISTENT across both experiments → metric is real.
If direction FLIPS (like GC) → metric is still confounded.

Output: fim_acid_results.png + fim_summary.txt
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

SEED    = 42
OUT     = Path(__file__).parent
N_FIM   = 100    # number of per-sample gradients for FIM estimate
BATCH   = 64
EPOCHS  = 200


# ------------------------------------------------------------------ #
#  MLP                                                                 #
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

    def _grad_single(self, x, y):
        """Gradient vector for a single sample. Returns flat numpy array."""
        X = x[np.newaxis, :]
        n = 1
        p, cache, pre = self._fwd(X)
        dh = p.copy(); dh[0, y] -= 1     # shape (1, K)
        grads = []
        for i in reversed(range(len(self.W))):
            dW = cache[i].T @ dh + self.l2 * self.W[i]
            grads.append(dW.ravel())
            if i > 0:
                dh = (dh @ self.W[i].T) * (1 - np.tanh(pre[i-1])**2)
        return np.concatenate(grads[::-1])   # same layer order as self.W

    def fim_erank(self, X_pool, y_pool, n_samples=N_FIM):
        """
        Empirical Fisher erank via dual N×N Gram matrix.
        G[i] = gradient vector for sample i  (shape: d)
        F_dual = G @ G.T / N   shape: N×N
        erank(F_dual) == erank(F_full) for non-zero eigenvalues.
        """
        n  = len(X_pool)
        idx = np.random.choice(n, min(n_samples, n), replace=False)
        G   = np.array([self._grad_single(X_pool[k], y_pool[k]) for k in idx])
        # G shape: (n_samples, d)
        F_dual = (G @ G.T) / len(idx)          # (n_samples, n_samples)
        return effective_rank(F_dual)

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


# ------------------------------------------------------------------ #
#  Train + measure                                                     #
# ------------------------------------------------------------------ #

def run_cond(X_tr, y_tr, X_te, y_te, l2=0.0, epochs=EPOCHS, lr=0.005,
             measure_every=20):
    model = MLP(l2=l2)
    n     = len(X_tr)
    log   = []
    for ep in range(epochs):
        idx = np.random.permutation(n)
        for s in range(0, n, BATCH):
            b = idx[s:s+BATCH]
            model.step(X_tr[b], y_tr[b], lr)

        if ep % measure_every == 0 or ep == epochs - 1:
            tr_acc = model.acc(X_tr, y_tr)
            te_acc = model.acc(X_te, y_te)
            fre    = model.fim_erank(X_tr, y_tr)    # on training set
            log.append({"ep": ep, "tr": round(tr_acc,4),
                        "te": round(te_acc,4), "fim_er": round(fre, 4)})
    return model, log


# ------------------------------------------------------------------ #
#  Experiment A: noise acid test (fixed n=400, vary noise)            #
# ------------------------------------------------------------------ #

def noise_experiment(X_pool, y_pool, X_eval, y_eval):
    NOISE  = [0.0, 0.15, 0.30, 0.50]
    SEEDS  = [42, 7, 123]
    results = {}

    print("\n=== EXPERIMENT A: noise acid test (n=400, ep=200) ===")
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
            _, log = run_cond(X_tr, y_noisy, X_eval, y_eval)
            results[(noise, seed)] = log
            r = log[-1]
            print(f"  noise={noise:.0%} s={seed}: "
                  f"tr={r['tr']:.3f} te={r['te']:.3f} FIM_er={r['fim_er']:.2f}")
    return results, NOISE, SEEDS


# ------------------------------------------------------------------ #
#  Experiment B: n_train probe (noise=0, vary n)                      #
# ------------------------------------------------------------------ #

def ntrain_experiment(X_pool, y_pool, X_eval, y_eval):
    NTRAINS = [40, 200, 400, 800]
    SEEDS   = [42, 7, 123]
    results = {}

    print("\n=== EXPERIMENT B: n_train probe (noise=0) ===")
    for n in NTRAINS:
        for seed in SEEDS:
            np.random.seed(seed)
            X_tr, _, y_tr, _ = train_test_split(
                X_pool, y_pool, train_size=n, random_state=seed)
            _, log = run_cond(X_tr, y_tr, X_eval, y_eval)
            results[(n, seed)] = log
            r = log[-1]
            print(f"  n={n:4d} s={seed}: "
                  f"tr={r['tr']:.3f} te={r['te']:.3f} FIM_er={r['fim_er']:.2f}")
    return results, NTRAINS, SEEDS


# ------------------------------------------------------------------ #
#  Main                                                                #
# ------------------------------------------------------------------ #

def run():
    X, y = load_digits(return_X_y=True)
    X    = StandardScaler().fit_transform(X)
    X_eval, X_pool, y_eval, y_pool = train_test_split(
        X, y, test_size=len(X)-200, random_state=SEED)

    res_noise, NOISE, SEEDS_N = noise_experiment(X_pool, y_pool, X_eval, y_eval)
    res_ntrain, NTRAINS, SEEDS_T = ntrain_experiment(X_pool, y_pool, X_eval, y_eval)

    # ---- pool final values ----
    def pool_final(results):
        frs, tes = [], []
        for log in results.values():
            r = log[-1]; frs.append(r["fim_er"]); tes.append(r["te"])
        return frs, tes

    noise_frs, noise_tes = pool_final(res_noise)
    train_frs, train_tes = pool_final(res_ntrain)

    rho_n, p_n = spearmanr(noise_frs, noise_tes)
    rho_t, p_t = spearmanr(train_frs, train_tes)

    # ---- per-condition means ----
    def means_by_key(results, keys, seeds):
        out = {}
        for k in keys:
            frs = [results[(k,s)][-1]["fim_er"] for s in seeds]
            tes = [results[(k,s)][-1]["te"]     for s in seeds]
            out[k] = (np.mean(frs), np.std(frs), np.mean(tes), np.std(tes))
        return out

    noise_means  = means_by_key(res_noise,  NOISE,   SEEDS_N)
    ntrain_means = means_by_key(res_ntrain, NTRAINS, SEEDS_T)

    # ---- plot ----
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("FIM Effective Rank — Dual Acid Test\n"
                 "Left: noise probe (n=400 fixed) | Right: n_train probe (noise=0 fixed)",
                 fontweight="bold")

    C_NOISE  = {0.0:"#2ecc71", 0.15:"#3498db", 0.30:"#e67e22", 0.50:"#e74c3c"}
    C_NTRAIN = {40:"#e74c3c", 200:"#e67e22", 400:"#3498db", 800:"#2ecc71"}

    # top-left: FIM erank over training (noise probe)
    ax = axes[0,0]
    for noise in NOISE:
        for i, seed in enumerate(SEEDS_N):
            log = res_noise[(noise,seed)]
            ax.plot([r["ep"] for r in log], [r["fim_er"] for r in log],
                    color=C_NOISE[noise], alpha=0.4 if i>0 else 0.9,
                    linewidth=1.4 if i>0 else 2.2,
                    label=f"noise={noise:.0%}" if i==0 else None)
    ax.set_title(f"Noise probe — FIM erank\nrho={rho_n:.3f} p={p_n:.2e}")
    ax.set_xlabel("Epoch"); ax.set_ylabel("FIM erank"); ax.legend(fontsize=8); ax.grid(alpha=0.3)

    # top-right: FIM erank over training (n_train probe)
    ax = axes[0,1]
    for n in NTRAINS:
        for i, seed in enumerate(SEEDS_T):
            log = res_ntrain[(n,seed)]
            ax.plot([r["ep"] for r in log], [r["fim_er"] for r in log],
                    color=C_NTRAIN[n], alpha=0.4 if i>0 else 0.9,
                    linewidth=1.4 if i>0 else 2.2,
                    label=f"n={n}" if i==0 else None)
    ax.set_title(f"n_train probe — FIM erank\nrho={rho_t:.3f} p={p_t:.2e}")
    ax.set_xlabel("Epoch"); ax.set_ylabel("FIM erank"); ax.legend(fontsize=8); ax.grid(alpha=0.3)

    # bottom-left: scatter noise
    ax = axes[1,0]
    for noise in NOISE:
        frs = [res_noise[(noise,s)][-1]["fim_er"] for s in SEEDS_N]
        tes = [res_noise[(noise,s)][-1]["te"]     for s in SEEDS_N]
        ax.scatter(frs, tes, color=C_NOISE[noise], s=70, zorder=3,
                   label=f"noise={noise:.0%}", edgecolors="white", linewidths=0.4)
        ax.errorbar(np.mean(frs), np.mean(tes), xerr=np.std(frs), yerr=np.std(tes),
                    color=C_NOISE[noise], alpha=0.5, capsize=3)
    ax.set_title(f"Noise probe: FIM_er vs test_acc\nrho={rho_n:.3f} p={p_n:.2e}")
    ax.set_xlabel("FIM erank"); ax.set_ylabel("Test Accuracy"); ax.legend(fontsize=8); ax.grid(alpha=0.3)

    # bottom-right: scatter n_train
    ax = axes[1,1]
    for n in NTRAINS:
        frs = [res_ntrain[(n,s)][-1]["fim_er"] for s in SEEDS_T]
        tes = [res_ntrain[(n,s)][-1]["te"]     for s in SEEDS_T]
        ax.scatter(frs, tes, color=C_NTRAIN[n], s=70, zorder=3,
                   label=f"n={n}", edgecolors="white", linewidths=0.4)
        ax.errorbar(np.mean(frs), np.mean(tes), xerr=np.std(frs), yerr=np.std(tes),
                    color=C_NTRAIN[n], alpha=0.5, capsize=3)
    ax.set_title(f"n_train probe: FIM_er vs test_acc\nrho={rho_t:.3f} p={p_t:.2e}")
    ax.set_xlabel("FIM erank"); ax.set_ylabel("Test Accuracy"); ax.legend(fontsize=8); ax.grid(alpha=0.3)

    plt.tight_layout()
    fig.savefig(OUT / "fim_acid_results.png", dpi=150, bbox_inches="tight")
    print(f"\nSaved: {OUT / 'fim_acid_results.png'}")

    # ---- terminal summary ----
    print("\n====== FIM ERANK RESULTS ======")
    print(f"\n[Noise acid test — n=400 fixed]")
    print(f"  {'noise':>6}  {'FIM_er':>8}  {'±':>6}  {'te':>7}  {'±':>6}")
    for noise in NOISE:
        m = noise_means[noise]
        print(f"  {noise:>5.0%}  {m[0]:>8.2f}  {m[1]:>6.2f}  {m[2]:>7.3f}  {m[3]:>6.3f}")
    print(f"  rho(FIM_er, test_acc) = {rho_n:.3f}  p={p_n:.2e}")

    print(f"\n[n_train probe — noise=0 fixed]")
    print(f"  {'n_tr':>6}  {'FIM_er':>8}  {'±':>6}  {'te':>7}  {'±':>6}")
    for n in NTRAINS:
        m = ntrain_means[n]
        print(f"  {n:>6d}  {m[0]:>8.2f}  {m[1]:>6.2f}  {m[2]:>7.3f}  {m[3]:>6.3f}")
    print(f"  rho(FIM_er, test_acc) = {rho_t:.3f}  p={p_t:.2e}")

    print(f"\n====== CONSISTENCY CHECK ======")
    same_dir = (rho_n < 0) == (rho_t < 0)
    both_sig = p_n < 0.05 and p_t < 0.05
    print(f"  Direction consistent across experiments: {same_dir}")
    print(f"  Both significant (p<0.05):               {both_sig}")
    if same_dir and both_sig:
        dir_str = "LOWER FIM_er = better" if rho_n < 0 else "HIGHER FIM_er = better"
        print(f"  => METRIC PASSES DUAL ACID TEST")
        print(f"  => {dir_str}")
    elif same_dir:
        print(f"  => Direction consistent but one p-value marginal — weak evidence")
    else:
        print(f"  => Direction INCONSISTENT — FIM_er is still confounded")

    with open(OUT / "fim_summary.txt", "w") as f:
        f.write("FIM EFFECTIVE RANK — DUAL ACID TEST\n")
        f.write("=====================================\n\n")
        f.write(f"Noise probe rho={rho_n:.3f}  p={p_n:.2e}\n")
        f.write(f"n_train probe rho={rho_t:.3f}  p={p_t:.2e}\n")
        f.write(f"Direction consistent: {same_dir}\n")
        f.write(f"Both significant:     {both_sig}\n")
    print(f"Saved: {OUT / 'fim_summary.txt'}")

    plt.show()


if __name__ == "__main__":
    run()
