"""
CEI v2 — FIM_norm on ResNet-18 / CIFAR-10.

This is the v1 benchmark: CEI v1 showed increasing activation erank on
ResNet-18 (opposite direction to MLP), which was attributed to BatchNorm.
FIM_norm should be BatchNorm-agnostic — this is the direct replication test.

Architecture: ResNet-18 with CIFAR mods
  - First conv: 7x7 stride-2 -> 3x3 stride-1
  - Remove maxpool

3 conditions x 3 seeds = 9 runs:
  A: n=500,  no reg  (overfit relative to full CIFAR)
  B: n=5000, wd=1e-4 (generalise)
  C: n=5000, 30%noise, wd=1e-4

FIM_norm computed via dual N=60 per-sample gradients.
SAM sharpness for comparison.

Output: fim_cifar_results.png + fim_cifar_summary.txt
"""

import sys, math, os
import numpy as np
import torch
import torch.nn as nn
import torchvision
import torchvision.transforms as T
from pathlib import Path
from sklearn.model_selection import train_test_split
from scipy.stats import spearmanr
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).parent))
from sci_tracker import effective_rank

SEED      = 42
OUT       = Path(__file__).parent
DATA_DIR  = OUT / "cifar10_data"
N_FIM     = 60
BATCH     = 64
EVAL_BATCH = 512      # mini-batch size for accuracy eval (avoids OOM)
EPOCHS    = 15        # 15 epochs enough to see trend; 30 was too slow on CPU
LR        = 0.05
WD        = 1e-4
torch.manual_seed(SEED)


# ------------------------------------------------------------------ #
#  CIFAR-10 data                                                       #
# ------------------------------------------------------------------ #

_CIFAR_CACHE = {}   # module-level cache: load full tensors once, subsample each call

def load_cifar10(data_dir, n_train_limit=None, noise=0.0, seed=42):
    DATA_DIR.mkdir(exist_ok=True)

    # cache the full train/test tensors so 9 calls don't reload 50k images each time
    if "X_tr_full" not in _CIFAR_CACHE:
        cache_path = DATA_DIR / "cifar10_tensors.pt"
        if cache_path.exists():
            print("  Loading cached CIFAR-10 tensors...", flush=True)
            d = torch.load(cache_path)
            _CIFAR_CACHE.update(d)
        else:
            print("  Building CIFAR-10 tensor cache (one-time, ~60s)...", flush=True)
            transform = T.Compose([T.ToTensor(),
                                   T.Normalize((0.4914,0.4822,0.4465),
                                               (0.2023,0.1994,0.2010))])
            ds_tr = torchvision.datasets.CIFAR10(str(data_dir), train=True,
                                                  download=True, transform=transform)
            ds_te = torchvision.datasets.CIFAR10(str(data_dir), train=False,
                                                  download=True, transform=transform)
            X_tr_full = torch.stack([ds_tr[i][0] for i in range(len(ds_tr))])
            y_tr_full = torch.tensor([ds_tr[i][1] for i in range(len(ds_tr))])
            X_te_full = torch.stack([ds_te[i][0] for i in range(len(ds_te))])
            y_te_full = torch.tensor([ds_te[i][1] for i in range(len(ds_te))])
            d = dict(X_tr_full=X_tr_full, y_tr_full=y_tr_full,
                     X_te_full=X_te_full, y_te_full=y_te_full)
            torch.save(d, cache_path)
            _CIFAR_CACHE.update(d)
            print("  Cached.", flush=True)

    X_tr = _CIFAR_CACHE["X_tr_full"].clone()
    y_tr = _CIFAR_CACHE["y_tr_full"].clone()
    X_te = _CIFAR_CACHE["X_te_full"]
    y_te = _CIFAR_CACHE["y_te_full"]

    if n_train_limit:
        rng  = torch.Generator().manual_seed(seed)
        idx  = torch.randperm(len(X_tr), generator=rng)[:n_train_limit]
        X_tr, y_tr = X_tr[idx], y_tr[idx]

    if noise > 0:
        rng  = np.random.RandomState(seed)
        n_f  = int(noise * len(y_tr))
        fidx = rng.choice(len(y_tr), n_f, replace=False)
        y_tr = y_tr.clone()
        y_tr[fidx] = torch.tensor(rng.randint(0, 10, n_f), dtype=torch.long)

    # fixed 500-pt eval subset from test set
    X_ev = X_te[:500]; y_ev = y_te[:500]
    return X_tr, y_tr, X_te, y_te, X_ev, y_ev


# ------------------------------------------------------------------ #
#  ResNet-18 CIFAR variant                                             #
# ------------------------------------------------------------------ #

def make_resnet18_cifar():
    model = torchvision.models.resnet18(weights=None)
    model.conv1 = nn.Conv2d(3, 64, 3, stride=1, padding=1, bias=False)
    model.maxpool = nn.Identity()
    return model


