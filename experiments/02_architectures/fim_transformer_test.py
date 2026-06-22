"""
CEI v2 — FIM_norm on Transformer with LayerNorm (PyTorch).

Architecture: small ViT-style encoder on digits (8x8 images).
  - 8 patches of dim 8, linearly projected to d_model=64
  - Prepend CLS token
  - 2x TransformerEncoder layers (nhead=4, ffn=128, LayerNorm)
  - CLS token -> FC(64 -> 10)

Key distinction from CNN test: uses LayerNorm (not BatchNorm).
This fully tests architecture-agnosticity — FIM_norm should work
regardless of normalisation scheme because it operates in param space.

Dual acid test: noise (n=400 fixed) + n_train (noise=0 fixed).
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

SEED  = 42
OUT   = Path(__file__).parent
N_FIM = 80
BATCH = 64
EPOCHS = 120
LR    = 1e-3
torch.manual_seed(SEED)


# ------------------------------------------------------------------ #
#  Small Transformer                                                   #
# ------------------------------------------------------------------ #

class DigitsTransformer(nn.Module):
    """
    Treats 64-dim digit feature as 8 tokens of dim 8,
    projects to d_model=64, applies 2-layer transformer encoder.
    """
    def __init__(self, d_model=64, nhead=4, n_layers=2, d_ff=128, dropout=0.0):
        super().__init__()
        self.patch_proj = nn.Linear(8, d_model)          # 8-dim patch -> d_model
        self.cls_token  = nn.Parameter(torch.randn(1, 1, d_model) * 0.02)
        self.pos_emb    = nn.Parameter(torch.randn(1, 9, d_model) * 0.02)  # 8 patches + CLS

        enc_layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=nhead, dim_feedforward=d_ff,
            dropout=dropout, batch_first=True, norm_first=True   # pre-LN
        )
        self.encoder = nn.TransformerEncoder(enc_layer, num_layers=n_layers)
        self.norm    = nn.LayerNorm(d_model)
        self.head    = nn.Linear(d_model, 10)

    def forward(self, x):
        # x: (B, 64) -> (B, 8, 8) patches
        x = x.reshape(x.shape[0], 8, 8)
        x = self.patch_proj(x)                          # (B, 8, d_model)
        cls = self.cls_token.expand(x.shape[0], -1, -1) # (B, 1, d_model)
        x   = torch.cat([cls, x], dim=1)                # (B, 9, d_model)
        x   = x + self.pos_emb
        x   = self.encoder(x)                           # (B, 9, d_model)
        x   = self.norm(x[:, 0])                        # CLS token
        return self.head(x)


# ------------------------------------------------------------------ #
#  FIM_norm and SAM sharpness for PyTorch model                       #
# ------------------------------------------------------------------ #

def fim_norm_torch(model, X_np, y_np, n_samples=N_FIM):
    model.eval()
    n, n_use = len(X_np), min(n_samples, len(X_np))
    idx      = np.random.choice(n, n_use, replace=False)
    crit     = nn.CrossEntropyLoss()
    grads    = []
    for i in idx:
        model.zero_grad()
        x = torch.tensor(X_np[i:i+1], dtype=torch.float32)
        y = torch.tensor([int(y_np[i])], dtype=torch.long)
        crit(model(x), y).backward()
        g = torch.cat([p.grad.flatten() for p in model.parameters()
                       if p.grad is not None])
        grads.append(g.detach().numpy())
    G   = np.array(grads)
    F_d = (G @ G.T) / n_use
    model.train()
    return effective_rank(F_d) / n_use


def sam_sharp_torch(model, X_np, y_np, rho=0.05, n_pts=100):
    model.eval()
    n   = min(n_pts, len(X_np))
    idx = np.random.choice(len(X_np), n, replace=False)
    X_t = torch.tensor(X_np[idx], dtype=torch.float32)
    y_t = torch.tensor(y_np[idx], dtype=torch.long)
    crit = nn.CrossEntropyLoss()
    model.zero_grad()
    loss0 = crit(model(X_t), y_t); loss0.backward()
    gnorm = torch.sqrt(sum((p.grad**2).sum() for p in model.parameters()
                           if p.grad is not None))
    scale = rho / (gnorm + 1e-12)
    saved = []
    for p in model.parameters():
        saved.append(p.data.clone())
        if p.grad is not None:
            p.data += scale * p.grad
    with torch.no_grad():
        loss1 = crit(model(X_t), y_t)
    sharp = float((loss1 - loss0).detach())
    for p, s in zip(model.parameters(), saved):
        p.data = s
    model.train()
    return sharp


# ------------------------------------------------------------------ #
#  Training                                                            #
# ------------------------------------------------------------------ #

def train_cond(X_tr, y_tr, X_te, y_te, epochs=EPOCHS, lr=LR,
               measure_every=20):
    model = DigitsTransformer()
    opt   = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    crit  = nn.CrossEntropyLoss()
    X_tt  = torch.tensor(X_tr, dtype=torch.float32)
    y_tt  = torch.tensor(y_tr, dtype=torch.long)
    X_et  = torch.tensor(X_te, dtype=torch.float32)
    y_et  = torch.tensor(y_te, dtype=torch.long)
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
            sharp = sam_sharp_torch(model, X_tr, y_tr)
            log.append({"ep":ep, "tr":round(tr,4), "te":round(te,4),
                        "fim_norm":round(fm,6), "sharpness":round(sharp,6)})
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

    print("\n=== Transformer EXP A: noise acid test (n=400) ===")
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

    print("\n=== Transformer EXP B: n_train probe (noise=0) ===")
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

    def pool(res):
        fm, te = [], []
        for log in res.values():
            r = log[-1]; fm.append(r["fim_norm"]); te.append(r["te"])
        return fm, te

    n_fm, n_te = pool(res_n)
    t_fm, t_te = pool(res_t)
    rho_n, p_n = spearmanr(n_fm, n_te)
    rho_t, p_t = spearmanr(t_fm, t_te)

    def cond_means(res, keys, seeds):
        d = {}
        for k in keys:
            ls = [res[(k,s)][-1] for s in seeds]
            d[k] = (np.mean([l["fim_norm"] for l in ls]),
                    np.std ([l["fim_norm"] for l in ls]),
                    np.mean([l["te"]       for l in ls]))
        return d

    nm  = cond_means(res_n, NOISE,  SEEDS)
    ntm = cond_means(res_t, NTRAIN, SEEDS)

    CN = {0.0:"#2ecc71", 0.15:"#3498db", 0.30:"#e67e22", 0.50:"#e74c3c"}
    CT = {40:"#e74c3c", 200:"#e67e22", 400:"#3498db", 800:"#2ecc71"}

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("FIM_norm on Transformer (LayerNorm) — Dual Acid Test\n"
                 "2-layer encoder, d_model=64, 8 patches", fontweight="bold")

    for ax, res, keys, cmap, title, rho, p in [
        (axes[0,0], res_n, NOISE,  CN, "Noise probe — FIM_norm", rho_n, p_n),
        (axes[0,1], res_t, NTRAIN, CT, "n_train probe — FIM_norm", rho_t, p_t),
    ]:
        for k in keys:
            for i, seed in enumerate(SEEDS):
                log = res[(k,seed)]
                ax.plot([r["ep"] for r in log], [r["fim_norm"] for r in log],
                        color=cmap[k], alpha=0.35 if i else 0.9,
                        linewidth=1.4 if i else 2.2,
                        label=(f"noise={k:.0%}" if isinstance(k,float) and not i
                               else (f"n={k}" if not i else None)))
        ax.set_title(f"{title}\nrho={rho:.3f}  p={p:.2e}")
        ax.set_xlabel("Epoch"); ax.set_ylabel("FIM_norm")
        ax.legend(fontsize=8); ax.grid(alpha=0.3)

    for ax, res, keys, cmap, rho, p, xlabel in [
        (axes[1,0], res_n, NOISE,  CN, rho_n, p_n, "Noise probe"),
        (axes[1,1], res_t, NTRAIN, CT, rho_t, p_t, "n_train probe"),
    ]:
        for k in keys:
            fms = [res[(k,s)][-1]["fim_norm"] for s in SEEDS]
            tes = [res[(k,s)][-1]["te"]       for s in SEEDS]
            lbl = f"noise={k:.0%}" if isinstance(k,float) else f"n={k}"
            ax.scatter(fms, tes, color=cmap[k], s=70, zorder=3, label=lbl,
                       edgecolors="w", linewidths=0.5)
            ax.errorbar(np.mean(fms), np.mean(tes),
                        xerr=np.std(fms), yerr=np.std(tes),
                        color=cmap[k], alpha=0.5, capsize=3)
        ax.set_title(f"Transformer {xlabel}: FIM_norm vs test_acc\n"
                     f"rho={rho:.3f}  p={p:.2e}")
        ax.set_xlabel("FIM_norm"); ax.set_ylabel("Test Accuracy")
        ax.legend(fontsize=8); ax.grid(alpha=0.3)

    plt.tight_layout()
    fig.savefig(OUT / "fim_transformer_results.png", dpi=150, bbox_inches="tight")
    print(f"\nSaved: {OUT / 'fim_transformer_results.png'}")

    print("\n====== TRANSFORMER (LAYERNORM) RESULTS ======")
    print(f"\n  Noise probe (n=400 fixed):")
    for noise in NOISE:
        m = nm[noise]
        print(f"  noise={noise:.0%}: FIM_norm={m[0]:.4f}±{m[1]:.4f}  te={m[2]:.3f}")
    print(f"  rho={rho_n:.3f}  p={p_n:.2e}")

    print(f"\n  n_train probe (noise=0):")
    for n in NTRAIN:
        m = ntm[n]
        print(f"  n={n:4d}: FIM_norm={m[0]:.4f}±{m[1]:.4f}  te={m[2]:.3f}")
    print(f"  rho={rho_t:.3f}  p={p_t:.2e}")

    consistent = (rho_n < 0) == (rho_t < 0)
    both_sig   = p_n < 0.05 and p_t < 0.05
    print(f"\n  CONSISTENCY: same_dir={consistent}  both_sig={both_sig}")
    verdict = ("PASSES" if (consistent and both_sig)
               else ("PARTIAL" if consistent else "FAILS"))
    print(f"  => {verdict}")

    with open(OUT / "fim_transformer_summary.txt", "w") as f:
        f.write("FIM_norm TRANSFORMER (LayerNorm) RESULTS\n")
        f.write(f"Noise probe   rho={rho_n:.3f}  p={p_n:.2e}\n")
        f.write(f"n_train probe rho={rho_t:.3f}  p={p_t:.2e}\n")
        f.write(f"Consistent: {consistent}  Both_sig: {both_sig}\n")
        f.write(f"Verdict: {verdict}\n")
    print(f"Saved: {OUT / 'fim_transformer_summary.txt'}")
    plt.show()


if __name__ == "__main__":
    run()
