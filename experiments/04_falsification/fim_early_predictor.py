"""
CEI v2 — THE DECISIVE TEST.

Does FIM_norm@ep20 predict FINAL test accuracy AFTER controlling for the loss
you could already measure at ep20?

If YES (significant partial correlation) -> FIM_norm carries genuine early
predictive information beyond loss -> the strong thesis survives, the
early-predictor / training-efficiency story is real.

If NO -> FIM_norm@ep20 is just an early loss proxy -> honest incremental
contribution only (BatchNorm-robust loss-correlate).

Design: 6 heterogeneous conditions x 5 seeds = 30 runs. Conditions deliberately
DECOUPLE early loss from final generalization (noisy models fit fast early but
generalize poorly). At ep20 we snapshot 4 early signals; at the end we record
final test accuracy. Then partial correlations.

Early signals captured at ep20:
  fim_train  = FIM_norm on training data (Standard 1)
  fim_eval   = FIM_norm on held-out eval data (alternative; may predict better)
  train_loss = mean CE on training data
  val_loss   = mean CE on held-out eval data  <- the practitioner's baseline

Decisive number: partial( fim@20, final_te | val_loss@20 ).

Output: fim_early_predictor.txt
"""

import sys, math
import numpy as np
from pathlib import Path
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from scipy.stats import spearmanr, pearsonr, rankdata

sys.path.insert(0, str(Path(__file__).parent))
from sci_tracker import effective_rank
from fim_full_study import MLP, BATCH

SEED = 42
OUT  = Path(__file__).parent
EP_EARLY = 20
EPOCHS   = 200
LR       = 0.005
N_FIX    = 40
np.random.seed(SEED)


def fim_norm_at(model, X, y, n_fix=N_FIX):
    n = len(X); n_use = min(n_fix, n)
    idx = np.random.choice(n, n_use, replace=False)
    G   = np.array([model._grad_single(X[k], y[k]) for k in idx])
    F   = (G @ G.T) / n_use
    return effective_rank(F) / n_use


def partial_spearman(x, y, z):
    """Spearman partial correlation of x,y controlling for z."""
    rx, ry, rz = rankdata(x), rankdata(y), rankdata(z)
    def resid(a, b):
        b1 = np.vstack([b, np.ones_like(b)]).T
        coef, *_ = np.linalg.lstsq(b1, a, rcond=None)
        return a - b1 @ coef
    ex, ey = resid(rx, rz), resid(ry, rz)
    r, p = pearsonr(ex, ey)
    return r, p


def train_with_snapshot(X_tr, y_tr, X_ev, y_ev, l2=0.0):
    model = MLP(l2=l2)
    n = len(X_tr)
    snap = None
    for ep in range(EPOCHS):
        idx = np.random.permutation(n)
        for s in range(0, n, BATCH):
            b = idx[s:s+BATCH]; model.step(X_tr[b], y_tr[b], LR)
        if ep == EP_EARLY:
            snap = dict(
                fim_train = fim_norm_at(model, X_tr, y_tr),
                fim_eval  = fim_norm_at(model, X_ev, y_ev),
                train_loss= model._loss(X_tr, y_tr),
                val_loss  = model._loss(X_ev, y_ev),
            )
    final_te = model.acc(X_ev, y_ev)
    return snap, final_te