# ------------------------------------------------------------------ #
#  Metrics                                                             #
# ------------------------------------------------------------------ #

def fim_norm_cifar(model, X, y, n_samples=N_FIM, device="cpu"):
    model.eval()
    n, n_use = len(X), min(n_samples, len(X))
    idx      = np.random.choice(n, n_use, replace=False)
    crit     = nn.CrossEntropyLoss()
    grads    = []
    for i in idx:
        model.zero_grad()
        xi = X[i:i+1].to(device)
        yi = y[i:i+1].to(device)
        crit(model(xi), yi).backward()
        g = torch.cat([p.grad.flatten() for p in model.parameters()
                       if p.grad is not None])
        grads.append(g.detach().cpu().numpy())
    G   = np.array(grads)
    F_d = (G @ G.T) / n_use
    model.train()
    return effective_rank(F_d) / n_use


def sam_cifar(model, X, y, rho=0.05, n_pts=64, device="cpu"):
    model.eval()
    n   = min(n_pts, len(X))
    idx = np.random.choice(len(X), n, replace=False)
    xt  = X[idx].to(device); yt = y[idx].to(device)
    crit = nn.CrossEntropyLoss()
    model.zero_grad()
    loss0 = crit(model(xt), yt); loss0.backward()
    gnorm = torch.sqrt(sum((p.grad**2).sum() for p in model.parameters()
                           if p.grad is not None))
    scale = rho / (gnorm + 1e-12)
    saved = []
    for p in model.parameters():
        saved.append(p.data.clone())
        if p.grad is not None:
            p.data += scale * p.grad
    with torch.no_grad():
        loss1 = crit(model(xt), yt)
    sharp = float((loss1 - loss0).detach())
    for p, s in zip(model.parameters(), saved):
        p.data = s
    model.train()
    return sharp


# ------------------------------------------------------------------ #
#  Training                                                            #
# ------------------------------------------------------------------ #

def train_cifar(X_tr, y_tr, X_te, y_te, X_ev, y_ev,
                wd=WD, epochs=EPOCHS, measure_every=5, device="cpu"):
    model = make_resnet18_cifar().to(device)
    opt   = torch.optim.SGD(model.parameters(), lr=LR, momentum=0.9,
                             weight_decay=wd, nesterov=True)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=epochs)
    crit  = nn.CrossEntropyLoss()
    n, log = len(X_tr), []

    for ep in range(epochs):
        model.train()
        perm = torch.randperm(n)
        for s in range(0, n, BATCH):
            b = perm[s:s+BATCH]
            opt.zero_grad()
            crit(model(X_tr[b].to(device)), y_tr[b].to(device)).backward()
            opt.step()
        sched.step()

        if ep % measure_every == 0 or ep == epochs - 1:
            model.eval()
            with torch.no_grad():
                # mini-batched eval — avoids OOM / extreme slowdown on CPU
                def batched_acc(X, y):
                    correct = 0
                    for i in range(0, len(X), EVAL_BATCH):
                        xb = X[i:i+EVAL_BATCH].to(device)
                        yb = y[i:i+EVAL_BATCH].to(device)
                        correct += (model(xb).argmax(1) == yb).sum().item()
                    return correct / len(X)
                tr = batched_acc(X_tr, y_tr)
                te = batched_acc(X_te, y_te)
            # FIM on TRAINING data — consistent with MLP/CNN/Transformer tests,
            # and required for the noise mechanism (corrupted labels live in train set).
            fm    = fim_norm_cifar(model, X_tr, y_tr, device=device)
            sharp = sam_cifar(model, X_ev, y_ev, device=device)
            log.append({"ep":ep, "tr":round(tr,4), "te":round(te,4),
                        "fim_norm":round(fm,6), "sharpness":round(sharp,6)})
            print(f"    ep={ep:3d}: tr={tr:.3f} te={te:.3f} "
                  f"FIM={fm:.5f} sharp={sharp:.4f}")
    return log


# ------------------------------------------------------------------ #
#  Main                                                                #
# ------------------------------------------------------------------ #

