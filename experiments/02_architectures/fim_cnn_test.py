"""
CEI v2 — FIM_norm on CNN with BatchNorm (PyTorch).

This is the critical architecture test. CEI v1 completely failed on
ResNet-18/CIFAR because BatchNorm artificially inflates activation erank.
FIM_norm is computed in parameter space, not activation space — hypothesis:
it should be BatchNorm-agnostic.

Architecture: small CNN on digits (8x8 grayscale)
  Conv(1->16, 3x3) -> BN -> ReLU -> Conv(16->32, 3x3) -> BN -> ReLU
  -> AdaptiveAvgPool(1) -> FC(32->10)

Same dual acid test:
  Exp A: noise acid test (n=400 fixed, noise=0/15/30/50%)
  Exp B: n_train probe (noise=0, n=40/200/400/800)

If direction is consistent and significant in both: PASSES.
"""

import sys, math
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from pathlib import Path
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from scipy.stats import spearmanr
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).parent))
from sci_tracker import effective_rank

SEED   = 42
OUT    = Path(__file__).parent
N_FIM  = 80
BATCH  = 64
EPOCHS = 150
LR     = 3e-3
torch.manual_seed(SEED)


# ------------------------------------------------------------------ #
#  Small CNN with BatchNorm                                            #
# ------------------------------------------------------------------ #

class DigitsCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 16, 3, padding=1)
        self.bn1   = nn.BatchNorm2d(16)
        self.conv2 = nn.Conv2d(16, 32, 3, padding=1)
        self.bn2   = nn.BatchNorm2d(32)
        self.pool  = nn.AdaptiveAvgPool2d(1)
        self.fc    = nn.Linear(32, 10)

    def forward(self, x):
        x = F.relu(self.bn1(self.conv1(x)))
        x = F.relu(self.bn2(self.conv2(x)))
        x = self.pool(x).flatten(1)
        return self.fc(x)


def make_tensor(X_np, y_np=None):
    """Reshape digits (N,64) -> (N,1,8,8) tensor."""
    X_t = torch.tensor(X_np, dtype=torch.float32).reshape(-1, 1, 8, 8)
    if y_np is None:
        return X_t
    return X_t, torch.tensor(y_np, dtype=torch.long)


# ------------------------------------------------------------------ #
#  FIM_norm via per-sample gradients (PyTorch)                        #
# ------------------------------------------------------------------ #

def fim_norm_torch(model, X_np, y_np, n_samples=N_FIM, device="cpu"):
    """
    Computes FIM_norm for a PyTorch model using per-sample gradients.
    Uses the dual N x N Gram matrix formulation.
    """
    model.eval()
    n     = len(X_np)
    n_use = min(n_samples, n)
    idx   = np.random.choice(n, n_use, replace=False)

    grad_vecs = []
    crit = nn.CrossEntropyLoss()

    for i in idx:
        model.zero_grad()
        x = torch.tensor(X_np[i:i+1], dtype=torch.float32).reshape(1, 1, 8, 8)
        y = torch.tensor([int(y_np[i])], dtype=torch.long)
        loss = crit(model(x), y)
        loss.backward()
        g = torch.cat([p.grad.flatten() for p in model.parameters()
                       if p.grad is not None])
        grad_vecs.append(g.detach().numpy())

    G     = np.array(grad_vecs)          # (n_use, d)
    F_d   = (G @ G.T) / n_use            # (n_use, n_use)
    er    = effective_rank(F_d)
    model.train()
    return er / n_use


# ------------------------------------------------------------------ #
#  SAM sharpness (PyTorch)                                            #
# ------------------------------------------------------------------ #

def sam_sharpness_torch(model, X_np, y_np, rho=0.05, n_pts=100, device="cpu"):
    model.eval()
    n    = min(n_pts, len(X_np))
    idx  = np.random.choice(len(X_np), n, replace=False)
    X_t, y_t = make_tensor(X_np[idx], y_np[idx])
    crit = nn.CrossEntropyLoss()

    model.zero_grad()
    loss_base = crit(model(X_t), y_t)
    loss_base.backward()

    # compute gradient norm and perturbation
    grad_norm = torch.sqrt(sum((p.grad**2).sum()
                               for p in model.parameters() if p.grad is not None))
    eps_scale = rho / (grad_norm + 1e-12)

    orig_params = []
    for p in model.parameters():
        orig_params.append(p.data.clone())
        if p.grad is not None:
            p.data += eps_scale * p.grad

    with torch.no_grad():
        loss_pert = crit(model(X_t), y_t)
    sharp = float(loss_pert - loss_base)

    for p, orig in zip(model.parameters(), orig_params):
        p.data = orig
    model.train()
    return sharp


