from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import math
import os
import random
import subprocess
import sys
import time
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path

if sys.platform != "win32" and Path("/kaggle/working").exists():
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--quiet",
            "--force-reinstall",
            "--no-cache-dir",
            "torch==2.4.1",
            "torchvision==0.19.1",
            "--index-url",
            "https://download.pytorch.org/whl/cu118",
        ]
    )

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset, Subset, TensorDataset


OUT_DIR = Path.cwd()
CIFAR_MEAN = (0.4914, 0.4822, 0.4465)
CIFAR_STD = (0.2023, 0.1994, 0.2010)
SVHN_MEAN = (0.4377, 0.4438, 0.4728)
SVHN_STD = (0.1980, 0.2010, 0.1970)
DEFAULT_DATASET = Path(__file__).stem.rsplit("_", 1)[-1]
SPLIT_SEED = 20260823


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def device_name() -> str:
    return "cuda" if torch.cuda.is_available() else "cpu"


def stable_corruption_seed(run_id: str) -> int:
    return int(hashlib.sha256(f"corruption:{run_id}".encode()).hexdigest()[:8], 16)


class SimpleCNN(nn.Module):
    def __init__(self, dropout: float = 0.0, num_classes: int = 10) -> None:
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 64, 3, padding=1, bias=False),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            nn.Dropout(dropout),
            nn.Conv2d(64, 128, 3, padding=1, bias=False),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            nn.Dropout(dropout),
            nn.Conv2d(128, 256, 3, padding=1, bias=False),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d((1, 1)),
            nn.Flatten(),
        )
        self.fc = nn.Linear(256, num_classes)

    def forward(self, x: torch.Tensor, return_features: bool = False):
        z = self.features(x)
        logits = self.fc(z)
        return (logits, z) if return_features else logits


class BasicBlock(nn.Module):
    def __init__(self, in_planes: int, planes: int, stride: int = 1, dropout: float = 0.0) -> None:
        super().__init__()
        self.conv1 = nn.Conv2d(in_planes, planes, 3, stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(planes)
        self.conv2 = nn.Conv2d(planes, planes, 3, stride=1, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(planes)
        self.drop = nn.Dropout2d(dropout)
        self.shortcut = nn.Identity()
        if stride != 1 or in_planes != planes:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_planes, planes, 1, stride=stride, bias=False),
                nn.BatchNorm2d(planes),
            )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out = F.relu(self.bn1(self.conv1(x)))
        out = self.drop(out)
        out = self.bn2(self.conv2(out))
        return F.relu(out + self.shortcut(x))


class CifarResNet(nn.Module):
    def __init__(self, width: int = 32, dropout: float = 0.0, num_classes: int = 10) -> None:
        super().__init__()
        self.in_planes = width
        self.conv1 = nn.Conv2d(3, width, 3, stride=1, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(width)
        self.layer1 = self._make_layer(width, 2, stride=1, dropout=dropout)
        self.layer2 = self._make_layer(width * 2, 2, stride=2, dropout=dropout)
        self.layer3 = self._make_layer(width * 4, 2, stride=2, dropout=dropout)
        self.fc = nn.Linear(width * 4, num_classes)

    def _make_layer(self, planes: int, blocks: int, stride: int, dropout: float) -> nn.Sequential:
        strides = [stride] + [1] * (blocks - 1)
        layers = []
        for s in strides:
            layers.append(BasicBlock(self.in_planes, planes, s, dropout))
            self.in_planes = planes
        return nn.Sequential(*layers)

    def forward(self, x: torch.Tensor, return_features: bool = False):
        out = F.relu(self.bn1(self.conv1(x)))
        out = self.layer1(out)
        out = self.layer2(out)
        out = self.layer3(out)
        out = F.avg_pool2d(out, out.size(3))
        z = torch.flatten(out, 1)
        logits = self.fc(z)
        return (logits, z) if return_features else logits


class TinyViT(nn.Module):
    def __init__(self, dropout: float = 0.0, dim: int = 128, depth: int = 4, heads: int = 4) -> None:
        super().__init__()
        self.patch = nn.Conv2d(3, dim, kernel_size=4, stride=4)
        self.cls = nn.Parameter(torch.zeros(1, 1, dim))
        self.pos = nn.Parameter(torch.randn(1, 65, dim) * 0.02)
        enc_layer = nn.TransformerEncoderLayer(
            d_model=dim,
            nhead=heads,
            dim_feedforward=dim * 4,
            dropout=dropout,
            batch_first=True,
            activation="gelu",
            norm_first=True,
        )
        self.encoder = nn.TransformerEncoder(enc_layer, num_layers=depth)
        self.norm = nn.LayerNorm(dim)
        self.fc = nn.Linear(dim, 10)

    def forward(self, x: torch.Tensor, return_features: bool = False):
        z = self.patch(x).flatten(2).transpose(1, 2)
        cls = self.cls.expand(z.size(0), -1, -1)
        z = torch.cat([cls, z], dim=1) + self.pos[:, : z.size(1) + 1]
        z = self.encoder(z)
        feat = self.norm(z[:, 0])
        logits = self.fc(feat)
        return (logits, feat) if return_features else logits


class CharDataset(Dataset):
    def __init__(self, ids: torch.Tensor, block_size: int) -> None:
        self.ids = ids.long()
        self.block_size = block_size

    def __len__(self) -> int:
        return max(0, len(self.ids) - self.block_size - 1)

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, torch.Tensor]:
        x = self.ids[idx : idx + self.block_size]
        y = self.ids[idx + 1 : idx + self.block_size + 1]
        return x, y


