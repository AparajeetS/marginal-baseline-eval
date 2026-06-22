"""
CEI v2 — Review follow-up experiments.

Addresses four issues surfaced in the critical review, all on the fast
digits MLP (training-data FIM, consistent with the validated experiments):

  ISSUE 3  Fixed-N n_train probe — remove the erank/N normalization confound
           (original used N=40 for n=40 but N=100 elsewhere). Here N=40 for ALL.

  ISSUE 4  Per-layer FIM_norm — recover v1's layer-localization. erank of each
           weight-matrix gradient block separately.

  ISSUE 6  Loss baseline — does FIM_norm predict test_acc BEYOND the loss value
           itself? (gradients scale with loss, so this is the key confound.)

  NEW FIX  Unit-normalized gradients — normalize each per-sample gradient to
           unit norm BEFORE the Gram matrix, isolating DIRECTIONAL diversity
           from magnitude. Motivated by the CIFAR condition-C collapse, where a
           fully-memorized model has vanishing gradients -> erank collapses ->
           noise undetectable. Unit-norm should be immune to that.

Outputs: fim_review_followup.txt
"""

import sys, math
import numpy as np
from pathlib import Path
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from scipy.stats import spearmanr, pearsonr

sys.path.insert(0, str(Path(__file__).parent))
from sci_tracker import effective_rank
from fim_full_study import MLP, BATCH

SEED = 42
OUT  = Path(__file__).parent
np.random.seed(SEED)

# MLP layer boundaries (WIDTHS = [64,128,64,32,10] -> 4 weight matrices)
LAYER_SIZES = [64*128, 128*64, 64*32, 32*10]   # [8192, 8192, 2048, 320]
LAYER_BOUNDS = np.cumsum([0] + LAYER_SIZES)


def all_fim_variants(model, X, y, n_fix=40):
    """Compute every FIM variant from ONE shared set of per-sample gradients.
       N is FIXED at n_fix for all conditions (removes the N-normalization confound)."""
    n     = len(X)
    n_use = min(n_fix, n)
    idx   = np.random.choice(n, n_use, replace=False)
    G     = np.array([model._grad_single(X[k], y[k]) for k in idx])   # (n_use, d)

    # --- raw FIM_norm (current metric) ---
    F_raw = (G @ G.T) / n_use
    fim_raw = effective_rank(F_raw) / n_use

    # --- unit-normalized gradients (directional diversity only) ---
    norms = np.linalg.norm(G, axis=1, keepdims=True)
    Gu    = G / (norms + 1e-12)
    F_unit = (Gu @ Gu.T) / n_use
    fim_unit = effective_rank(F_unit) / n_use

    # --- per-layer FIM_norm (raw) ---
    per_layer = []
    for li in range(len(LAYER_SIZES)):
        a, b = LAYER_BOUNDS[li], LAYER_BOUNDS[li+1]
        Gl = G[:, a:b]
        Fl = (Gl @ Gl.T) / n_use
        per_layer.append(effective_rank(Fl) / n_use)

    # --- loss baseline (mean per-sample loss on the same data) ---
    loss = model._loss(X, y)

    return dict(fim_raw=fim_raw, fim_unit=fim_unit,
                per_layer=per_layer, loss=loss)


def train(X_tr, y_tr, l2=0.0, epochs=200, lr=0.005):
    model = MLP(l2=l2)
    n = len(X_tr)
    for _ in range(epochs):
        idx = np.random.permutation(n)
        for s in range(0, n, BATCH):
            b = idx[s:s+BATCH]; model.step(X_tr[b], y_tr[b], lr)
    return model


def partial_spearman(x, y, z):
    """Spearman partial correlation of x,y controlling for z (rank-based)."""
    from scipy.stats import rankdata
    rx, ry, rz = rankdata(x), rankdata(y), rankdata(z)
    def resid(a, b):
        b1 = np.vstack([b, np.ones_like(b)]).T
        coef, *_ = np.linalg.lstsq(b1, a, rcond=None)
        return a - b1 @ coef
    ex, ey = resid(rx, rz), resid(ry, rz)
    r, p = pearsonr(ex, ey)
    return r, p


