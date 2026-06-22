"""
CEI v2 — Early stopping utility test.

Can FIM_norm guide early stopping better than validation loss?

Three stopping strategies, evaluated on 6 conditions x 5 seeds:
  1. VAL_LOSS:  stop when val_loss hasn't improved for patience=15 epochs
  2. FIM_FLAT:  stop when FIM_norm change < threshold for 3 consecutive checks
  3. FIM_THRESH: stop when FIM_norm < percentile threshold (set from train set)
  4. FIXED_200: baseline — always run 200 epochs

Metric: final test_acc on held-out clean test set.

Output: fim_early_stop_results.png + fim_early_stop_table.csv
"""

import sys, csv
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from scipy.stats import wilcoxon

sys.path.insert(0, str(Path(__file__).parent))
from sci_tracker import effective_rank
from fim_full_study import MLP

SEED   = 42
OUT    = Path(__file__).parent
N_FIM  = 60
BATCH  = 64
LR     = 0.005
MAX_EP = 300
MEAS   = 5     # measure every N epochs


def fim_norm_quick(model, X, y, n_samples=N_FIM):
    n     = len(X)
    n_use = min(n_samples, n)
    idx   = np.random.choice(n, n_use, replace=False)
    G     = np.array([model._grad_single(X[k], y[k]) for k in idx])
    F_d   = (G @ G.T) / n_use
    return effective_rank(F_d) / n_use


def train_with_strategy(model, X_tr, y_tr, X_val, y_val, X_te, y_te,
                         strategy="fixed"):
    n = len(X_tr)
    fim_hist, val_loss_hist = [], []
    best_val, patience_count = 1e9, 0
    PATIENCE = 15
    FIM_FLAT_TOL   = 0.005
    FIM_FLAT_WAIT  = 3
    FIM_THRESH_PCT = 0.25   # stop if FIM_norm < 25th pct of first 20 ep values
    fim_initial    = []
    stop_epoch     = MAX_EP - 1

    import torch
    crit_np = lambda X, y: -np.log(
        model._fwd(X)[0][np.arange(len(y)), y] + 1e-12).mean()

    for ep in range(MAX_EP):
        idx = np.random.permutation(n)
        for s in range(0, n, BATCH):
            b = idx[s:s+BATCH]; model.step(X_tr[b], y_tr[b], LR)

        if ep % MEAS != 0:
            continue

        fim   = fim_norm_quick(model, X_tr, y_tr)
        vloss = crit_np(X_val, y_val)
        fim_hist.append((ep, fim))
        val_loss_hist.append((ep, vloss))

        # collect initial FIM estimates for threshold
        if ep < 20 * MEAS:
            fim_initial.append(fim)

        # --- stopping logic ---
        if strategy == "fixed":
            pass   # never stop early

        elif strategy == "val_loss":
            if vloss < best_val - 1e-4:
                best_val, patience_count = vloss, 0
            else:
                patience_count += 1
            if patience_count >= PATIENCE // MEAS:
                stop_epoch = ep; break

        elif strategy == "fim_flat":
            if len(fim_hist) >= FIM_FLAT_WAIT:
                recent = [f for _, f in fim_hist[-FIM_FLAT_WAIT:]]
                if max(recent) - min(recent) < FIM_FLAT_TOL:
                    stop_epoch = ep; break

        elif strategy == "fim_thresh":
            if len(fim_initial) >= 4:
                thresh = np.percentile(fim_initial, FIM_THRESH_PCT * 100)
                if fim < thresh:
                    stop_epoch = ep; break

    te_acc = model.acc(X_te, y_te)
    return te_acc, stop_epoch, fim_hist