def run():
    X, y = load_digits(return_X_y=True)
    X    = StandardScaler().fit_transform(X)
    X_ev, X_pool, y_ev, y_pool = train_test_split(
        X, y, test_size=len(X)-200, random_state=SEED)

    CONDITIONS = [
        ("A_n100",     dict(n=100, noise=0.0,  l2=0.0)),
        ("B_n400",     dict(n=400, noise=0.0,  l2=0.0)),
        ("C_n800",     dict(n=800, noise=0.0,  l2=0.0)),
        ("D_n400_reg", dict(n=400, noise=0.0,  l2=1e-3)),
        ("E_n400_n30", dict(n=400, noise=0.30, l2=0.0)),
        ("F_n400_n50", dict(n=400, noise=0.50, l2=0.0)),
    ]
    SEEDS = [42, 7, 123, 1, 99]

    data = {"fim_train":[], "fim_eval":[], "train_loss":[],
            "val_loss":[], "final_te":[], "cond":[]}

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
            snap, final_te = train_with_snapshot(X_tr, y_use, X_ev, y_ev, l2=cfg["l2"])
            for k in ["fim_train","fim_eval","train_loss","val_loss"]:
                data[k].append(snap[k])
            data["final_te"].append(final_te)
            data["cond"].append(cname)
        print(f"  {cname} done", flush=True)

    te = np.array(data["final_te"])
    lines = []
    def emit(s): print(s, flush=True); lines.append(s)

    emit("\n" + "="*70)
    emit("DECISIVE TEST: does FIM@ep20 predict FINAL test_acc beyond loss@ep20?")
    emit(f"6 conditions x 5 seeds = {len(te)} runs.  ep_early={EP_EARLY}, epochs={EPOCHS}")
    emit("="*70)

    emit("\n[1] Raw early predictors vs FINAL test_acc (Spearman):")
    for k in ["fim_train","fim_eval","train_loss","val_loss"]:
        rho, p = spearmanr(data[k], te)
        emit(f"    {k:<11} rho={rho:+.3f}  p={p:.2e}")

    emit("\n[2] DECISIVE — partial correlation of FIM@20 vs final_te | loss@20:")
    for fim_key in ["fim_train","fim_eval"]:
        for loss_key in ["train_loss","val_loss"]:
            r, p = partial_spearman(data[fim_key], te, data[loss_key])
            verdict = "SURVIVES" if (p < 0.05 and r < 0) else "fails"
            emit(f"    {fim_key:<10} vs final_te | {loss_key:<10}:  "
                 f"r={r:+.3f}  p={p:.2e}   [{verdict}]")

    emit("\n[3] Reverse check — does loss@20 add beyond FIM@20? (symmetry):")
    for loss_key in ["train_loss","val_loss"]:
        r, p = partial_spearman(data[loss_key], te, data["fim_eval"])
        emit(f"    {loss_key:<10} vs final_te | fim_eval :  r={r:+.3f}  p={p:.2e}")

    emit("\n[4] Per-condition means (to see the decoupling):")
    emit(f"    {'cond':<12}{'fim_tr':>8}{'fim_ev':>8}{'tr_loss':>9}{'val_loss':>9}{'final_te':>9}")
    conds = list(dict.fromkeys(data["cond"]))
    for c in conds:
        mask = [i for i,cc in enumerate(data["cond"]) if cc==c]
        row = lambda k: np.mean([data[k][i] for i in mask])
        emit(f"    {c:<12}{row('fim_train'):>8.3f}{row('fim_eval'):>8.3f}"
             f"{row('train_loss'):>9.3f}{row('val_loss'):>9.3f}{row('final_te'):>9.3f}")

    emit("\nVERDICT:")
    # decisive = fim_eval | val_loss (strongest baseline)
    r_dec, p_dec = partial_spearman(data["fim_eval"], te, data["val_loss"])
    if p_dec < 0.05 and r_dec < 0:
        emit(f"  STRONG THESIS SURVIVES: FIM@20 beats val_loss@20 as early predictor")
        emit(f"  (partial r={r_dec:+.3f}, p={p_dec:.2e}). Independent early signal is real.")
    else:
        emit(f"  STRONG THESIS DOES NOT SURVIVE: FIM@20 adds nothing beyond val_loss@20")
        emit(f"  (partial r={r_dec:+.3f}, p={p_dec:.2e}). FIM@20 is an early loss proxy.")

    with open(OUT / "fim_early_predictor.txt", "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\nSaved: {OUT/'fim_early_predictor.txt'}")


if __name__ == "__main__":
    run()
