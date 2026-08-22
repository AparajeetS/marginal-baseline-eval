from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import random
import subprocess
import sys
import time
import urllib.request
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
            "--index-url",
            "https://download.pytorch.org/whl/cu118",
        ]
    )

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


WIKITEXT = {
    "train": "https://raw.githubusercontent.com/pytorch/examples/main/word_language_model/data/wikitext-2/train.txt",
    "valid": "https://raw.githubusercontent.com/pytorch/examples/main/word_language_model/data/wikitext-2/valid.txt",
    "test": "https://raw.githubusercontent.com/pytorch/examples/main/word_language_model/data/wikitext-2/test.txt",
}
OUTPUT = Path("mbe2_causal_text_factorial_replication.csv")
MANIFEST = Path("mbe2_causal_text_factorial_replication_manifest.json")
LEAKAGE_REPORT = Path("causal_mask_leakage_test.json")


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class CausalTransformer(nn.Module):
    def __init__(
        self,
        vocab_size: int,
        sequence_length: int,
        dim: int,
        depth: int,
        heads: int,
        dropout: float,
        causal: bool = True,
    ) -> None:
        super().__init__()
        self.sequence_length = sequence_length
        self.causal = causal
        self.token_embedding = nn.Embedding(vocab_size, dim)
        self.position_embedding = nn.Embedding(sequence_length, dim)
        layer = nn.TransformerEncoderLayer(
            d_model=dim,
            nhead=heads,
            dim_feedforward=4 * dim,
            dropout=dropout,
            activation="gelu",
            batch_first=True,
            norm_first=True,
        )
        self.encoder = nn.TransformerEncoder(layer, num_layers=depth)
        self.norm = nn.LayerNorm(dim)
        self.output = nn.Linear(dim, vocab_size, bias=False)
        self.output.weight = self.token_embedding.weight

    def forward(self, tokens: torch.Tensor, return_features: bool = False):
        length = tokens.shape[1]
        positions = torch.arange(length, device=tokens.device)
        hidden = self.token_embedding(tokens) + self.position_embedding(positions)[None]
        mask = None
        if self.causal:
            mask = torch.triu(
                torch.ones(length, length, device=tokens.device, dtype=torch.bool),
                diagonal=1,
            )
        hidden = self.encoder(hidden, mask=mask)
        features = self.norm(hidden)
        logits = self.output(features)
        if return_features:
            return logits, features.mean(dim=1)
        return logits


def causal_leakage_test() -> dict[str, float | bool]:
    set_seed(20260717)
    tokens = torch.randint(0, 97, (3, 24))
    changed = tokens.clone()
    changed[:, 13:] = torch.randint(0, 97, changed[:, 13:].shape)

    causal = CausalTransformer(97, 24, 48, 2, 4, 0.0, causal=True).eval()
    unmasked = CausalTransformer(97, 24, 48, 2, 4, 0.0, causal=False).eval()
    unmasked.load_state_dict(causal.state_dict())
    with torch.no_grad():
        causal_difference = (causal(tokens)[:, :13] - causal(changed)[:, :13]).abs().max().item()
        unmasked_difference = (unmasked(tokens)[:, :13] - unmasked(changed)[:, :13]).abs().max().item()
    report = {
        "prefix_length": 13,
        "causal_max_abs_difference": causal_difference,
        "unmasked_max_abs_difference": unmasked_difference,
        "causal_pass": causal_difference <= 1e-6,
        "negative_control_pass": unmasked_difference > 1e-5,
    }
    if not report["causal_pass"] or not report["negative_control_pass"]:
        raise RuntimeError(f"causal leakage preflight failed: {report}")
    return report


def download_wikitext(root: Path, smoke: bool) -> dict[str, Path]:
    root.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}
    if smoke:
        text = ("the metric must not see future tokens . <eos> " * 3000).strip()
        for split in WIKITEXT:
            path = root / f"wiki.{split}.tokens"
            path.write_text(text, encoding="utf-8")
            paths[split] = path
        return paths
    for split, url in WIKITEXT.items():
        path = root / f"wiki.{split}.tokens"
        if not path.exists():
            urllib.request.urlretrieve(url, path)
        paths[split] = path
    return paths