def run():
    X, y = load_digits(return_X_y=True)
    X    = StandardScaler().fit_transform(X)
    X_ev, X_pool, y_ev, y_pool = train_test_split(
        X, y, test_size=len(X)-200, random_state=SEED)
    # split eval into val (100) and test (100) for stopping decisions
    X_val, X_te, y_val, y_te = train_test_split(
        X_ev, y_ev, test_size=100, random_state=SEED)

    SEEDS = [42, 7, 123, 17, 99]
    CONDITIONS = {
        "A_n40":       {"n": 40,  "noise": 0.0},
        "B_n400":      {"n": 400, "noise": 0.0},
        "C_n400_n30":  {"n": 400, "noise": 0.30},
    }
    STRATEGIES = ["fixed", "val_loss", "fim_flat", "fim_thresh"]
    SCOLS = {"fixed":"#95a5a6","val_loss":"#e74c3c","fim_flat":"#3498db","fim_thresh":"#2ecc71"}

    results = {}   # (cond, strategy, seed) -> (te_acc, stop_ep)
    rows    = []

    for cname, cfg in CONDITIONS.items():
        for strategy in STRATEGIES:
            for seed in SEEDS:
                np.random.seed(seed)
                X_tr, _, y_tr, _ = train_test_split(
                    X_pool, y_pool, train_size=cfg["n"], random_state=seed)
                y_use = y_tr.copy()
                if cfg["noise"] > 0:
                    nf = int(cfg["noise"] * len(y_tr))
                    fi = np.random.choice(len(y_tr), nf, replace=False)
                    y_use[fi] = np.random.randint(0, 10, nf)
                model = MLP(l2=0.0)
                te, ep, _ = train_with_strategy(
                    model, X_tr, y_use, X_val, y_val, X_te, y_te, strategy)
                results[(cname, strategy, seed)] = (te, ep)
                rows.append({"cond":cname,"strategy":strategy,"seed":seed,
                             "test_acc":round(te,4),"stop_ep":ep})
            mean_te = np.mean([results[(cname,strategy,s)][0] for s in SEEDS])
            mean_ep = np.mean([results[(cname,strategy,s)][1] for s in SEEDS])
            print(f"  {cname:<14} {strategy:<12}: "
                  f"te={mean_te:.3f}  stop@{mean_ep:.0f}")

    # ---- save CSV ----
    with open(OUT / "fim_early_stop_table.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader(); w.writerows(rows)

    # ---- plot ----
    fig, axes = plt.subplots(1, len(CONDITIONS), figsize=(5*len(CONDITIONS), 6))
    fig.suptitle("Early Stopping Utility — FIM_norm vs Val Loss\n"
                 "(5 seeds per condition)", fontweight="bold")

    for ax, (cname, cfg) in zip(axes, CONDITIONS.items()):
        x = np.arange(len(STRATEGIES))
        means = [np.mean([results[(cname,st,s)][0] for s in SEEDS]) for st in STRATEGIES]
        stds  = [np.std ([results[(cname,st,s)][0] for s in SEEDS]) for st in STRATEGIES]
        bars  = ax.bar(x, means, yerr=stds, color=[SCOLS[st] for st in STRATEGIES],
                       alpha=0.85, capsize=5, width=0.6)
        ax.set_xticks(x); ax.set_xticklabels(STRATEGIES, rotation=20, fontsize=9)
        ax.set_title(f"{cname}\nn={cfg['n']}, noise={cfg['noise']:.0%}")
        ax.set_ylabel("Test Accuracy"); ax.set_ylim(0, 1.05)
        ax.grid(alpha=0.3, axis="y")
        for bar, m, s in zip(bars, means, stds):
            ax.text(bar.get_x() + bar.get_width()/2,
                    bar.get_height() + s + 0.01,
                    f"{m:.3f}", ha="center", fontsize=8)
        # highlight best
        best_idx = int(np.argmax(means))
        bars[best_idx].set_edgecolor("black")
        bars[best_idx].set_linewidth(2.5)

    plt.tight_layout()
    fig.savefig(OUT / "fim_early_stop_results.png", dpi=150, bbox_inches="tight")
    print(f"\nSaved: {OUT / 'fim_early_stop_results.png'}")

    # ---- summary ----
    print("\n====== EARLY STOPPING UTILITY ======")
    print(f"  {'cond':<14}  {'strategy':<12}  {'mean_te':>8}  {'std_te':>7}  {'mean_stop_ep':>13}")
    for cname in CONDITIONS:
        for st in STRATEGIES:
            tes = [results[(cname,st,s)][0] for s in SEEDS]
            eps = [results[(cname,st,s)][1] for s in SEEDS]
            print(f"  {cname:<14}  {st:<12}  {np.mean(tes):>8.4f}  "
                  f"{np.std(tes):>7.4f}  {np.mean(eps):>13.1f}")
        print()

    plt.show()


if __name__ == "__main__":
    run()
