"""
Run only condition C (n=5000, 30% noise) for CIFAR ResNet-18 test.
Conditions A and B were already captured from the first run.
Uses 25 epochs for better convergence than the 15-epoch run.
"""
import sys, math, os
import numpy as np
import torch
import torch.nn as nn
import torchvision
import torchvision.transforms as T
from pathlib import Path
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).parent))
from sci_tracker import effective_rank
from fim_cifar_test import (load_cifar10, make_resnet18_cifar,
                             fim_norm_cifar, sam_cifar, DATA_DIR,
                             LR, WD, BATCH)

SEED   = 42
OUT    = Path(__file__).parent
EPOCHS = 25
EVAL_BATCH = 512

def batched_acc(model, X, y, device="cpu"):
    model.eval()
    correct = 0
    with torch.no_grad():
        for i in range(0, len(X), EVAL_BATCH):
            xb = X[i:i+EVAL_BATCH].to(device)
            yb = y[i:i+EVAL_BATCH].to(device)
            correct += (model(xb).argmax(1) == yb).sum().item()
    return correct / len(X)

def train_cond_C(X_tr, y_tr, X_te, y_te, X_ev, y_ev, device="cpu"):
    model = make_resnet18_cifar().to(device)
    opt   = torch.optim.SGD(model.parameters(), lr=LR, momentum=0.9,
                             weight_decay=WD, nesterov=True)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=EPOCHS)
    crit  = nn.CrossEntropyLoss()
    n = len(X_tr)

    for ep in range(EPOCHS):
        model.train()
        perm = torch.randperm(n)
        for s in range(0, n, BATCH):
            b = perm[s:s+BATCH]
            opt.zero_grad()
            crit(model(X_tr[b].to(device)), y_tr[b].to(device)).backward()
            opt.step()
        sched.step()

        if ep % 5 == 0 or ep == EPOCHS - 1:
            tr = batched_acc(model, X_tr, y_tr, device)
            te = batched_acc(model, X_te, y_te, device)
            fm = fim_norm_cifar(model, X_tr, y_tr, device=device)
            print(f"    ep={ep:3d}: tr={tr:.3f} te={te:.3f} FIM={fm:.5f}", flush=True)

    fm_final = fim_norm_cifar(model, X_tr, y_tr, device=device)
    te_final = batched_acc(model, X_te, y_te, device)
    return te_final, fm_final

SEEDS = [42, 7, 123]
print("\n=== C_n5000_noise30 (n=5000, 30% noise, 25 epochs) ===", flush=True)
c_fims, c_tes = [], []
for seed in SEEDS:
    torch.manual_seed(seed); np.random.seed(seed)
    print(f"  seed={seed}:", flush=True)
    X_tr, y_tr, X_te, y_te, X_ev, y_ev = load_cifar10(
        DATA_DIR, n_train_limit=5000, noise=0.30, seed=seed)
    te, fm = train_cond_C(X_tr, y_tr, X_te, y_te, X_ev, y_ev)
    c_fims.append(fm); c_tes.append(te)
    print(f"  FINAL: te={te:.3f} FIM={fm:.5f}", flush=True)

print(f"\nCondition C mean: te={np.mean(c_tes):.3f}  FIM={np.mean(c_fims):.5f}", flush=True)

# ---- Assemble full 3-condition picture using A/B data from 15-ep run ----
# These values are the finals from the first run (15 epochs)
A_fims = [0.29550, 0.32491, 0.29345]
A_tes  = [0.333,   0.344,   0.353  ]
B_fims = [0.32965, 0.27211, 0.39646]
B_tes  = [0.582,   0.569,   0.580  ]
C_fims = c_fims
C_tes  = c_tes

all_fims = A_fims + B_fims + C_fims
all_tes  = A_tes  + B_tes  + C_tes
rho, p = spearmanr(all_fims, all_tes)

print("\n====== CIFAR-10 / ResNet-18 RESULTS (A+B @15ep, C @25ep) ======")
print(f"  A (n=500 noreg):    FIM={np.mean(A_fims):.5f}+-{np.std(A_fims):.5f}  te={np.mean(A_tes):.3f}")
print(f"  B (n=5000 wd=1e-4): FIM={np.mean(B_fims):.5f}+-{np.std(B_fims):.5f}  te={np.mean(B_tes):.3f}")
print(f"  C (n=5000 30%noise):FIM={np.mean(C_fims):.5f}+-{np.std(C_fims):.5f}  te={np.mean(C_tes):.3f}")
print(f"  Overall rho(FIM, test_acc) = {rho:.3f}  p={p:.2e}")
print(f"  Direction correct (negative): {rho < 0}")

with open(OUT / "fim_cifar_summary.txt", "w") as f:
    f.write("FIM_norm CIFAR-10 / ResNet-18\n")
    f.write("Note: A+B trained 15 epochs, C trained 25 epochs\n")
    f.write(f"rho={rho:.3f}  p={p:.2e}\n")
    f.write(f"Direction correct: {rho < 0}\n")
    f.write(f"  A_n500_noreg:    FIM={np.mean(A_fims):.5f}  te={np.mean(A_tes):.3f}\n")
    f.write(f"  B_n5000_gen:     FIM={np.mean(B_fims):.5f}  te={np.mean(B_tes):.3f}\n")
    f.write(f"  C_n5000_noise30: FIM={np.mean(C_fims):.5f}  te={np.mean(C_tes):.3f}\n")
print(f"Saved: {OUT / 'fim_cifar_summary.txt'}")