class TinyCharTransformer(nn.Module):
    def __init__(self, vocab_size: int, block_size: int, dropout: float = 0.0, dim: int = 128) -> None:
        super().__init__()
        self.block_size = block_size
        self.token_emb = nn.Embedding(vocab_size, dim)
        self.pos_emb = nn.Embedding(block_size, dim)
        enc_layer = nn.TransformerEncoderLayer(
            d_model=dim,
            nhead=4,
            dim_feedforward=dim * 4,
            dropout=dropout,
            batch_first=True,
            activation="gelu",
            norm_first=True,
        )
        self.encoder = nn.TransformerEncoder(enc_layer, num_layers=3)
        self.norm = nn.LayerNorm(dim)
        self.head = nn.Linear(dim, vocab_size)

    def forward(self, x: torch.Tensor, return_features: bool = False):
        positions = torch.arange(x.size(1), device=x.device)
        z = self.token_emb(x) + self.pos_emb(positions)[None, :, :]
        z = self.encoder(z)
        feat = self.norm(z)
        logits = self.head(feat)
        pooled = feat.mean(dim=1)
        return (logits, pooled) if return_features else logits


def make_model(
    arch: str,
    dropout: float,
    vocab_size: int | None = None,
    block_size: int = 96,
    num_classes: int = 10,
) -> nn.Module:
    if arch == "cnn":
        return SimpleCNN(dropout=dropout, num_classes=num_classes)
    if arch == "resnet":
        return CifarResNet(width=32, dropout=dropout, num_classes=num_classes)
    if arch == "wide_resnet":
        return CifarResNet(width=48, dropout=dropout, num_classes=num_classes)
    if arch == "vit":
        return TinyViT(dropout=dropout)
    if arch == "char_transformer":
        if vocab_size is None:
            raise ValueError("vocab_size is required for char_transformer")
        return TinyCharTransformer(vocab_size=vocab_size, block_size=block_size, dropout=dropout)
    raise ValueError(f"Unknown architecture: {arch}")


def _split_indices(
    train_population: int,
    test_population: int,
    n_train: int,
    n_val: int,
    n_test: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(SPLIT_SEED)
    train_order = rng.permutation(train_population)
    test_order = rng.permutation(test_population)
    return (
        train_order[:n_train],
        train_order[n_train : n_train + n_val],
        test_order[:n_test],
    )


def dataset_spec(dataset_name: str) -> dict[str, object]:
    if dataset_name == "cifar10":
        return {"classes": 10, "train_population": 50_000, "test_population": 10_000, "mean": CIFAR_MEAN, "std": CIFAR_STD}
    if dataset_name == "cifar100":
        return {"classes": 100, "train_population": 50_000, "test_population": 10_000, "mean": CIFAR_MEAN, "std": CIFAR_STD}
    if dataset_name == "svhn":
        return {"classes": 10, "train_population": 73_257, "test_population": 26_032, "mean": SVHN_MEAN, "std": SVHN_STD}
    raise ValueError(f"unsupported dataset: {dataset_name}")


def load_image_data(
    dataset_name: str,
    batch_size: int,
    n_train: int,
    n_val: int,
    n_test: int,
    seed: int,
):
    import torchvision.transforms as T
    import torchvision.datasets as datasets

    spec = dataset_spec(dataset_name)
    train_idx, val_idx, test_idx = _split_indices(
        int(spec["train_population"]), int(spec["test_population"]), n_train, n_val, n_test
    )
    transform = T.Compose([T.ToTensor(), T.Normalize(spec["mean"], spec["std"])])
    root = "/kaggle/working/data" if Path("/kaggle/working").exists() else str(OUT_DIR / "data")
    if dataset_name == "cifar10":
        train_ds = datasets.CIFAR10(root, train=True, download=True, transform=transform)
        test_ds = datasets.CIFAR10(root, train=False, download=True, transform=transform)
    elif dataset_name == "cifar100":
        train_ds = datasets.CIFAR100(root, train=True, download=True, transform=transform)
        test_ds = datasets.CIFAR100(root, train=False, download=True, transform=transform)
    else:
        train_ds = datasets.SVHN(root, split="train", download=True, transform=transform)
        test_ds = datasets.SVHN(root, split="test", download=True, transform=transform)
    train_subset = Subset(train_ds, train_idx)
    val_subset = Subset(train_ds, val_idx)
    test_subset = Subset(test_ds, test_idx)

    train_generator = torch.Generator().manual_seed(seed)
    train_loader = DataLoader(
        train_subset,
        batch_size=batch_size,
        shuffle=True,
        generator=train_generator,
        num_workers=2,
        pin_memory=torch.cuda.is_available(),
    )
    val_loader = DataLoader(val_subset, batch_size=batch_size, shuffle=False, num_workers=2, pin_memory=torch.cuda.is_available())
    test_loader = DataLoader(test_subset, batch_size=batch_size, shuffle=False, num_workers=2, pin_memory=torch.cuda.is_available())
    metric_loaders = [
        DataLoader(
            train_subset,
            batch_size=batch_size,
            shuffle=True,
            generator=torch.Generator().manual_seed(SPLIT_SEED + offset),
            num_workers=2,
            pin_memory=torch.cuda.is_available(),
        )
        for offset in (300, 301, 302)
    ]
    return train_loader, val_loader, test_loader, metric_loaders


def load_cifar_pickles(cifar_dir: Path):
    import pickle

    xs, ys = [], []
    for i in range(1, 6):
        with (cifar_dir / f"data_batch_{i}").open("rb") as handle:
            batch = pickle.load(handle, encoding="latin1")
        xs.append(batch["data"])
        ys.extend(batch["labels"])
    with (cifar_dir / "test_batch").open("rb") as handle:
        test = pickle.load(handle, encoding="latin1")
    train_x = np.concatenate(xs).reshape(-1, 3, 32, 32).astype("float32") / 255.0
    test_x = test["data"].reshape(-1, 3, 32, 32).astype("float32") / 255.0
    mean = np.asarray(CIFAR_MEAN, dtype="float32").reshape(1, 3, 1, 1)
    std = np.asarray(CIFAR_STD, dtype="float32").reshape(1, 3, 1, 1)
    return (train_x - mean) / std, np.asarray(ys, dtype="int64"), (test_x - mean) / std, np.asarray(test["labels"], dtype="int64")


def load_char_data(batch_size: int, n_train: int, n_test: int, seed: int, block_size: int):
    path = OUT_DIR / "tinyshakespeare.txt"
    if not path.exists():
        try:
            urllib.request.urlretrieve(
                "https://raw.githubusercontent.com/karpathy/char-rnn/master/data/tinyshakespeare/input.txt",
                path,
            )
        except Exception:
            fallback = ("To be, or not to be, that is the question.\n" * 5000)
            path.write_text(fallback, encoding="utf-8")
    text = path.read_text(encoding="utf-8", errors="ignore")
    chars = sorted(set(text))
    stoi = {ch: i for i, ch in enumerate(chars)}
    ids = torch.tensor([stoi[ch] for ch in text], dtype=torch.long)
    split = int(0.9 * len(ids))
    train_ids, test_ids = ids[:split], ids[split:]
    train_ds = CharDataset(train_ids[: min(len(train_ids), n_train + block_size + 1)], block_size)
    test_ds = CharDataset(test_ids[: min(len(test_ids), n_test + block_size + 1)], block_size)
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=0)
    eval_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False, num_workers=0)
    metric_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=False, num_workers=0)
    return train_loader, eval_loader, metric_loader, len(chars)