def tokenize(paths: dict[str, Path]) -> tuple[dict[str, torch.Tensor], dict[str, int]]:
    train_words = paths["train"].read_text(encoding="utf-8").replace("\n", " <eos> ").split()
    counts: dict[str, int] = {}
    for word in train_words:
        counts[word] = counts.get(word, 0) + 1
    vocabulary = ["<unk>"] + sorted(
        word for word, count in counts.items() if count >= 2 and word != "<unk>"
    )
    word_to_id = {word: index for index, word in enumerate(vocabulary)}
    encoded: dict[str, torch.Tensor] = {}
    for split, path in paths.items():
        words = path.read_text(encoding="utf-8").replace("\n", " <eos> ").split()
        encoded[split] = torch.tensor(
            [word_to_id.get(word, 0) for word in words], dtype=torch.long
        )
        if encoded[split].numel() and int(encoded[split].max()) >= len(word_to_id):
            raise ValueError(f"{split} token id exceeds vocabulary bounds")
    return encoded, word_to_id


def sample_batch(
    tokens: torch.Tensor,
    batch_size: int,
    sequence_length: int,
    generator: torch.Generator,
    device: torch.device,
) -> tuple[torch.Tensor, torch.Tensor]:
    starts = torch.randint(
        0,
        len(tokens) - sequence_length - 1,
        (batch_size,),
        generator=generator,
    )
    x = torch.stack([tokens[start : start + sequence_length] for start in starts])
    y = torch.stack([tokens[start + 1 : start + sequence_length + 1] for start in starts])
    return x.to(device, non_blocking=True), y.to(device, non_blocking=True)