def run():
    X, y = load_digits(return_X_y=True)
    X    = StandardScaler().fit_transform(X)
    X_ev, X_pool, y_ev, y_pool = train_test_split(
        X, y, test_size=len(X)-200, random_state=SEED)

    SEEDS  = [42, 7, 123, 1, 99]      # 5 seeds (Issue 8: more power)
    NOISE  = [0.0, 0.15, 0.30, 0.50]
    NTRAIN = [40, 200, 400, 800]

    # storage
    res = {k: {"fim_raw":[], "fim_unit":[], "loss":[], "te":[],
               "L0":[], "L1":[], "L2":[], "L3":[]} for k in ["noise","ntrain"]}

    print("=== NOISE probe (n=400 fixed, N_FIM=40 fixed) ===", flush=True)
    for noise in NOISE:
        for seed in SEEDS:
            np.random.seed(seed)
            X_tr, _, y_tr, _ = train_test_split(
                X_pool, y_pool, train_size=400, random_state=seed)
            y_use = y_tr.copy()
            if noise > 0:
                nf = int(noise*len(y_tr)); fi = np.random.choice(len(y_tr), nf, replace=False)
                y_use[fi] = np.random.randint(0, 10, nf)
            model = train(X_tr, y_use)
            m = all_fim_variants(model, X_tr, y_use, n_fix=40)
            te = model.acc(X_ev, y_ev)
            res["noise"]["fim_raw"].append(m["fim_raw"])
            res["noise"]["fim_unit"].append(m["fim_unit"])
            res["noise"]["loss"].append(m["loss"])
            res["noise"]["te"].append(te)
            for li in range(4): res["noise"][f"L{li}"].append(m["per_layer"][li])
        print(f"  noise={noise:.0%} done", flush=True)

    print("=== N_TRAIN probe (noise=0, N_FIM=40 FIXED for all n) ===", flush=True)
    for n in NTRAIN:
        for seed in SEEDS:
            np.random.seed(seed)
            X_tr, _, y_tr, _ = train_test_split(
                X_pool, y_pool, train_size=n, random_state=seed)
            model = train(X_tr, y_tr)
            m = all_fim_variants(model, X_tr, y_tr, n_fix=40)   # N=40 for ALL n
            te = model.acc(X_ev, y_ev)
            res["ntrain"]["fim_raw"].append(m["fim_raw"])
            res["ntrain"]["fim_unit"].append(m["fim_unit"])
            res["ntrain"]["loss"].append(m["loss"])
            res["ntrain"]["te"].append(te)
            for li in range(4): res["ntrain"][f"L{li}"].append(m["per_layer"][li])
        print(f"  n={n} done", flush=True)

    # ---- analysis ----
    lines = []
    def emit(s): print(s, flush=True); lines.append(s)

    emit("\n" + "="*70)
    emit("REVIEW FOLLOW-UP RESULTS (5 seeds, training-data FIM, N_FIM=40 fixed)")
    emit("="*70)

    for probe in ["noise", "ntrain"]:
        d = res[probe]
        te = d["te"]
        emit(f"\n--- {probe.upper()} probe (n={len(te)}) ---")
        for metric in ["fim_raw", "fim_unit", "loss"]:
            rho, p = spearmanr(d[metric], te)
            emit(f"  {metric:<10} vs test_acc:  rho={rho:+.3f}  p={p:.2e}")

        # ISSUE 6: FIM beyond loss
        r_raw, p_raw   = partial_spearman(d["fim_raw"],  te, d["loss"])
        r_unit, p_unit = partial_spearman(d["fim_unit"], te, d["loss"])
        emit(f"  [partial] fim_raw  vs te | loss:  r={r_raw:+.3f}  p={p_raw:.2e}")
        emit(f"  [partial] fim_unit vs te | loss:  r={r_unit:+.3f}  p={p_unit:.2e}")

        # ISSUE 4: per-layer
        emit("  per-layer FIM_norm (raw) vs test_acc:")
        for li in range(4):
            rho, p = spearmanr(d[f"L{li}"], te)
            emit(f"    layer{li} (size {LAYER_SIZES[li]:5d}): rho={rho:+.3f}  p={p:.2e}")

    emit("\nINTERPRETATION GUIDE:")
    emit("  - fim_raw should still pass both probes (validates fixed-N: Issue 3).")
    emit("  - if fim_unit >= fim_raw on noise probe, unit-norm is the better metric.")
    emit("  - if partial r (fim|loss) stays significant, FIM beats loss (Issue 6).")
    emit("  - per-layer: which layer carries the signal (Issue 4 / neural collapse).")

    with open(OUT / "fim_review_followup.txt", "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\nSaved: {OUT/'fim_review_followup.txt'}")


if __name__ == "__main__":
    run()