def loss_for_logits(logits: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
    if logits.ndim == 3:
        return F.cross_entropy(logits.reshape(-1, logits.size(-1)), y.reshape(-1))
    return F.cross_entropy(logits, y)


def flatten_logits_targets(logits: torch.Tensor, y: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    if logits.ndim == 3:
        return logits.reshape(-1, logits.size(-1)), y.reshape(-1)
    return logits, y


def collect_batch(loader: DataLoader, n: int, device: str) -> tuple[torch.Tensor, torch.Tensor]:
    xs, ys = [], []
    total = 0
    for x, y in loader:
        xs.append(x)
        ys.append(y)
        total += len(x)
        if total >= n:
            break
    x = torch.cat(xs)[:n].to(device)
    y = torch.cat(ys)[:n].to(device)
    return x, y


def evaluate(model: nn.Module, loader: DataLoader, device: str, max_batches: int | None = None) -> dict[str, float]:
    model.eval()
    total_loss, total_correct, total_seen = 0.0, 0, 0
    with torch.no_grad():
        for batch_i, (x, y) in enumerate(loader):
            if max_batches is not None and batch_i >= max_batches:
                break
            x, y = x.to(device), y.to(device)
            logits = model(x)
            flat_logits, flat_y = flatten_logits_targets(logits, y)
            loss = F.cross_entropy(flat_logits, flat_y, reduction="sum")
            total_loss += float(loss)
            total_correct += int((flat_logits.argmax(1) == flat_y).sum())
            total_seen += int(flat_y.numel())
    return {"loss": total_loss / max(1, total_seen), "acc": total_correct / max(1, total_seen)}


def evaluate_target_suite(
    model: nn.Module,
    loader: DataLoader,
    device: str,
    corruption_seed: int,
) -> dict[str, float]:
    model.eval()
    names = ("clean", "gaussian_noise", "blur", "low_contrast")
    totals = {name: {"loss": 0.0, "correct": 0, "seen": 0} for name in names}
    clean_probabilities: list[torch.Tensor] = []
    clean_targets: list[torch.Tensor] = []
    generator = torch.Generator(device=device).manual_seed(corruption_seed)
    with torch.no_grad():
        for x, y in loader:
            x, y = x.to(device), y.to(device)
            variants = {
                "clean": x,
                "gaussian_noise": x + 0.20 * torch.randn(x.shape, generator=generator, device=device),
                "blur": F.avg_pool2d(x, kernel_size=3, stride=1, padding=1),
                "low_contrast": 0.55 * x,
            }
            for name, inputs in variants.items():
                logits = model(inputs)
                loss = F.cross_entropy(logits, y, reduction="sum")
                totals[name]["loss"] += float(loss)
                totals[name]["correct"] += int((logits.argmax(1) == y).sum())
                totals[name]["seen"] += int(y.numel())
                if name == "clean":
                    clean_probabilities.append(logits.softmax(dim=1).cpu())
                    clean_targets.append(y.cpu())
    output: dict[str, float] = {}
    for name in names:
        seen = max(1, totals[name]["seen"])
        output[f"{name}_test_loss"] = totals[name]["loss"] / seen
        output[f"{name}_test_acc"] = totals[name]["correct"] / seen
    output["corruption_mean_loss"] = float(np.mean([output[f"{name}_test_loss"] for name in names[1:]]))
    output["corruption_mean_acc"] = float(np.mean([output[f"{name}_test_acc"] for name in names[1:]]))
    probabilities = torch.cat(clean_probabilities)
    targets = torch.cat(clean_targets)
    one_hot = F.one_hot(targets, num_classes=probabilities.size(1)).float()
    output["clean_test_brier"] = float(((probabilities - one_hot) ** 2).sum(dim=1).mean())
    confidence, prediction = probabilities.max(dim=1)
    correct = prediction.eq(targets).float()
    ece = 0.0
    edges = torch.linspace(0.0, 1.0, 16)
    for index in range(15):
        selected = (confidence > edges[index]) & (confidence <= edges[index + 1])
        if selected.any():
            ece += float(selected.float().mean() * (confidence[selected].mean() - correct[selected].mean()).abs())
    output["clean_test_ece"] = ece
    return output


def effective_rank_from_eigs(eigs: torch.Tensor | np.ndarray) -> float:
    vals = torch.as_tensor(eigs, dtype=torch.float64).clamp_min(0)
    total = vals.sum()
    if float(total) <= 0:
        return 0.0
    probs = vals / total
    probs = probs[probs > 0]
    return float(torch.exp(-(probs * torch.log(probs)).sum()))


def feature_metrics(model: nn.Module, x: torch.Tensor) -> dict[str, float]:
    model.eval()
    with torch.no_grad():
        _, z = model(x, return_features=True)
        z = z.detach().float()
        zc = z - z.mean(dim=0, keepdim=True)
        gram = zc @ zc.T / max(1, zc.size(1))
        eigs = torch.linalg.eigvalsh(gram.cpu()).clamp_min(0)
        norms = z.norm(dim=1)
        zn = F.normalize(z, dim=1)
        sim = zn @ zn.T
        off_diag = sim[~torch.eye(sim.size(0), dtype=torch.bool, device=sim.device)]
    return {
        "feature_erank": effective_rank_from_eigs(eigs),
        "feature_erank_norm": effective_rank_from_eigs(eigs) / max(1, len(x)),
        "feature_norm_mean": float(norms.mean().cpu()),
        "feature_cosine_mean": float(off_diag.mean().cpu()) if off_diag.numel() else 0.0,
    }


def prediction_metrics(model: nn.Module, x: torch.Tensor, y: torch.Tensor, n_bins: int = 15) -> dict[str, float]:
    model.eval()
    with torch.no_grad():
        logits = model(x)
        flat_logits, flat_y = flatten_logits_targets(logits, y)
        probs = flat_logits.softmax(dim=1)
        conf, pred = probs.max(dim=1)
        correct = (pred == flat_y).float()
        entropy = -(probs.clamp_min(1e-12) * probs.clamp_min(1e-12).log()).sum(dim=1)
        top2 = probs.topk(k=min(2, probs.size(1)), dim=1).values
        margin = top2[:, 0] - (top2[:, 1] if top2.size(1) > 1 else 0)
        one_hot = F.one_hot(flat_y, num_classes=probs.size(1)).float()
        brier = ((probs - one_hot) ** 2).sum(dim=1).mean()
        logit_norm = flat_logits.norm(dim=1).mean()
        ece = torch.tensor(0.0, device=flat_logits.device)
        edges = torch.linspace(0, 1, n_bins + 1, device=flat_logits.device)
        for i in range(n_bins):
            mask = (conf > edges[i]) & (conf <= edges[i + 1])
            if mask.any():
                ece += mask.float().mean() * (conf[mask].mean() - correct[mask].mean()).abs()
    return {
        "confidence_mean": float(conf.mean().cpu()),
        "entropy_mean": float(entropy.mean().cpu()),
        "margin_mean": float(margin.mean().cpu()),
        "brier": float(brier.cpu()),
        "ece": float(ece.cpu()),
        "logit_norm_mean": float(logit_norm.cpu()),
        "metric_batch_acc": float(correct.mean().cpu()),
        "metric_batch_loss": float(F.cross_entropy(flat_logits, flat_y).cpu()),
    }


def parameter_vector(model: nn.Module) -> torch.Tensor:
    return torch.cat([p.detach().flatten().cpu().float() for p in model.parameters()])


def parameter_metrics(model: nn.Module, init_vec: torch.Tensor) -> dict[str, float]:
    vec = parameter_vector(model)
    delta = vec - init_vec
    weight_l2 = float(vec.norm())
    return {
        "weight_l2": weight_l2,
        "weight_l1": float(vec.abs().sum()),
        "weight_linf": float(vec.abs().max()),
        "weight_rms": float(torch.sqrt((vec.square()).mean())),
        "distance_from_init_l2": float(delta.norm()),
        "relative_distance_from_init": float(delta.norm() / (init_vec.norm() + 1e-12)),
        "update_to_weight_ratio": float(delta.norm() / (vec.norm() + 1e-12)),
    }


def grad_vector(model: nn.Module, loss: torch.Tensor, create_graph: bool = False) -> torch.Tensor:
    grads = torch.autograd.grad(loss, [p for p in model.parameters() if p.requires_grad], create_graph=create_graph, retain_graph=create_graph, allow_unused=True)
    flat = [g.flatten() for g in grads if g is not None]
    return torch.cat(flat) if flat else torch.zeros(1, device=loss.device)


def gradient_metrics(model: nn.Module, x: torch.Tensor, y: torch.Tensor) -> dict[str, float]:
    model.eval()
    logits = model(x)
    loss = loss_for_logits(logits, y)
    g = grad_vector(model, loss, create_graph=False).detach()
    return {
        "grad_norm": float(g.norm().cpu()),
        "grad_l1": float(g.abs().sum().cpu()),
        "grad_linf": float(g.abs().max().cpu()),
        "grad_mean_abs": float(g.abs().mean().cpu()),
    }


def fisher_metrics(model: nn.Module, x: torch.Tensor, y: torch.Tensor) -> dict[str, float]:
    model.eval()
    rows = []
    losses = []
    for i in range(len(x)):
        model.zero_grad(set_to_none=True)
        logits = model(x[i : i + 1])
        yi = y[i : i + 1]
        loss = loss_for_logits(logits, yi)
        loss.backward()
        losses.append(float(loss.detach().cpu()))
        rows.append(torch.cat([p.grad.detach().flatten().cpu().float() for p in model.parameters() if p.grad is not None]))
    if not rows:
        return {}
    G = torch.stack(rows)
    norms_sq = G.square().sum(dim=1)
    dual = (G @ G.T) / len(rows)
    eigs = torch.linalg.eigvalsh(dual).clamp_min(0)
    trace = float(eigs.sum())
    spectral = float(eigs.max()) if eigs.numel() else 0.0
    erank = effective_rank_from_eigs(eigs)
    stable_rank = trace / (spectral + 1e-12)
    condition = float(spectral / (eigs[eigs > 1e-12].min() + 1e-12)) if (eigs > 1e-12).any() else math.nan
    mean_g = G.mean(dim=0)
    per_sample_var = ((G - mean_g) ** 2).sum(dim=1).mean()
    noise_scale = float(per_sample_var / (mean_g.square().sum() + 1e-12))
    p = eigs / (eigs.sum() + 1e-12)
    entropy = float(-(p[p > 0] * p[p > 0].log()).sum())
    norms = norms_sq.sqrt().clamp_min(1e-12)
    unit_g = G / norms[:, None]
    unit_eigs = torch.linalg.eigvalsh((unit_g @ unit_g.T) / len(rows)).clamp_min(0)
    unit_erank = effective_rank_from_eigs(unit_eigs)
    loss_vec = torch.tensor(losses, dtype=G.dtype).clamp_min(1e-6)
    loss_scaled_g = G / loss_vec[:, None]
    loss_scaled_eigs = torch.linalg.eigvalsh((loss_scaled_g @ loss_scaled_g.T) / len(rows)).clamp_min(0)
    loss_scaled_erank = effective_rank_from_eigs(loss_scaled_eigs)
    energy = norms_sq.clamp_min(0)
    energy_p = energy / (energy.sum() + 1e-12)
    energy_entropy = float(-(energy_p[energy_p > 0] * energy_p[energy_p > 0].log()).sum())
    sorted_energy = torch.sort(energy).values
    n_energy = len(sorted_energy)
    gini_num = (2 * torch.arange(1, n_energy + 1, dtype=sorted_energy.dtype) - n_energy - 1) * sorted_energy
    energy_gini = float(gini_num.sum() / (n_energy * sorted_energy.sum() + 1e-12))
    if len(rows) >= 3 and float(loss_vec.std(unbiased=False)) > 1e-12 and float(norms.std(unbiased=False)) > 1e-12:
        grad_loss_corr = float(torch.corrcoef(torch.stack([loss_vec.log(), norms.log()]))[0, 1])
    else:
        grad_loss_corr = math.nan
    return {
        "fisher_trace": trace,
        "fisher_spectral": spectral,
        "fisher_stable_rank": float(stable_rank),
        "fisher_entropy": entropy,
        "fim_erank": erank,
        "fim_norm": erank / len(rows),
        "fim_unit_erank": unit_erank,
        "fim_unit_norm": unit_erank / len(rows),
        "fim_loss_scaled_erank": loss_scaled_erank,
        "fim_loss_scaled_norm": loss_scaled_erank / len(rows),
        "fisher_condition": condition,
        "grad_noise_scale": noise_scale,
        "gradient_energy_entropy": energy_entropy,
        "gradient_energy_gini": energy_gini,
        "grad_loss_logcorr": grad_loss_corr,
        "per_sample_grad_norm_mean": float(norms_sq.sqrt().mean()),
        "per_sample_grad_norm_std": float(norms_sq.sqrt().std(unbiased=False)),
    }


def sharpness_metric(model: nn.Module, x: torch.Tensor, y: torch.Tensor, rho: float, adaptive: bool = False) -> float:
    backup = copy.deepcopy(model.state_dict())
    model.eval()
    logits = model(x)
    loss0 = loss_for_logits(logits, y)
    model.zero_grad(set_to_none=True)
    loss0.backward()
    if adaptive:
        pieces = [(p.grad * p.detach().abs()).norm() for p in model.parameters() if p.grad is not None]
    else:
        pieces = [p.grad.norm() for p in model.parameters() if p.grad is not None]
    norm = torch.norm(torch.stack(pieces)) if pieces else torch.tensor(0.0, device=x.device)
    if float(norm) <= 1e-12:
        model.load_state_dict(backup)
        return 0.0
    scale = rho / norm
    with torch.no_grad():
        for p in model.parameters():
            if p.grad is None:
                continue
            if adaptive:
                p.add_(p.grad * p.detach().abs().square() * scale)
            else:
                p.add_(p.grad * scale)
    with torch.no_grad():
        loss1 = loss_for_logits(model(x), y)
    model.load_state_dict(backup)
    return float((loss1 - loss0).detach().cpu())


def hessian_metrics(model: nn.Module, x: torch.Tensor, y: torch.Tensor, probes: int = 2, power_steps: int = 4) -> dict[str, float]:
    params = [p for p in model.parameters() if p.requires_grad]
    model.eval()
    logits = model(x)
    loss = loss_for_logits(logits, y)
    grads = torch.autograd.grad(loss, params, create_graph=True, retain_graph=True)
    flat_grad = torch.cat([g.contiguous().view(-1) for g in grads])
    n = flat_grad.numel()
    trace_estimates = []
    for _ in range(probes):
        v = torch.randint(0, 2, (n,), device=x.device, dtype=flat_grad.dtype) * 2 - 1
        hv = torch.autograd.grad((flat_grad * v).sum(), params, retain_graph=True, allow_unused=True)
        flat_hv = torch.cat([h.contiguous().view(-1) for h in hv if h is not None])
        trace_estimates.append(float((v[: flat_hv.numel()] * flat_hv).sum().detach().cpu()))
    v = F.normalize(torch.randn(n, device=x.device), dim=0)
    eig = torch.tensor(0.0, device=x.device)
    for _ in range(power_steps):
        hv = torch.autograd.grad((flat_grad * v).sum(), params, retain_graph=True, allow_unused=True)
        flat_hv = torch.cat([h.contiguous().view(-1) for h in hv if h is not None])
        eig = (v[: flat_hv.numel()] * flat_hv).sum()
        v = F.normalize(flat_hv.detach(), dim=0)
    return {
        "hessian_trace_hutchinson": float(np.mean(trace_estimates)),
        "hessian_top_eig_power": float(eig.detach().cpu()),
    }


def all_metrics(model: nn.Module, init_vec: torch.Tensor, x: torch.Tensor, y: torch.Tensor, heavy: bool = True) -> dict[str, float]:
    out: dict[str, float] = {}
    out.update(prediction_metrics(model, x, y))
    out.update(feature_metrics(model, x))
    out.update(parameter_metrics(model, init_vec))
    out.update(gradient_metrics(model, x, y))
    out.update(fisher_metrics(model, x, y))
    out["sam_sharpness"] = sharpness_metric(model, x, y, rho=0.05, adaptive=False)
    out["asam_sharpness"] = sharpness_metric(model, x, y, rho=0.5, adaptive=True)
    if heavy:
        try:
            out.update(hessian_metrics(model, x[: min(8, len(x))], y[: min(8, len(y))]))
        except Exception as exc:
            out["hessian_error"] = str(exc)[:160]
    return out


@dataclass(frozen=True)
class RunConfig:
    dataset: str
    arch: str
    optimizer: str
    lr_level: str
    lr: float
    wd: float
    dropout: float
    seed: int

    @property
    def config_id(self) -> str:
        payload = asdict(self) | {"seed": 0}
        return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:12]

    @property
    def run_id(self) -> str:
        return f"{self.config_id}-s{self.seed}"


def frozen_grid(dataset_name: str, smoke: bool) -> list[RunConfig]:
    architectures = ("cnn", "resnet", "wide_resnet")
    learning_rates = {
        "adamw": {"low": 3e-4, "high": 1e-3},
        "sgd": {"low": 1e-2, "high": 3e-2},
    }
    seeds = (8311,) if smoke else (8311, 8312, 8313, 8314, 8315)
    settings = []
    for optimizer in ("adamw", "sgd"):
        settings.extend([
            (optimizer, "low", learning_rates[optimizer]["low"], 0.0, 0.0),
            (optimizer, "low", learning_rates[optimizer]["low"], 1e-3, 0.2),
            (optimizer, "high", learning_rates[optimizer]["high"], 0.0, 0.2),
            (optimizer, "high", learning_rates[optimizer]["high"], 1e-3, 0.0),
        ])
    if smoke:
        settings = settings[:1]
    # Settings are outermost so a time-boxed prefix remains architecture-balanced.
    return [
        RunConfig(dataset_name, arch, optimizer, lr_level, lr, wd, dropout, seed)
        for optimizer, lr_level, lr, wd, dropout in settings
        for arch in architectures
        for seed in seeds
    ]


def make_optimizer(model: nn.Module, cfg: RunConfig):
    if cfg.optimizer == "sgd":
        return torch.optim.SGD(model.parameters(), lr=cfg.lr, momentum=0.9, nesterov=True, weight_decay=cfg.wd)
    return torch.optim.AdamW(model.parameters(), lr=cfg.lr, weight_decay=cfg.wd)


def train_run(
    cfg: RunConfig,
    epochs: int,
    batch_size: int,
    n_train: int,
    n_val: int,
    n_test: int,
    metric_n: int,
    device: str,
    deadline: float,
    in_run_reserve: float,
) -> dict[str, float | int | str]:
    set_seed(cfg.seed)
    train_loader, val_loader, test_loader, metric_loaders = load_image_data(
        cfg.dataset, batch_size, n_train, n_val, n_test, cfg.seed
    )
    model = make_model(cfg.arch, cfg.dropout, num_classes=int(dataset_spec(cfg.dataset)["classes"])).to(device)
    init_vec = parameter_vector(model)
    optimizer = make_optimizer(model, cfg)
    started = time.time()
    snapshots = sorted(set([max(1, epochs // 2), epochs]))

    row: dict[str, float | int | str] = {
        "run_uuid": str(uuid.uuid4()),
        "run_id": cfg.run_id,
        "config_id": cfg.config_id,
        "environment_id": f"{cfg.dataset}-target-transport-v1",
        "split_id": f"{cfg.dataset}-train-validation-test-20260823",
        "task": cfg.dataset,
        "arch": cfg.arch,
        "seed_id": cfg.seed,
        "learning_rate": cfg.lr,
        "lr_level": cfg.lr_level,
        "weight_decay": cfg.wd,
        "dropout": cfg.dropout,
        "optimizer": cfg.optimizer,
        "epochs": epochs,
        "batch_size": batch_size,
        "n_train": n_train,
        "n_val": n_val,
        "n_test": n_test,
        "metric_n": metric_n,
        "device": device,
    }

    for epoch in range(1, epochs + 1):
        model.train()
        for x, y in train_loader:
            x, y = x.to(device), y.to(device)
            optimizer.zero_grad(set_to_none=True)
            loss = loss_for_logits(model(x), y)
            loss.backward()
            optimizer.step()
        if time.time() > deadline - in_run_reserve:
            raise TimeoutError("wall-clock reserve reached during run")
        if epoch in snapshots:
            ev = evaluate(model, val_loader, device)
            row[f"val_loss_ep{epoch}"] = ev["loss"]
            row[f"val_acc_ep{epoch}"] = ev["acc"]

    train_ev = evaluate(model, train_loader, device, max_batches=8)
    val_ev = evaluate(model, val_loader, device)
    target_suite = evaluate_target_suite(
        model,
        test_loader,
        device,
        stable_corruption_seed(cfg.run_id),
    )
    diagnostic_replicates = []
    for batch_index, metric_loader in enumerate(metric_loaders):
        metric_x, metric_y = collect_batch(metric_loader, metric_n, device)
        diagnostic_replicates.append(
            all_metrics(model, init_vec, metric_x, metric_y, heavy=batch_index == 0)
        )
    numeric_keys = sorted(
        set.union(
            *[
                {key for key, value in replicate.items() if isinstance(value, (int, float))}
                for replicate in diagnostic_replicates
            ]
        )
    )
    diagnostics = {
        key: float(
            np.mean(
                [float(replicate[key]) for replicate in diagnostic_replicates if key in replicate]
            )
        )
        for key in numeric_keys
    }
    diagnostics.update(
        {
            f"{key}_metric_batch_std": (
                float(
                    np.std(
                        [float(replicate[key]) for replicate in diagnostic_replicates if key in replicate],
                        ddof=1,
                    )
                )
                if sum(key in replicate for replicate in diagnostic_replicates) > 1
                else math.nan
            )
            for key in numeric_keys
        }
    )
    random_seed = int(hashlib.sha256(cfg.run_id.encode()).hexdigest()[:16], 16)
    diagnostics["random_metric"] = float(np.random.default_rng(random_seed).normal())
    row["final_train_batch_loss"] = float(loss.detach().cpu())
    row["train_loss"] = train_ev["loss"]
    row["train_acc"] = train_ev["acc"]
    row["val_loss"] = val_ev["loss"]
    row["val_acc"] = val_ev["acc"]
    row["test_loss"] = target_suite["clean_test_loss"]
    row["test_acc"] = target_suite["clean_test_acc"]
    row["final_acc"] = target_suite["clean_test_acc"]
    row.update(target_suite)
    row.update(diagnostics)
    row["elapsed_s"] = time.time() - started
    row["error"] = ""
    return row


def append_row(path: Path, row: dict[str, float | int | str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists()
    if exists:
        with path.open("r", newline="", encoding="utf-8") as handle:
            fieldnames = next(csv.reader(handle))
    else:
        fieldnames = list(row.keys())
    missing = [k for k in row.keys() if k not in fieldnames]
    if missing and exists:
        rows = []
        with path.open("r", newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            rows = list(reader)
        fieldnames = fieldnames + missing
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        if not exists:
            writer.writeheader()
        writer.writerow({k: row.get(k, "") for k in fieldnames})
        handle.flush()
        os.fsync(handle.fileno())


def main() -> int:
    parser = argparse.ArgumentParser(description="MBE multi-target image transport atlas")
    parser.add_argument("--dataset", choices=("cifar10", "cifar100", "svhn"), default=DEFAULT_DATASET)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--max-hours", type=float, default=9.5)
    parser.add_argument("--epochs", type=int, default=15)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--n-train", type=int, default=20_000)
    parser.add_argument("--n-val", type=int, default=5_000)
    parser.add_argument("--n-test", type=int, default=5_000)
    parser.add_argument("--metric-n", type=int, default=16)
    args = parser.parse_args()

    spec = dataset_spec(args.dataset)
    if args.n_train + args.n_val > int(spec["train_population"]) or args.n_test > int(spec["test_population"]):
        raise ValueError(f"requested split sizes exceed {args.dataset}")
    output = Path(f"mbe3_image_transport_{args.dataset}.csv")
    manifest_path = Path(f"mbe3_image_transport_{args.dataset}_manifest.json")
    integrity_path = Path(f"mbe3_image_transport_{args.dataset}_integrity.json")
    started = time.time()
    deadline = started + args.max_hours * 3600
    launch_reserve = 0 if args.smoke else 20 * 60
    in_run_reserve = 0 if args.smoke else 15 * 60
    device = device_name()
    if device == "cuda":
        preflight = torch.randn(128, 128, device=device)
        _ = preflight @ preflight
        torch.cuda.synchronize()

    grid = frozen_grid(args.dataset, args.smoke)
    epochs = 1 if args.smoke else args.epochs
    train_idx, val_idx, test_idx = _split_indices(
        int(spec["train_population"]), int(spec["test_population"]), args.n_train, args.n_val, args.n_test
    )
    manifest = {
        "schema_version": 1,
        "status": "preregistered_image_target_transport_atlas",
        "experiment": "mbe3_image_target_transport_atlas_v1",
        "environment_id": f"{args.dataset}-target-transport-v1",
        "split_id": f"{args.dataset}-train-validation-test-20260823",
        "split_hashes": {
            "train_indices": hashlib.sha256(train_idx.tobytes()).hexdigest(),
            "validation_indices": hashlib.sha256(val_idx.tobytes()).hexdigest(),
            "test_indices": hashlib.sha256(test_idx.tobytes()).hexdigest(),
        },
        "device": device,
        "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        "torch_version": torch.__version__,
        "grid": [asdict(config) | {"config_id": config.config_id, "run_id": config.run_id} for config in grid],
        "planned_runs": len(grid),
        "planned_configurations": len({config.config_id for config in grid}),
        "epochs": epochs,
        "batch_size": args.batch_size,
        "n_train": args.n_train,
        "n_validation": args.n_val,
        "n_test": args.n_test,
        "metric_batch_repeats": 3,
        "metric_batch_seed_offsets": [300, 301, 302],
        "max_hours": args.max_hours,
        "primary_target": "clean_test_loss",
        "secondary_targets": ["corruption_mean_loss", "clean_test_ece", "clean_test_brier"],
        "corruption_suite": {
            "gaussian_noise_normalized_sigma": 0.20,
            "blur": "3x3 average pool, stride 1, padding 1",
            "low_contrast_normalized_scale": 0.55,
            "seed": "SHA256 of full run_id",
        },
        "frozen_controls": [
            "arch",
            "optimizer",
            "lr_level",
            "learning_rate",
            "weight_decay",
            "dropout",
            "seed_id",
            "final_train_batch_loss",
            "val_loss",
        ],
        "primary_gate": "At least 90% of 120 planned runs, all 24 configurations, at least four seeds per included configuration, all three architectures, and no duplicate run IDs. Otherwise descriptive only.",
        "negative_control_definition": "One Gaussian value per full run_id from a SHA256-derived seed.",
        "exclusion_rule": "Retain every row and every failure. Exclude failed rows only from analyses requiring valid metric values.",
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2), flush=True)

    completed = set()
    if output.exists():
        with output.open("r", newline="", encoding="utf-8") as handle:
            completed = {row["run_id"] for row in csv.DictReader(handle) if not row.get("error")}

    for index, config in enumerate(grid, start=1):
        if config.run_id in completed:
            print(f"[{index}/{len(grid)}] cached {config.run_id}", flush=True)
            continue
        if time.time() > deadline - launch_reserve:
            print("Stopping before the wall-clock reserve.", flush=True)
            break
        try:
            row = train_run(
                config,
                epochs=epochs,
                batch_size=args.batch_size,
                n_train=args.n_train,
                n_val=args.n_val,
                n_test=args.n_test,
                metric_n=args.metric_n,
                device=device,
                deadline=deadline,
                in_run_reserve=in_run_reserve,
            )
            append_row(output, row)
            print(
                f"[{index}/{len(grid)}] {config.run_id} test_loss={row['test_loss']:.4f} "
                f"fim_norm={row.get('fim_norm', float('nan')):.4f} elapsed={row['elapsed_s']:.1f}s",
                flush=True,
            )
        except Exception as error:
            append_row(
                output,
                {
                    "run_uuid": str(uuid.uuid4()),
                    "run_id": config.run_id,
                    "config_id": config.config_id,
                    "environment_id": manifest["environment_id"],
                    "split_id": manifest["split_id"],
                    "task": args.dataset,
                    "arch": config.arch,
                    "seed_id": config.seed,
                    "learning_rate": config.lr,
                    "lr_level": config.lr_level,
                    "weight_decay": config.wd,
                    "dropout": config.dropout,
                    "optimizer": config.optimizer,
                    "error": repr(error),
                },
            )
            print(f"ERROR {config.run_id}: {error!r}", flush=True)
            if "CUDA" in repr(error) or "AcceleratorError" in type(error).__name__:
                raise
            if isinstance(error, TimeoutError):
                break

    rows = list(csv.DictReader(output.open(encoding="utf-8"))) if output.exists() else []
    valid = [row for row in rows if not row.get("error")]
    config_counts: dict[str, int] = {}
    for row in valid:
        config_counts[row["config_id"]] = config_counts.get(row["config_id"], 0) + 1
    integrity = {
        "rows": len(rows),
        "valid_rows": len(valid),
        "error_rows": len(rows) - len(valid),
        "unique_run_ids": len({row.get("run_id") for row in rows}),
        "duplicate_run_ids": len(rows) - len({row.get("run_id") for row in rows}),
        "valid_configurations": len(config_counts),
        "configurations_with_at_least_four_seeds": sum(count >= 4 for count in config_counts.values()),
        "architectures": sorted({row.get("arch") for row in valid}),
        "primary_gate_pass": (
            len(valid) >= math.ceil(0.9 * len(grid))
            and len(config_counts) == 24
            and all(count >= 4 for count in config_counts.values())
            and {"cnn", "resnet", "wide_resnet"}.issubset({row.get("arch") for row in valid})
        ),
    }
    integrity_path.write_text(json.dumps(integrity, indent=2), encoding="utf-8")
    manifest["finished_at_unix"] = time.time()
    manifest["elapsed_hours"] = (time.time() - started) / 3600
    manifest["integrity"] = integrity
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(integrity, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
