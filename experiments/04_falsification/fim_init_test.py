"""
CEI v2 — FIM@init test. The one regime where loss CANNOT compete.

At initialization every model sits at loss ~ log(10) ~ 2.30, so loss has zero
discriminative power. Therefore ANY correlation between FIM_norm@init and final
test accuracy is, by construction, predictive information beyond loss.

Two sub-tests:

  TEST A (data triage, across conditions): vary n_train and label noise. Compute
         FIM@init on each condition's training data BEFORE any training. Does it
         predict final test_acc? (A pre-training data-quality / setup detector.)

  TEST B (lucky-init geometry, fixed data): hold data fixed (n=400 clean), vary
         ONLY the random initialization across 20 seeds. Does FIM@init predict
         which seeds train to higher final accuracy? (Pure init-geometry signal.)

If either is significant -> a narrow but genuine beyond-loss thesis survives.
If both null -> FIM has no use loss doesn't already cover; metric is closed.

Output: fim_init_test.txt
"""

import sys
import numpy as np
from pathlib import Path
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).parent))
from sci_tracker import effective_rank
from fim_full_study import MLP, BATCH

SEED   = 42
OUT    = Path(__file__).parent
EPOCHS = 200
LR     = 0.005
N_FIX  = 40
np.random.seed(SEED)


def fim_norm_at(model, X, y, n_fix=N_FIX):
    n = len(X); n_use = min(n_fix, n)
    idx = np.random.choice(n, n_use, replace=False)
    G   = np.array([model._grad_single(X[k], y[k]) for k in idx])
    F   = (G @ G.T) / n_use
    return effective_rank(F) / n_use


def train_to_end(model, X_tr, y_tr, X_ev, y_ev):
    n = len(X_tr)
    for _ in range(EPOCHS):
        idx = np.random.permutation(n)
        for s in range(0, n, BATCH):
            b = idx[s:s+BATCH]; model.step(X_tr[b], y_tr[b], LR)
    return model.acc(X_ev, y_ev)


def run():
    X, y = load_digits(return_X_y=True)
    X    = StandardScaler().fit_transform(X)
    X_ev, X_pool, y_ev, y_pool = train_test_split(
        X, y, test_size=len(X)-200, random_state=SEED)

    lines = []
    def emit(s): print(s, flush=True); lines.append(s)

    emit("="*70)
    emit("FIM@init TEST — the regime where loss is structurally uninformative")
    emit("="*70)

    # ---------------- TEST A: across conditions ----------------
    CONDITIONS = [
        ("A_n100",     dict(n=100, noise=0.0,  l2=0.0)),
        ("B_n400",     dict(n=400, noise=0.0,  l2=0.0)),
        ("C_n800",     dict(n=800, noise=0.0,  l2=0.0)),
        ("D_n400_reg", dict(n=400, noise=0.0,  l2=1e-3)),
        ("E_n400_n30", dict(n=400, noise=0.30, l2=0.0)),
        ("F_n400_n50", dict(n=400, noise=0.50, l2=0.0)),
    ]
    SEEDS = [42, 7, 123, 1, 99]
    fim_init_A, final_te_A, loss_init_A = [], [], []

    emit("\n--- TEST A: FIM@init across heterogeneous conditions ---")
    for cname, cfg in CONDITIONS:
        for seed in SEEDS:
            np.random.seed(seed)
            X_tr, _, y_tr, _ = train_test_split(
                X_pool, y_pool, train_size=cfg["n"], random_state=seed)
            y_use = y_tr.copy()
            if cfg["noise"] > 0:
                nf = int(cfg["noise"]*len(y_tr))
                fi = np.random.choice(len(y_tr), nf, replace=False)
                y_use[fi] = np.random.randint(0, 10, nf)
            model = MLP(l2=cfg["l2"])             # <-- fresh init
            fim0  = fim_norm_at(model, X_tr, y_use)   # FIM at init, before training
            loss0 = model._loss(X_tr, y_use)
            te    = train_to_end(model, X_tr, y_use, X_ev, y_ev)
            fim_init_A.append(fim0); final_te_A.append(te); loss_init_A.append(loss0)
        print(f"  {cname} done", flush=True)

    rhoA, pA = spearmanr(fim_init_A, final_te_A)
    rho_loss0, p_loss0 = spearmanr(loss_init_A, final_te_A)
    emit(f"  FIM@init   vs final_te:  rho={rhoA:+.3f}  p={pA:.2e}")
    emit(f"  loss@init  vs final_te:  rho={rho_loss0:+.3f}  p={p_loss0:.2e}  "
         f"(should be ~0: loss is flat at init)")
    emit(f"  loss@init range: [{min(loss_init_A):.3f}, {max(loss_init_A):.3f}] "
         f"(narrow = confirms loss can't discriminate)")

    # ---------------- TEST B: lucky-init, fixed data ----------------
    emit("\n--- TEST B: FIM@init across 20 inits, FIXED data (n=400 clean) ---")
    np.random.seed(SEED)
    X_tr, _, y_tr, _ = train_test_split(
        X_pool, y_pool, train_size=400, random_state=SEED)   # FIXED data

    fim_init_B, final_te_B = [], []
    for s in range(20):
        np.random.seed(1000 + s)      # varies ONLY model init + train shuffling
        model = MLP(l2=0.0)
        fim0  = fim_norm_at(model, X_tr, y_tr)
        te    = train_to_end(model, X_tr, y_tr, X_ev, y_ev)
        fim_init_B.append(fim0); final_te_B.append(te)
    rhoB, pB = spearmanr(fim_init_B, final_te_B)
    emit(f"  FIM@init   vs final_te:  rho={rhoB:+.3f}  p={pB:.2e}  (n=20 inits)")
    emit(f"  FIM@init range: [{min(fim_init_B):.3f}, {max(fim_init_B):.3f}]")
    emit(f"  final_te range: [{min(final_te_B):.3f}, {max(final_te_B):.3f}]")

    # ---------------- verdict ----------------
    emit("\nVERDICT:")
    A_live = pA < 0.05
    B_live = pB < 0.05
    if A_live or B_live:
        emit("  NARROW THESIS SURVIVES — FIM@init carries beyond-loss signal:")
        if A_live: emit(f"    TEST A significant (rho={rhoA:+.3f}, p={pA:.2e}) -> pre-training setup/data detector")
        if B_live: emit(f"    TEST B significant (rho={rhoB:+.3f}, p={pB:.2e}) -> init geometry predicts trainability")
    else:
        emit("  METRIC CLOSED — FIM@init has no beyond-loss signal either:")
        emit(f"    TEST A: rho={rhoA:+.3f}, p={pA:.2e} (n.s.)")
        emit(f"    TEST B: rho={rhoB:+.3f}, p={pB:.2e} (n.s.)")
        emit("    Loss dominates FIM at every checkpoint including init. Honest")
        emit("    conclusion: gradient effective rank is not a useful generalization")
        emit("    predictor beyond loss. Write the negative-results paper.")

    with open(OUT / "fim_init_test.txt", "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\nSaved: {OUT/'fim_init_test.txt'}")


if __name__ == "__main__":
    run()
