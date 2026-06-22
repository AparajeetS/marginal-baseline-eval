"""
SCI Tracker — Structural Constraint Index (CEI v2)

Measures erank(W_l) / min(n_out, n_in) for each weight matrix.
No forward pass required. No BatchNorm contamination.
"""

import math
import numpy as np


# ------------------------------------------------------------------ #
#  Core math                                                           #
# ------------------------------------------------------------------ #

def effective_rank(M: np.ndarray) -> float:
    """
    erank(M) = exp( H(p) )  where H is Shannon entropy of
    normalized singular values p_k = σ_k / Σ σ_j.
    Range: [1, min(n_rows, n_cols)].
    """
    sv = np.linalg.svd(M.astype(np.float64), compute_uv=False)
    sv = sv[sv > 1e-10]
    if len(sv) == 0:
        return 1.0
    p  = sv / sv.sum()
    H  = -(p * np.log(p + 1e-12)).sum()
    return float(math.exp(H))


def sci_from_weight(W: np.ndarray) -> float:
    """
    Structural Constraint Index for a single weight matrix W.
    sci ∈ (1/r, 1] where r = min(n_out, n_in).
    Lower = more constrained = more generalizable (hypothesis).
    """
    r = min(W.shape[0], W.shape[1])
    return effective_rank(W) / r


def sci_spectrum(W: np.ndarray) -> dict:
    """
    Full spectral breakdown for diagnostics.
    Returns: sci, erank, rank_max, singular values, spectral entropy.
    """
    sv   = np.linalg.svd(W.astype(np.float64), compute_uv=False)
    r    = min(W.shape[0], W.shape[1])
    sv_p = sv[sv > 1e-10]
    if len(sv_p) == 0:
        return {"sci": 1.0, "erank": 1.0, "rank_max": r,
                "spectral_entropy": 0.0, "sv_max": 0.0, "sv_min": 0.0,
                "stable_rank": 0.0, "nuclear_norm": 0.0, "spectral_norm": 0.0}
    p   = sv_p / sv_p.sum()
    H   = -(p * np.log(p + 1e-12)).sum()
    er  = math.exp(H)
    return {
        "sci":             er / r,
        "erank":           er,
        "rank_max":        r,
        "spectral_entropy": float(H),
        "sv_max":          float(sv_p[0]),
        "sv_min":          float(sv_p[-1]),
        # stable rank = ||W||_F^2 / ||W||_2^2 (Rudelson & Vershynin)
        "stable_rank":     float((sv_p**2).sum() / (sv_p[0]**2 + 1e-12)),
        "nuclear_norm":    float(sv_p.sum()),
        "spectral_norm":   float(sv_p[0]),
    }


# ------------------------------------------------------------------ #
#  NumPy MLP tracker (no PyTorch needed)                              #
# ------------------------------------------------------------------ #

class NumpySCITracker:
    """
    Tracks SCI across all weight matrices of a numpy MLP.

    Usage:
        tracker = NumpySCITracker(model)
        sci_vals, net_sci = tracker.compute()
    """

    def __init__(self, model):
        self.model = model   # expects model.W = list of np.ndarray

    def compute(self) -> tuple[list[float], float]:
        """Returns (per_layer_sci, network_mean_sci)."""
        vals = [sci_from_weight(W) for W in self.model.W]
        return vals, float(np.mean(vals))

    def compute_full(self) -> list[dict]:
        """Returns full spectral breakdown per layer."""
        return [sci_spectrum(W) for W in self.model.W]


# ------------------------------------------------------------------ #
#  Optional PyTorch wrapper                                           #
# ------------------------------------------------------------------ #

def pytorch_sci(model, layer_types=None) -> dict:
    """
    Compute SCI for all weight matrices in a PyTorch model.

    Args:
        model: nn.Module
        layer_types: tuple of types to include (default: Linear + Conv2d)

    Returns:
        dict mapping layer_name -> sci_spectrum dict, plus "network_sci" mean.
    """
    try:
        import torch
        import torch.nn as nn
    except ImportError:
        raise ImportError("PyTorch not available; use NumpySCITracker for numpy models.")

    if layer_types is None:
        layer_types = (nn.Linear, nn.Conv2d)

    results = {}
    sci_list = []

    for name, module in model.named_modules():
        if isinstance(module, layer_types):
            W = module.weight.detach().cpu().numpy()
            if W.ndim > 2:
                # Conv2d: (C_out, C_in, kH, kW) → reshape to (C_out, C_in*kH*kW)
                W = W.reshape(W.shape[0], -1)
            spec = sci_spectrum(W)
            results[name] = spec
            sci_list.append(spec["sci"])

    results["network_sci"] = float(np.mean(sci_list)) if sci_list else float("nan")
    return results