# ------------------------------------------------------------------ #
#  Training                                                            #
# ------------------------------------------------------------------ #

def train_cond(X_tr, y_tr, X_te, y_te, epochs=EPOCHS, lr=LR,
               measure_every=20):
    model = DigitsCNN()
    opt   = torch.optim.Adam(model.parameters(), lr=lr)
    crit  = nn.CrossEntropyLoss()
    X_tt, y_tt = make_tensor(X_tr, y_tr)
    X_et, y_et = make_tensor(X_te, y_te)
    n, log = len(X_tr), []

    for ep in range(epochs):
        model.train()
        perm = torch.randperm(n)
        for s in range(0, n, BATCH):
            b = perm[s:s+BATCH]
            opt.zero_grad()
            crit(model(X_tt[b]), y_tt[b]).backward()
            opt.step()

        if ep % measure_every == 0 or ep == epochs - 1:
            model.eval()
            with torch.no_grad():
                tr = (model(X_tt).argmax(1) == y_tt).float().mean().item()
                te = (model(X_et).argmax(1) == y_et).float().mean().item()
            fm    = fim_norm_torch(model, X_tr, y_tr)
            sharp = sam_sharpness_torch(model, X_tr, y_tr)
            log.append({"ep": ep, "tr": round(tr,4), "te": round(te,4),
                        "fim_norm": round(fm,6), "sharpness": round(sharp,6)})
    return log


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

    print("\n=== EXP A: CNN noise acid test (n=400, BatchNorm) ===")
    res_n = {}
    for noise in NOISE:
        for seed in SEEDS:
            np.random.seed(seed); torch.manual_seed(seed)
            X_tr, _, y_tr, _ = train_test_split(
                X_pool, y_pool, train_size=400, random_state=seed)
            y_noisy = y_tr.copy()
            if noise > 0:
                nf = int(noise * len(y_tr))
                fi = np.random.choice(len(y_tr), nf, replace=False)
                y_noisy[fi] = np.random.randint(0, 10, nf)
            log = train_cond(X_tr, y_noisy, X_ev, y_ev)
            res_n[(noise, seed)] = log
            r = log[-1]
            print(f"  noise={noise:.0%} s={seed}: te={r['te']:.3f} "
                  f"FIM={r['fim_norm']:.4f} sharp={r['sharpness']:.4f}")

    print("\n=== EXP B: CNN n_train probe (noise=0, BatchNorm) ===")
    res_t = {}
    for n in NTRAIN:
        for seed in SEEDS:
            np.random.seed(seed); torch.manual_seed(seed)
            X_tr, _, y_tr, _ = train_test_split(
                X_pool, y_pool, train_size=n, random_state=seed)
            log = train_cond(X_tr, y_tr, X_ev, y_ev)
            res_t[(n, seed)] = log
            r = log[-1]
            print(f"  n={n:4d} s={seed}: te={r['te']:.3f} "
                  f"FIM={r['fim_norm']:.4f} sharp={r['sharpness']:.4f}")

    # ---- pool final ----
    def pool(res):
        fm, te = [], []
        for log in res.values():
            r = log[-1]; fm.append(r["fim_norm"]); te.append(r["te"])
        return fm, te

    n_fm, n_te = pool(res_n)
    t_fm, t_te = pool(res_t)

    rho_n, p_n = spearmanr(n_fm, n_te)
    rho_t, p_t = spearmanr(t_fm, t_te)

    # per-condition means
    def cond_means(res, keys, seeds):
        d = {}
        for k in keys:
            logs = [res[(k,s)][-1] for s in seeds]
            d[k] = (np.mean([l["fim_norm"] for l in logs]),
                    np.std ([l["fim_norm"] for l in logs]),
                    np.mean([l["te"]       for l in logs]))
        return d

    nm  = cond_means(res_n, NOISE,  SEEDS)
    ntm = cond_means(res_t, NTRAIN, SEEDS)

    # ---- plot ----
    CN = {0.0:"#2ecc71", 0.15:"#3498db", 0.30:"#e67e22", 0.50:"#e74c3c"}
    CT = {40:"#e74c3c", 200:"#e67e22", 400:"#3498db", 800:"#2ecc71"}

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("FIM_norm on CNN with BatchNorm — Dual Acid Test\n"
                 "(CEI v1 failed here; does FIM_norm survive?)", fontweight="bold")

    for ax, res, keys, col_map, title, rho, p in [
        (axes[0,0], res_n, NOISE,  CN, "Noise probe — FIM_norm", rho_n, p_n),
        (axes[0,1], res_t, NTRAIN, CT, "n_train probe — FIM_norm", rho_t, p_t),
    ]:
        for k in keys:
            for i, seed in enumerate(SEEDS):
                log = res[(k,seed)]
                ax.plot([r["ep"] for r in log], [r["fim_norm"] for r in log],
                        color=col_map[k], alpha=0.35 if i else 0.9,
                        linewidth=1.4 if i else 2.2,
                        label=f"{k:.0%}" if not i and isinstance(k,float) else
                              (f"n={k}" if not i else None))
        ax.set_title(f"{title}\nrho={rho:.3f}  p={p:.2e}")
        ax.set_xlabel("Epoch"); ax.set_ylabel("FIM_norm"); ax.legend(fontsize=8); ax.grid(alpha=0.3)

    # scatter noise
    ax = axes[1,0]
    for noise in NOISE:
        fms = [res_n[(noise,s)][-1]["fim_norm"] for s in SEEDS]
        tes = [res_n[(noise,s)][-1]["te"]       for s in SEEDS]
        ax.scatter(fms, tes, color=CN[noise], s=70, zorder=3,
                   label=f"noise={noise:.0%}", edgecolors="w", linewidths=0.5)
        ax.errorbar(np.mean(fms), np.mean(tes), xerr=np.std(fms), yerr=np.std(tes),
                    color=CN[noise], alpha=0.5, capsize=3)
    ax.set_title(f"CNN Noise: FIM_norm vs test_acc\nrho={rho_n:.3f}  p={p_n:.2e}")
    ax.set_xlabel("FIM_norm"); ax.set_ylabel("Test Accuracy"); ax.legend(fontsize=8); ax.grid(alpha=0.3)

    # scatter n_train
    ax = axes[1,1]
    for n in NTRAIN:
        fms = [res_t[(n,s)][-1]["fim_norm"] for s in SEEDS]
        tes = [res_t[(n,s)][-1]["te"]       for s in SEEDS]
        ax.scatter(fms, tes, color=CT[n], s=70, zorder=3,
                   label=f"n={n}", edgecolors="w", linewidths=0.5)
        ax.errorbar(np.mean(fms), np.mean(tes), xerr=np.std(fms), yerr=np.std(tes),
                    color=CT[n], alpha=0.5, capsize=3)
    ax.set_title(f"CNN n_train: FIM_norm vs test_acc\nrho={rho_t:.3f}  p={p_t:.2e}")
    ax.set_xlabel("FIM_norm"); ax.set_ylabel("Test Accuracy"); ax.legend(fontsize=8); ax.grid(alpha=0.3)

    plt.tight_layout()
    fig.savefig(OUT / "fim_cnn_results.png", dpi=150, bbox_inches="tight")
    print(f"\nSaved: {OUT / 'fim_cnn_results.png'}")

    print("\n====== CNN + BATCHNORM RESULTS ======")
    print(f"\n  Noise probe (n=400 fixed):")
    print(f"  {'noise':>6}  {'FIM_norm':>10}  {'±':>6}  {'te':>7}")
    for noise in NOISE:
        m = nm[noise]
        print(f"  {noise:>5.0%}  {m[0]:>10.4f}  {m[1]:>6.4f}  {m[2]:>7.3f}")
    print(f"  rho={rho_n:.3f}  p={p_n:.2e}")

    print(f"\n  n_train probe (noise=0):")
    print(f"  {'n_tr':>6}  {'FIM_norm':>10}  {'±':>6}  {'te':>7}")
    for n in NTRAIN:
        m = ntm[n]
        print(f"  {n:>6d}  {m[0]:>10.4f}  {m[1]:>6.4f}  {m[2]:>7.3f}")
    print(f"  rho={rho_t:.3f}  p={p_t:.2e}")

    consistent = (rho_n < 0) == (rho_t < 0)
    both_sig   = p_n < 0.05 and p_t < 0.05
    print(f"\n  Consistency: direction same={consistent}  both_sig={both_sig}")
    if consistent and both_sig:
        print(f"  => CNN + BatchNorm: PASSES DUAL ACID TEST")
        print(f"  => FIM_norm is architecture-agnostic (survives BatchNorm)")
    elif consistent:
        print(f"  => Direction consistent but not both significant. Partial pass.")
    else:
        print(f"  => FAILS on CNN — direction inconsistent with BatchNorm.")

    with open(OUT / "fim_cnn_summary.txt", "w") as f:
        f.write("FIM_norm CNN + BatchNorm Acid Test\n")
        f.write(f"Noise probe rho={rho_n:.3f}  p={p_n:.2e}\n")
        f.write(f"n_train probe rho={rho_t:.3f}  p={p_t:.2e}\n")
        f.write(f"Consistent: {consistent}  Both_sig: {both_sig}\n")
    print(f"Saved: {OUT / 'fim_cnn_summary.txt'}")
    plt.show()


if __name__ == "__main__":
    run()