def run():
    device = "cpu"

    CONDITIONS = {
        "A_n500_noreg":    {"n": 500,  "noise": 0.0,  "wd": 0.0,  "label": "n=500 no-reg"},
        "B_n5000_gen":     {"n": 5000, "noise": 0.0,  "wd": WD,   "label": "n=5000 wd=1e-4"},
        "C_n5000_noise30": {"n": 5000, "noise": 0.30, "wd": WD,   "label": "n=5000 30%noise"},
    }
    SEEDS = [42, 7, 123]

    all_logs = {}
    for cname, cfg in CONDITIONS.items():
        all_logs[cname] = []
        print(f"\n=== {cname} ({cfg['label']}) ===")
        for seed in SEEDS:
            torch.manual_seed(seed); np.random.seed(seed)
            print(f"  seed={seed}:")
            X_tr, y_tr, X_te, y_te, X_ev, y_ev = load_cifar10(
                DATA_DIR, n_train_limit=cfg["n"], noise=cfg["noise"], seed=seed)
            log = train_cifar(X_tr, y_tr, X_te, y_te, X_ev, y_ev,
                              wd=cfg["wd"], device=device)
            all_logs[cname].append(log)
            r = log[-1]
            print(f"  FINAL: te={r['te']:.3f} FIM={r['fim_norm']:.5f}")

    # ---- pool final ----
    fim_all, te_all, cond_labels = [], [], []
    for cname, logs in all_logs.items():
        for log in logs:
            r = log[-1]
            fim_all.append(r["fim_norm"])
            te_all.append(r["te"])
            cond_labels.append(cname)

    rho, p = spearmanr(fim_all, te_all)

    # ---- plot ----
    COLS = {"A_n500_noreg":"#e74c3c","B_n5000_gen":"#2ecc71","C_n5000_noise30":"#9b59b6"}
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.suptitle("FIM_norm on ResNet-18 / CIFAR-10 (CEI v1 failure case)\n"
                 "3 conditions x 3 seeds, 30 epochs", fontweight="bold")

    ax = axes[0]
    for cname, logs in all_logs.items():
        for i, log in enumerate(logs):
            ax.plot([r["ep"] for r in log], [r["fim_norm"] for r in log],
                    color=COLS[cname], alpha=0.35 if i else 0.9,
                    linewidth=1.4 if i else 2.2,
                    label=CONDITIONS[cname]["label"] if not i else None)
    ax.set_title("FIM_norm over training"); ax.set_xlabel("Epoch")
    ax.set_ylabel("FIM_norm"); ax.legend(fontsize=8); ax.grid(alpha=0.3)

    ax = axes[1]
    for cname, logs in all_logs.items():
        for i, log in enumerate(logs):
            ax.plot([r["ep"] for r in log], [r["te"] for r in log],
                    color=COLS[cname], alpha=0.35 if i else 0.9,
                    linewidth=1.4 if i else 2.2,
                    label=CONDITIONS[cname]["label"] if not i else None)
    ax.set_title("Test Accuracy over training"); ax.set_xlabel("Epoch")
    ax.set_ylabel("Test Accuracy"); ax.legend(fontsize=8); ax.grid(alpha=0.3)

    ax = axes[2]
    for cname, logs in all_logs.items():
        fms = [log[-1]["fim_norm"] for log in logs]
        tes = [log[-1]["te"]       for log in logs]
        ax.scatter(fms, tes, color=COLS[cname], s=80, zorder=3,
                   label=CONDITIONS[cname]["label"], edgecolors="w", linewidths=0.5)
        ax.errorbar(np.mean(fms), np.mean(tes), xerr=np.std(fms), yerr=np.std(tes),
                    color=COLS[cname], alpha=0.5, capsize=3)
    ax.set_title(f"FIM_norm vs Test Acc\nrho={rho:.3f}  p={p:.2e}")
    ax.set_xlabel("FIM_norm"); ax.set_ylabel("Test Accuracy")
    ax.legend(fontsize=8); ax.grid(alpha=0.3)

    plt.tight_layout()
    fig.savefig(OUT / "fim_cifar_results.png", dpi=150, bbox_inches="tight")
    print(f"\nSaved: {OUT / 'fim_cifar_results.png'}")

    print("\n====== CIFAR-10 / ResNet-18 RESULTS ======")
    for cname, logs in all_logs.items():
        fms = [log[-1]["fim_norm"] for log in logs]
        tes = [log[-1]["te"]       for log in logs]
        print(f"  {cname}: FIM={np.mean(fms):.5f}±{np.std(fms):.5f}  te={np.mean(tes):.3f}")
    print(f"  Overall rho(FIM_norm, test_acc) = {rho:.3f}  p={p:.2e}")
    consistent_with_theory = rho < 0
    print(f"  Direction correct (negative): {consistent_with_theory}")

    with open(OUT / "fim_cifar_summary.txt", "w") as f:
        f.write(f"FIM_norm CIFAR-10 / ResNet-18\n")
        f.write(f"rho={rho:.3f}  p={p:.2e}\n")
        f.write(f"Direction correct: {consistent_with_theory}\n")
        for cname, logs in all_logs.items():
            fms = [log[-1]["fim_norm"] for log in logs]
            tes = [log[-1]["te"]       for log in logs]
            f.write(f"  {cname}: FIM={np.mean(fms):.5f}  te={np.mean(tes):.3f}\n")
    print(f"Saved: {OUT / 'fim_cifar_summary.txt'}")
    plt.show()


if __name__ == "__main__":
    run()
