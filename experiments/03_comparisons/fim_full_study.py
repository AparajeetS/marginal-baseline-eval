"""
CEI v2 — Full study: FIM_norm + SAM sharpness, 6 conditions x 3 seeds.

Questions:
  1. Does FIM_norm@ep20 predict final test_acc? (leading indicator)
  2. Does FIM_norm add info beyond SAM sharpness? (partial R^2 analysis)
  3. How does FIM_norm compare to CEI v1 across conditions?

Conditions (mirrors the original full_study.py for direct comparison):
  A: n=40,  l2=0,     label=overfit_small
  B: n=400, l2=0,     label=standard_noreg
  C: n=400, l2=0.001, label=standard_light
  D: n=400, l2=0.005, label=standard_med
  E: n=400, l2=0,     early_stop=50
  F: n=400, noise=0.3,label=noisy

Seeds: 42, 7, 123

Output: fim_full_results.png + fim_full_table.csv
"""

import sys, math, csv
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).parent))
from sci_tracker import effective_rank

SEED   = 42
OUT    = Path(__file__).parent
N_FIM  = 100
BATCH  = 64


# ------------------------------------------------------------------ #
#  MLP with FIM_norm + SAM sharpness                                  #
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

    def _loss(self, X, y):
        p, _, _ = self._fwd(X)
        return -np.log(p[np.arange(len(y)), y] + 1e-12).mean()

    def _grad_vec(self, X, y):
        """Full gradient as flat vector (for SAM)."""
        n = len(y)
        p, cache, pre = self._fwd(X)
        dh = p.copy(); dh[np.arange(n), y] -= 1; dh /= n
        gs = []
        for i in reversed(range(len(self.W))):
            dW = cache[i].T @ dh + self.l2 * self.W[i]
            gs.append(dW.ravel())
            if i > 0:
                dh = (dh @ self.W[i].T) * (1 - np.tanh(pre[i-1])**2)
        return np.concatenate(gs[::-1])

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

    def fim_norm(self, X_pool, y_pool, n_samples=N_FIM):
        n     = len(X_pool)
        n_use = min(n_samples, n)
        idx   = np.random.choice(n, n_use, replace=False)
        G     = np.array([self._grad_single(X_pool[k], y_pool[k]) for k in idx])
        F_d   = (G @ G.T) / n_use
        return effective_rank(F_d) / n_use

    def sam_sharpness(self, X, y, rho=0.05):
        """SAM 1-step gradient ascent sharpness."""
        g    = self._grad_vec(X, y)
        norm = np.linalg.norm(g)
        if norm < 1e-12:
            return 0.0
        eps  = rho * g / norm
        # perturb weights
        ptr  = 0
        orig = []
        for i in range(len(self.W)):
            sz = self.W[i].size
            orig.append(self.W[i].copy())
            self.W[i] += eps[ptr:ptr+sz].reshape(self.W[i].shape)
            ptr += sz
        loss_pert = self._loss(X, y)
        loss_orig = self._loss(X, y)    # approximate (perturbed weights still in)
        # restore
        for i in range(len(self.W)):
            self.W[i] = orig[i]
        loss_base = self._loss(X, y)
        return float(loss_pert - loss_base)

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
#  Train                                                               #
# ------------------------------------------------------------------ #

def run_cond(X_tr, y_tr, X_te, y_te, l2=0.0,
             epochs=200, lr=0.005, early_stop=None):
    model   = MLP(l2=l2)
    n, log  = len(X_tr), []

    for ep in range(epochs):
        if early_stop and ep >= early_stop:
            break
        idx = np.random.permutation(n)
        for s in range(0, n, BATCH):
            b = idx[s:s+BATCH]; model.step(X_tr[b], y_tr[b], lr)

        if ep % 10 == 0 or ep == epochs - 1:
            tr     = model.acc(X_tr, y_tr)
            te     = model.acc(X_te, y_te)
            fm     = model.fim_norm(X_tr, y_tr)
            sharp  = model.sam_sharpness(X_tr, y_tr)
            log.append({"ep": ep, "tr": round(tr,4), "te": round(te,4),
                        "fim_norm": round(fm,6), "sharpness": round(sharp,6)})
    return model, log