def loss_for(model: nn.Module, x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
    logits = model(x)
    return F.cross_entropy(logits.reshape(-1, logits.shape[-1]), y.reshape(-1))


@torch.no_grad()
def evaluate(
    model: nn.Module,
    tokens: torch.Tensor,
    sequence_length: int,
    device: torch.device,
    seed: int,
    batches: int = 40,
) -> dict[str, float]:
    model.eval()
    generator = torch.Generator().manual_seed(seed)
    losses = []
    correct = 0
    total = 0
    for _ in range(batches):
        x, y = sample_batch(tokens, 32, sequence_length, generator, device)
        logits = model(x)
        losses.append(F.cross_entropy(logits.reshape(-1, logits.shape[-1]), y.reshape(-1)).item())
        correct += int((logits.argmax(dim=-1) == y).sum())
        total += y.numel()
    loss = float(np.mean(losses))
    return {"loss": loss, "perplexity": float(math.exp(min(loss, 20))), "accuracy": correct / total}


def parameter_vector(model: nn.Module) -> torch.Tensor:
    return torch.cat([parameter.detach().float().cpu().flatten() for parameter in model.parameters()])


def effective_rank(eigenvalues: torch.Tensor) -> float:
    positive = eigenvalues.clamp_min(0)
    probabilities = positive / positive.sum().clamp_min(1e-12)
    entropy = -(probabilities[probabilities > 0] * probabilities[probabilities > 0].log()).sum()
    return float(entropy.exp())


def diagnostic_metrics(
    model: nn.Module,
    initial: torch.Tensor,
    tokens: torch.Tensor,
    sequence_length: int,
    device: torch.device,
    seed: int,
    random_control_seed: int,
) -> dict[str, float]:
    model.eval()
    generator = torch.Generator().manual_seed(seed)
    x, y = sample_batch(tokens, 8, sequence_length, generator, device)
    logits, features = model(x, return_features=True)
    probabilities = logits.softmax(dim=-1)
    confidence, predictions = probabilities.max(dim=-1)
    entropy = -(probabilities * probabilities.clamp_min(1e-12).log()).sum(dim=-1)
    top2 = probabilities.topk(2, dim=-1).values

    rows = []
    sequence_losses = []
    for index in range(len(x)):
        model.zero_grad(set_to_none=True)
        sequence_loss = loss_for(model, x[index : index + 1], y[index : index + 1])
        sequence_loss.backward()
        rows.append(
            torch.cat(
                [p.grad.detach().float().flatten().cpu() for p in model.parameters() if p.grad is not None]
            )
        )
        sequence_losses.append(sequence_loss.item())
    gradients = torch.stack(rows)
    gram = gradients @ gradients.T / len(gradients)
    eigenvalues = torch.linalg.eigvalsh(gram).clamp_min(0)
    fisher_trace = float(eigenvalues.sum())
    fim_erank = effective_rank(eigenvalues)

    feature_gram = features.float() @ features.float().T / max(1, features.shape[1])
    feature_eigenvalues = torch.linalg.eigvalsh(feature_gram).clamp_min(0).cpu()
    final = parameter_vector(model)
    update = final - initial

    base_loss = float(np.mean(sequence_losses))
    noise = []
    with torch.no_grad():
        for parameter in model.parameters():
            scale = 0.01 * parameter.detach().norm() / math.sqrt(max(1, parameter.numel()))
            perturbation = torch.randn_like(parameter) * scale
            parameter.add_(perturbation)
            noise.append(perturbation)
        perturbed_loss = loss_for(model, x, y).item()
        for parameter, perturbation in zip(model.parameters(), noise):
            parameter.sub_(perturbation)

    return {
        "metric_batch_loss": base_loss,
        "metric_batch_accuracy": float((predictions == y).float().mean()),
        "prediction_confidence": float(confidence.mean().detach()),
        "prediction_entropy": float(entropy.mean().detach()),
        "prediction_margin": float((top2[..., 0] - top2[..., 1]).mean().detach()),
        "gradient_norm": float(gradients.mean(dim=0).norm()),
        "empirical_fisher_trace": fisher_trace,
        "fim_erank": fim_erank,
        "fim_norm": fim_erank / len(gradients),
        "feature_erank": effective_rank(feature_eigenvalues.detach()),
        "parameter_l2": float(final.norm()),
        "distance_from_initialization_l2": float(update.norm()),
        "relative_distance_from_initialization": float(update.norm() / initial.norm().clamp_min(1e-12)),
        "update_to_weight_ratio": float(update.norm() / final.norm().clamp_min(1e-12)),
        "sharpness_random_perturbation": perturbed_loss - base_loss,
        # This control is independent for every trained run, unlike the
        # diagnostic-batch seed, which is intentionally shared for comparison.
        "random_metric": float(torch.randn((), generator=torch.Generator().manual_seed(random_control_seed))),
    }


@dataclass(frozen=True)
class RunConfig:
    model_size: str
    dim: int
    depth: int
    heads: int
    learning_rate: float
    weight_decay: float
    dropout: float
    seed: int

    @property
    def config_id(self) -> str:
        payload = asdict(self) | {"seed": 0}
        return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:12]

    @property
    def run_id(self) -> str:
        return f"{self.config_id}-s{self.seed}"


def frozen_grid(smoke: bool) -> list[RunConfig]:
    sizes = {
        "small": (96, 2, 4),
        "medium": (160, 4, 8),
    }
    # A full 3 x 3 x 2 factorial uses a new balanced intervention grid. The
    # values and primary analysis are frozen before this sequential replication
    # is launched; it is not pooled with the earlier underpowered grid.
    settings = [
        (lr, wd, dropout)
        for lr in (1.5e-4, 4e-4, 1e-3)
        for wd in (0.0, 3e-3, 2e-2)
        for dropout in (0.0, 0.2)
    ]
    seeds = [2701] if smoke else [2701, 2702, 2703, 2704, 2705]
    return [
        RunConfig(size, *sizes[size], lr, wd, dropout, seed)
        for size in sizes
        for lr, wd, dropout in settings
        for seed in seeds
    ]