# ------------------------------------------------------------------ #
#  Main                                                                #
# ------------------------------------------------------------------ #

def run():
    X, y = load_digits(return_X_y=True)
    X    = StandardScaler().fit_transform(X)
    X_ev, X_pool, y_ev, y_pool = train_test_split(
        X, y, test_size=len(X)-200, random_state=SEED)

    SEEDS = [42, 7, 123]
    CONDITIONS = {
        "A_n40_noreg":    {"n": 40,  "l2": 0.0,   "noise": 0.0,  "early": None, "label": "n=40 no-reg"},
        "B_n400_noreg":   {"n": 400, "l2": 0.0,   "noise": 0.0,  "early": None, "label": "n=400 no-reg"},
        "C_n400_l2light": {"n": 400, "l2": 0.001, "noise": 0.0,  "early": None, "label": "n=400 l2=0.001"},
        "D_n400_l2med":   {"n": 400, "l2": 0.005, "noise": 0.0,  "early": None, "label": "n=400 l2=0.005"},
        "E_n400_early50": {"n": 400, "l2": 0.0,   "noise": 0.0,  "early": 50,   "label": "n=400 stop@50"},
        "F_n400_noise30": {"n": 400, "l2": 0.0,   "noise": 0.30, "early": None, "label": "n=400 30%noise"},
    }

    all_logs = {}
    for cname, cfg in CONDITIONS.items():
        all_logs[cname] = []
        for seed in SEEDS:
            np.random.seed(seed)
            X_tr, _, y_tr, _ = train_test_split(
                X_pool, y_pool, train_size=cfg["n"], random_state=seed)
            y_use = y_tr.copy()
            if cfg["noise"] > 0:
                nf = int(cfg["noise"] * len(y_tr))
                fi = np.random.choice(len(y_tr), nf, replace=False)
                y_use[fi] = np.random.randint(0, 10, nf)
            _, log = run_cond(X_tr, y_use, X_ev, y_ev,
                              l2=cfg["l2"], early_stop=cfg["early"])
            all_logs[cname].append(log)
            r = log[-1]
            print(f"  {cname} s={seed}: te={r['te']:.3f} "
                  f"FIM={r['fim_norm']:.4f} sharp={r['sharpness']:.4f}")

    # ---- pool final epoch ----
    rows = []
    for cname, logs in all_logs.items():
        for i, log in enumerate(logs):
            r = log[-1]
            # early epoch (ep~20)
            ep20 = next((x for x in log if x["ep"] >= 20), log[0])
            rows.append({
                "cond": cname, "seed": SEEDS[i],
                "final_te":    r["te"],
                "final_fim":   r["fim_norm"],
                "final_sharp": r["sharpness"],
                "ep20_fim":    ep20["fim_norm"],
                "ep20_sharp":  ep20["sharpness"],
            })

    fim_f   = [r["final_fim"]   for r in rows]
    sharp_f = [r["final_sharp"] for r in rows]
    fim_e   = [r["ep20_fim"]    for r in rows]
    sharp_e = [r["ep20_sharp"]  for r in rows]
    te      = [r["final_te"]    for r in rows]

    rho_fim_f,   p_fim_f   = spearmanr(fim_f,   te)
    rho_sharp_f, p_sharp_f = spearmanr(sharp_f, te)
    rho_fim_e,   p_fim_e   = spearmanr(fim_e,   te)
    rho_sharp_e, p_sharp_e = spearmanr(sharp_e, te)

    # partial R^2 (linear proxy)
    def partial_r2(y_arr, x1_arr, x2_arr):
        """R^2 of x1 after removing linear effect of x2."""
        from numpy.linalg import lstsq
        y  = np.array(y_arr);  x1 = np.array(x1_arr);  x2 = np.array(x2_arr)
        # residualise x1 on x2
        A  = np.column_stack([x2, np.ones(len(x2))])
        b2 = lstsq(A, x1, rcond=None)[0]
        x1_res = x1 - A @ b2
        # R^2 of x1_res on y
        b1 = lstsq(np.column_stack([x1_res, np.ones(len(x1_res))]), y, rcond=None)[0]
        y_hat = np.column_stack([x1_res, np.ones(len(x1_res))]) @ b1
        ss_res = ((y - y_hat)**2).sum()
        ss_tot = ((y - y.mean())**2).sum()
        return 1 - ss_res / ss_tot if ss_tot > 0 else 0.0

    pr2_fim_given_sharp_f   = partial_r2(te, fim_f,   sharp_f)
    pr2_sharp_given_fim_f   = partial_r2(te, sharp_f, fim_f)
    pr2_fim_given_sharp_e   = partial_r2(te, fim_e,   sharp_e)
    pr2_sharp_given_fim_e   = partial_r2(te, sharp_e, fim_e)

    # ---- save CSV ----
    with open(OUT / "fim_full_table.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader(); w.writerows(rows)

    # ---- plot ----
    COLS = {"A_n40_noreg":"#e74c3c","B_n400_noreg":"#3498db","C_n400_l2light":"#2ecc71",
            "D_n400_l2med":"#27ae60","E_n400_early50":"#e67e22","F_n400_noise30":"#9b59b6"}

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle("FIM_norm Full Study — 6 conditions x 3 seeds\n"
                 "CEI v2 vs SAM sharpness", fontweight="bold")

    # top-left: FIM_norm over training by condition
    ax = axes[0,0]
    for cname, logs in all_logs.items():
        lbl = CONDITIONS[cname]["label"]
        for i, log in enumerate(logs):
            ax.plot([r["ep"] for r in log], [r["fim_norm"] for r in log],
                    color=COLS[cname], alpha=0.35 if i else 0.95,
                    linewidth=1.4 if i else 2.2, label=lbl if not i else None)
    ax.set_title("FIM_norm over training"); ax.set_xlabel("Epoch")
    ax.set_ylabel("FIM_norm"); ax.legend(fontsize=7); ax.grid(alpha=0.3)

    # top-middle: sharpness over training
    ax = axes[0,1]
    for cname, logs in all_logs.items():
        lbl = CONDITIONS[cname]["label"]
        for i, log in enumerate(logs):
            ax.plot([r["ep"] for r in log], [r["sharpness"] for r in log],
                    color=COLS[cname], alpha=0.35 if i else 0.95,
                    linewidth=1.4 if i else 2.2, label=lbl if not i else None)
    ax.set_title("SAM Sharpness over training"); ax.set_xlabel("Epoch")
    ax.set_ylabel("Sharpness"); ax.legend(fontsize=7); ax.grid(alpha=0.3)

    # top-right: FIM_norm vs sharpness scatter (final)
    ax = axes[0,2]
    for cname, logs in all_logs.items():
        for log in logs:
            r = log[-1]
            ax.scatter(r["fim_norm"], r["sharpness"], color=COLS[cname], s=50, zorder=3)
        r0 = all_logs[cname][0][-1]
        ax.scatter(r0["fim_norm"], r0["sharpness"], color=COLS[cname], s=80,
                   label=CONDITIONS[cname]["label"])
    ax.set_title("FIM_norm vs Sharpness (final epoch)")
    ax.set_xlabel("FIM_norm"); ax.set_ylabel("Sharpness")
    ax.legend(fontsize=7); ax.grid(alpha=0.3)

    # bottom-left: FIM_norm@ep20 vs final test_acc
    ax = axes[1,0]
    for cname in CONDITIONS:
        idxs = [i for i, r in enumerate(rows) if r["cond"] == cname]
        ax.scatter([fim_e[i] for i in idxs], [te[i] for i in idxs],
                   color=COLS[cname], s=70, zorder=3,
                   label=CONDITIONS[cname]["label"], edgecolors="w", linewidths=0.5)
    ax.set_title(f"FIM_norm@ep20 vs final test_acc\nrho={rho_fim_e:.3f}  p={p_fim_e:.2e}")
    ax.set_xlabel("FIM_norm at epoch 20"); ax.set_ylabel("Final Test Accuracy")
    ax.legend(fontsize=7); ax.grid(alpha=0.3)

    # bottom-middle: sharpness@ep20 vs final test_acc
    ax = axes[1,1]
    for cname in CONDITIONS:
        idxs = [i for i, r in enumerate(rows) if r["cond"] == cname]
        ax.scatter([sharp_e[i] for i in idxs], [te[i] for i in idxs],
                   color=COLS[cname], s=70, zorder=3,
                   label=CONDITIONS[cname]["label"], edgecolors="w", linewidths=0.5)
    ax.set_title(f"Sharpness@ep20 vs final test_acc\nrho={rho_sharp_e:.3f}  p={p_sharp_e:.2e}")
    ax.set_xlabel("Sharpness at epoch 20"); ax.set_ylabel("Final Test Accuracy")
    ax.legend(fontsize=7); ax.grid(alpha=0.3)

    # bottom-right: partial R^2 bar chart
    ax = axes[1,2]
    labels = ["FIM|sharp\n(final)", "sharp|FIM\n(final)",
              "FIM|sharp\n(ep20)",  "sharp|FIM\n(ep20)"]
    vals   = [pr2_fim_given_sharp_f, pr2_sharp_given_fim_f,
              pr2_fim_given_sharp_e, pr2_sharp_given_fim_e]
    cols   = ["#3498db","#e74c3c","#2ecc71","#e67e22"]
    bars   = ax.bar(labels, vals, color=cols, alpha=0.8)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_title("Partial R^2 (unique variance explained)")
    ax.set_ylabel("Partial R^2"); ax.grid(alpha=0.3, axis="y")
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
                f"{v:.3f}", ha="center", fontsize=9)

    plt.tight_layout()
    fig.savefig(OUT / "fim_full_results.png", dpi=150, bbox_inches="tight")
    print(f"\nSaved: {OUT / 'fim_full_results.png'}")

    # ---- terminal summary ----
    print("\n====== FIM_norm FULL STUDY RESULTS ======")
    print(f"\n  {'Metric':<22} {'rho':>7}  {'p':>10}  {'partial_R2':>12}")
    print(f"  {'-'*55}")
    print(f"  {'FIM_norm (final)':<22} {rho_fim_f:>7.3f}  {p_fim_f:>10.2e}"
          f"  {'—':>12}")
    print(f"  {'Sharpness (final)':<22} {rho_sharp_f:>7.3f}  {p_sharp_f:>10.2e}"
          f"  {'—':>12}")
    print(f"  {'FIM_norm@ep20':<22} {rho_fim_e:>7.3f}  {p_fim_e:>10.2e}"
          f"  {'—':>12}")
    print(f"  {'Sharpness@ep20':<22} {rho_sharp_e:>7.3f}  {p_sharp_e:>10.2e}"
          f"  {'—':>12}")
    print(f"\n  Partial R^2 (unique variance):")
    print(f"    FIM_norm  | sharpness (final): {pr2_fim_given_sharp_f:+.4f}")
    print(f"    Sharpness | FIM_norm  (final): {pr2_sharp_given_fim_f:+.4f}")
    print(f"    FIM_norm  | sharpness (ep20):  {pr2_fim_given_sharp_e:+.4f}")
    print(f"    Sharpness | FIM_norm  (ep20):  {pr2_sharp_given_fim_e:+.4f}")

    print(f"\n  Interpretation:")
    if pr2_fim_given_sharp_e > 0.03:
        print(f"    FIM_norm@ep20 adds UNIQUE information beyond sharpness.")
    else:
        print(f"    FIM_norm@ep20 does NOT add unique information beyond sharpness.")
    if abs(rho_fim_e) > abs(rho_sharp_e):
        print(f"    FIM_norm@ep20 is a STRONGER early predictor than sharpness@ep20.")
    else:
        print(f"    Sharpness@ep20 remains the stronger early predictor.")

    plt.show()


if __name__ == "__main__":
    run()