def append_row(path: Path, row: dict[str, object]) -> None:
    exists = path.exists()
    fieldnames = list(row)
    if exists:
        with path.open("r", newline="", encoding="utf-8") as handle:
            fieldnames = next(csv.reader(handle))
        missing = [name for name in row if name not in fieldnames]
        if missing:
            with path.open("r", newline="", encoding="utf-8") as handle:
                existing_rows = list(csv.DictReader(handle))
            fieldnames.extend(missing)
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(existing_rows)
    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        if not exists:
            writer.writeheader()
        writer.writerow(row)
        handle.flush()
        os.fsync(handle.fileno())


def main() -> int:
    parser = argparse.ArgumentParser(description="Sequential MBE 2.0 causal-language factorial replication")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--max-hours", type=float, default=11.5)
    parser.add_argument("--steps", type=int, default=6000)
    parser.add_argument("--sequence-length", type=int, default=64)
    parser.add_argument("--batch-size", type=int, default=48)
    args = parser.parse_args()

    started = time.time()
    deadline = started + args.max_hours * 3600
    launch_reserve = 0 if args.smoke else 20 * 60
    in_run_reserve = 0 if args.smoke else 15 * 60
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if device.type == "cuda":
        preflight = torch.randn(128, 128, device=device)
        _ = preflight @ preflight
        torch.cuda.synchronize()
    leakage = causal_leakage_test()
    LEAKAGE_REPORT.write_text(json.dumps(leakage, indent=2), encoding="utf-8")

    paths = download_wikitext(Path("wikitext-2"), args.smoke)
    splits, vocabulary = tokenize(paths)
    grid = frozen_grid(args.smoke)
    steps = 3 if args.smoke else args.steps
    completed = set()
    if OUTPUT.exists():
        with OUTPUT.open("r", newline="", encoding="utf-8") as handle:
            completed = {row["run_id"] for row in csv.DictReader(handle) if not row.get("error")}

    manifest = {
        "schema_version": 1,
        "status": "preregistered_sequential_replication",
        "experiment": "mbe2_causal_text_factorial_replication_v1",
        "environment_id": "wikitext2-causal-lm-fixed-splits-v1-replication",
        "split_id": "official-wikitext2-train-valid-test",
        "dataset_hashes": {split: sha256(path) for split, path in paths.items()},
        "vocabulary_size": len(vocabulary),
        "device": str(device),
        "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        "torch_version": torch.__version__,
        "torch_cuda_version": torch.version.cuda,
        "causal_mask_test": leakage,
        "grid": [asdict(config) | {"config_id": config.config_id, "run_id": config.run_id} for config in grid],
        "steps": steps,
        "batch_size": args.batch_size,
        "sequence_length": args.sequence_length,
        "metric_batch_repeats": 3,
        "metric_batch_seed_offsets": [300, 301, 302],
        "negative_control_definition": "One Gaussian value per full run_id, generated with a SHA256-derived seed. Diagnostic batch sampling remains separately controlled by seed_id plus offset.",
        "max_hours": args.max_hours,
        "primary_targets": ["test_loss", "test_perplexity"],
        "secondary_target": "token_accuracy",
        "primary_claim_scope": "Sequential within-WikiText-2 replication of metric reliability profiles for token NLL beyond frozen design and training-state baselines. Cross-environment or universal claims are out of scope. This grid is reported separately from the earlier underpowered factorial.",
        "frozen_controls": ["model_size", "learning_rate", "weight_decay", "dropout", "seed_block", "final_train_batch_loss", "val_loss"],
        "exclusion_rule": "Keep every completed row. Retain failed rows in the raw ledger and exclude them only from analyses requiring valid metric values.",
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2), flush=True)

    for index, config in enumerate(grid, start=1):
        if config.run_id in completed:
            print(f"[{index}/{len(grid)}] cached {config.run_id}", flush=True)
            continue
        if time.time() > deadline - launch_reserve:
            print("Stopping before the wall-clock reserve.", flush=True)
            break
        run_started = time.time()
        try:
            set_seed(config.seed)
            model = CausalTransformer(
                len(vocabulary),
                args.sequence_length,
                config.dim,
                config.depth,
                config.heads,
                config.dropout,
                causal=True,
            ).to(device)
            initial = parameter_vector(model)
            optimizer = torch.optim.AdamW(
                model.parameters(), lr=config.learning_rate, weight_decay=config.weight_decay
            )
            generator = torch.Generator().manual_seed(config.seed)
            model.train()
            loss_value = math.nan
            for step in range(1, steps + 1):
                x, y = sample_batch(
                    splits["train"], args.batch_size, args.sequence_length, generator, device
                )
                optimizer.zero_grad(set_to_none=True)
                loss = loss_for(model, x, y)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()
                loss_value = loss.item()
                if step % 250 == 0:
                    print(f"{config.run_id} step={step}/{steps} loss={loss_value:.4f}", flush=True)
                if time.time() > deadline - in_run_reserve:
                    raise TimeoutError("wall-clock reserve reached during run")

            validation = evaluate(
                model, splits["valid"], args.sequence_length, device, config.seed + 100
            )
            test = evaluate(model, splits["test"], args.sequence_length, device, config.seed + 200)
            random_control_seed = int(
                hashlib.sha256(config.run_id.encode()).hexdigest()[:16], 16
            ) % (2**63 - 1)
            diagnostic_replicates = [
                diagnostic_metrics(
                    model,
                    initial,
                    splits["train"],
                    args.sequence_length,
                    device,
                    config.seed + offset,
                    random_control_seed,
                )
                for offset in (300, 301, 302)
            ]
            diagnostic_keys = diagnostic_replicates[0].keys()
            diagnostics = {
                key: float(np.mean([replicate[key] for replicate in diagnostic_replicates]))
                for key in diagnostic_keys
            }
            diagnostics.update(
                {
                    f"{key}_metric_batch_std": float(
                        np.std([replicate[key] for replicate in diagnostic_replicates], ddof=1)
                    )
                    for key in diagnostic_keys
                    if key != "random_metric"
                }
            )
            row: dict[str, object] = {
                "run_uuid": str(uuid.uuid4()),
                "run_id": config.run_id,
                "config_id": config.config_id,
                "seed_id": config.seed,
                "split_id": manifest["split_id"],
                "environment_id": manifest["environment_id"],
                **asdict(config),
                "steps": steps,
                "batch_size": args.batch_size,
                "sequence_length": args.sequence_length,
                "final_train_batch_loss": loss_value,
                "val_loss": validation["loss"],
                "val_perplexity": validation["perplexity"],
                "val_token_accuracy": validation["accuracy"],
                "test_loss": test["loss"],
                "test_perplexity": test["perplexity"],
                "test_token_accuracy": test["accuracy"],
                **diagnostics,
                "elapsed_s": time.time() - run_started,
                "error": "",
            }
            append_row(OUTPUT, row)
            print(
                f"[{index}/{len(grid)}] {config.run_id} test_ppl={test['perplexity']:.2f} "
                f"fim_norm={diagnostics['fim_norm']:.3f} elapsed={row['elapsed_s']:.1f}s",
                flush=True,
            )
        except Exception as error:
            append_row(
                OUTPUT,
                {
                    "run_uuid": str(uuid.uuid4()),
                    "run_id": config.run_id,
                    "config_id": config.config_id,
                    "seed_id": config.seed,
                    "split_id": manifest["split_id"],
                    "environment_id": manifest["environment_id"],
                    **asdict(config),
                    "steps": steps,
                    "batch_size": args.batch_size,
                    "sequence_length": args.sequence_length,
                    "error": repr(error),
                },
            )
            print(f"ERROR {config.run_id}: {error!r}", flush=True)
            if "CUDA" in repr(error) or "AcceleratorError" in type(error).__name__:
                raise
            if isinstance(error, TimeoutError):
                break

    manifest["finished_at_unix"] = time.time()
    manifest["elapsed_hours"] = (time.time() - started) / 3600
    manifest["completed_rows"] = sum(1 for _ in csv.DictReader(OUTPUT.open(encoding="utf-8"))) if OUTPUT.exists() else 0
    MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"finished rows={manifest['completed_rows']} elapsed_hours={manifest['elapsed_hours']:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
