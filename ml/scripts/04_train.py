"""
Pipeline d'entrenament fine-grained per identificació de bolets.

Backbones suportats:
    - convnext_tiny  (ràpid, recomanat baseline)
    - convnext_small
    - efficientnetv2_s
    - vit_b_16
    - dinov2_vits14_lc  (DINOv2 ViT-S/14, head linear)
    - dinov2_vitb14_lc  (DINOv2 ViT-B/14, head linear, top performance)

Optimitzat per Apple Silicon M4 amb MPS.

Ús:
    # Baseline ràpid
    python ml/scripts/04_train.py --backbone convnext_tiny --epochs 50

    # Top performance
    python ml/scripts/04_train.py --backbone dinov2_vitb14_lc --epochs 50 --batch-size 16

Sortida:
    ml/models/<run_name>/best.pt
    ml/models/<run_name>/last.pt
    ml/models/<run_name>/metrics.json
    ml/models/<run_name>/label_map.json
"""
from __future__ import annotations

import os
import sys
import json
import time
import math
import argparse
import shutil
from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader, WeightedRandomSampler
from torchvision import transforms
from torchvision.transforms import RandAugment
from PIL import Image
from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "ml" / "data"
MODELS_DIR = ROOT / "ml" / "models"

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


def get_device() -> torch.device:
    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


# -----------------------------------------------------------------------------
# Dataset
# -----------------------------------------------------------------------------
class MushroomDataset(Dataset):
    def __init__(self, df: pd.DataFrame, root: Path, transform=None):
        self.df = df.reset_index(drop=True)
        self.root = root
        self.transform = transform

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        path = self.root / row["local_path"]
        try:
            img = Image.open(path).convert("RGB")
        except Exception:
            # Imatge corrupta: retorna placeholder negre
            img = Image.new("RGB", (224, 224), (0, 0, 0))
        if self.transform:
            img = self.transform(img)
        label = int(row["label"])
        return img, label


def build_transforms(img_size: int, train: bool):
    if train:
        return transforms.Compose([
            transforms.RandomResizedCrop(img_size, scale=(0.6, 1.0)),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomRotation(degrees=20),
            transforms.ColorJitter(0.3, 0.3, 0.3, 0.1),
            RandAugment(num_ops=2, magnitude=9),
            transforms.ToTensor(),
            transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
            transforms.RandomErasing(p=0.25, scale=(0.02, 0.2)),
        ])
    return transforms.Compose([
        transforms.Resize(int(img_size * 1.14)),
        transforms.CenterCrop(img_size),
        transforms.ToTensor(),
        transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
    ])


# -----------------------------------------------------------------------------
# Models
# -----------------------------------------------------------------------------
def build_model(backbone: str, num_classes: int) -> tuple[nn.Module, int]:
    """Construeix el backbone amb cap classificadora.

    Retorna (model, img_size).
    """
    backbone = backbone.lower()
    img_size = 224

    if backbone in ("convnext_tiny", "convnext_small"):
        from torchvision import models as tvm
        if backbone == "convnext_tiny":
            m = tvm.convnext_tiny(weights=tvm.ConvNeXt_Tiny_Weights.DEFAULT)
        else:
            m = tvm.convnext_small(weights=tvm.ConvNeXt_Small_Weights.DEFAULT)
        in_feat = m.classifier[2].in_features
        m.classifier[2] = nn.Linear(in_feat, num_classes)
        return m, 224

    if backbone == "efficientnetv2_s":
        from torchvision import models as tvm
        m = tvm.efficientnet_v2_s(weights=tvm.EfficientNet_V2_S_Weights.DEFAULT)
        in_feat = m.classifier[1].in_features
        m.classifier[1] = nn.Linear(in_feat, num_classes)
        return m, 384

    if backbone == "vit_b_16":
        from torchvision import models as tvm
        m = tvm.vit_b_16(weights=tvm.ViT_B_16_Weights.DEFAULT)
        in_feat = m.heads.head.in_features
        m.heads.head = nn.Linear(in_feat, num_classes)
        return m, 224

    if backbone.startswith("dinov2_"):
        # Carrega via torch.hub (cal connexió primera vegada)
        # _lc significa "linear classifier" head
        repo = "facebookresearch/dinov2"
        if backbone == "dinov2_vits14_lc":
            base = torch.hub.load(repo, "dinov2_vits14")
            embed_dim = 384
        elif backbone == "dinov2_vitb14_lc":
            base = torch.hub.load(repo, "dinov2_vitb14")
            embed_dim = 768
        elif backbone == "dinov2_vitl14_lc":
            base = torch.hub.load(repo, "dinov2_vitl14")
            embed_dim = 1024
        else:
            raise ValueError(f"DINOv2 variant unknown: {backbone}")

        class DinoClassifier(nn.Module):
            def __init__(self, base, embed_dim, num_classes):
                super().__init__()
                self.base = base
                self.head = nn.Sequential(
                    nn.LayerNorm(embed_dim),
                    nn.Linear(embed_dim, num_classes),
                )

            def forward(self, x):
                feats = self.base(x)  # [B, embed_dim]
                return self.head(feats)

        return DinoClassifier(base, embed_dim, num_classes), 224

    raise ValueError(f"Backbone desconegut: {backbone}")


# -----------------------------------------------------------------------------
# MixUp / CutMix
# -----------------------------------------------------------------------------
def mixup_data(x, y, alpha=0.2):
    lam = np.random.beta(alpha, alpha) if alpha > 0 else 1.0
    idx = torch.randperm(x.size(0), device=x.device)
    mixed = lam * x + (1 - lam) * x[idx]
    return mixed, y, y[idx], lam


def mixup_loss(criterion, pred, y_a, y_b, lam):
    return lam * criterion(pred, y_a) + (1 - lam) * criterion(pred, y_b)


# -----------------------------------------------------------------------------
# Train loop
# -----------------------------------------------------------------------------
@torch.no_grad()
def evaluate(model, loader, device, num_classes):
    model.eval()
    correct1 = 0
    correct5 = 0
    total = 0
    loss_sum = 0.0
    crit = nn.CrossEntropyLoss(reduction="sum")
    per_class_correct = torch.zeros(num_classes)
    per_class_total = torch.zeros(num_classes)
    for x, y in tqdm(loader, desc="eval", leave=False):
        x = x.to(device, non_blocking=True)
        y = y.to(device, non_blocking=True)
        logits = model(x)
        loss_sum += crit(logits, y).item()
        topk = logits.topk(5, dim=1).indices
        correct1 += (topk[:, 0] == y).sum().item()
        correct5 += (topk == y.unsqueeze(1)).any(dim=1).sum().item()
        total += y.size(0)
        for c in range(num_classes):
            mask = (y == c)
            per_class_total[c] += mask.sum().item()
            per_class_correct[c] += ((topk[:, 0] == y) & mask).sum().item()
    avg_loss = loss_sum / total
    top1 = correct1 / total
    top5 = correct5 / total
    # macro-F1 simplificat: avg per-class accuracy ignorant classes amb 0 ex.
    valid = per_class_total > 0
    macro_acc = (per_class_correct[valid] / per_class_total[valid]).mean().item()
    return {"loss": avg_loss, "top1": top1, "top5": top5, "macro_acc": macro_acc}


def train_one_epoch(model, loader, optimizer, scheduler, criterion, device,
                    use_mixup=True, log_every=50):
    model.train()
    loss_sum = 0.0
    correct = 0
    total = 0
    pbar = tqdm(loader, desc="train", leave=False)
    for step, (x, y) in enumerate(pbar):
        x = x.to(device, non_blocking=True)
        y = y.to(device, non_blocking=True)

        if use_mixup and np.random.rand() < 0.5:
            x_m, y_a, y_b, lam = mixup_data(x, y, alpha=0.2)
            logits = model(x_m)
            loss = mixup_loss(criterion, logits, y_a, y_b, lam)
        else:
            logits = model(x)
            loss = criterion(logits, y)

        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()
        if scheduler is not None:
            scheduler.step()

        with torch.no_grad():
            preds = logits.argmax(dim=1)
            correct += (preds == y).sum().item()
            total += y.size(0)
        loss_sum += loss.item() * y.size(0)
        if step % log_every == 0:
            pbar.set_postfix(loss=loss.item(), acc=correct / max(total, 1))

    return {"loss": loss_sum / total, "top1": correct / total}


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--backbone", default="convnext_tiny")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--lr-head", type=float, default=3e-4)
    parser.add_argument("--lr-backbone", type=float, default=3e-5)
    parser.add_argument("--weight-decay", type=float, default=0.05)
    parser.add_argument("--warmup-epochs", type=int, default=5)
    parser.add_argument("--label-smoothing", type=float, default=0.1)
    parser.add_argument("--num-workers", type=int, default=4)
    parser.add_argument("--patience", type=int, default=10,
                        help="Early stopping patience (èpoques sense millorar val top1)")
    parser.add_argument("--freeze-backbone", action="store_true",
                        help="Congela backbone (només cap aprèn). Útil per DINOv2 quan dades < 50k.")
    parser.add_argument("--no-mixup", action="store_true")
    parser.add_argument("--run-name", default=None)
    args = parser.parse_args()

    device = get_device()
    print(f"Device: {device}")

    # Carrega dades
    splits = pd.read_parquet(DATA_DIR / "splits.parquet")
    with open(DATA_DIR / "label_map.json") as f:
        label_map = json.load(f)
    num_classes = len(label_map)
    print(f"Classes: {num_classes}")

    # Build model (necessita img_size abans de transforms)
    model, img_size = build_model(args.backbone, num_classes)
    if args.freeze_backbone:
        for n, p in model.named_parameters():
            if "head" not in n and "classifier" not in n:
                p.requires_grad = False
        print(">>> Backbone congelat. Només cap entrena.")
    model = model.to(device)

    # Datasets
    train_df = splits[splits["split"] == "train"]
    val_df = splits[splits["split"] == "val"]
    test_df = splits[splits["split"] == "test"]

    train_ds = MushroomDataset(train_df, ROOT, build_transforms(img_size, train=True))
    val_ds = MushroomDataset(val_df, ROOT, build_transforms(img_size, train=False))
    test_ds = MushroomDataset(test_df, ROOT, build_transforms(img_size, train=False))

    # Sampler ponderat (anti-desbalanceig)
    cls_counts = train_df.groupby("label").size().to_dict()
    sample_weights = train_df["label"].map(lambda c: 1.0 / cls_counts[c]).values
    sampler = WeightedRandomSampler(
        weights=torch.tensor(sample_weights, dtype=torch.double),
        num_samples=len(sample_weights),
        replacement=True,
    )

    train_loader = DataLoader(
        train_ds, batch_size=args.batch_size, sampler=sampler,
        num_workers=args.num_workers, pin_memory=False, persistent_workers=args.num_workers > 0,
    )
    val_loader = DataLoader(val_ds, batch_size=args.batch_size,
                            num_workers=args.num_workers, pin_memory=False,
                            persistent_workers=args.num_workers > 0)
    test_loader = DataLoader(test_ds, batch_size=args.batch_size,
                             num_workers=args.num_workers, pin_memory=False,
                             persistent_workers=args.num_workers > 0)

    # Optimizer: lr diferent per cap vs backbone
    head_params, backbone_params = [], []
    for n, p in model.named_parameters():
        if not p.requires_grad:
            continue
        if "head" in n or "classifier" in n:
            head_params.append(p)
        else:
            backbone_params.append(p)
    param_groups = [{"params": head_params, "lr": args.lr_head}]
    if backbone_params:
        param_groups.append({"params": backbone_params, "lr": args.lr_backbone})
    optimizer = torch.optim.AdamW(param_groups, weight_decay=args.weight_decay)

    # Scheduler: warmup lineal + cosine
    steps_per_epoch = len(train_loader)
    total_steps = steps_per_epoch * args.epochs
    warmup_steps = steps_per_epoch * args.warmup_epochs

    def lr_lambda(step):
        if step < warmup_steps:
            return step / max(1, warmup_steps)
        progress = (step - warmup_steps) / max(1, total_steps - warmup_steps)
        return 0.5 * (1 + math.cos(math.pi * progress))

    scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda)

    criterion = nn.CrossEntropyLoss(label_smoothing=args.label_smoothing)

    # Output dir
    run_name = args.run_name or f"{args.backbone}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir = MODELS_DIR / run_name
    out_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(DATA_DIR / "label_map.json", out_dir / "label_map.json")
    with open(out_dir / "config.json", "w") as f:
        json.dump(vars(args), f, indent=2)

    history = []
    best_top1 = -1.0
    epochs_no_improve = 0

    for epoch in range(1, args.epochs + 1):
        t0 = time.time()
        train_metrics = train_one_epoch(
            model, train_loader, optimizer, scheduler, criterion, device,
            use_mixup=not args.no_mixup,
        )
        val_metrics = evaluate(model, val_loader, device, num_classes)
        dt = time.time() - t0

        log = {
            "epoch": epoch, "time_s": round(dt, 1),
            "train": train_metrics, "val": val_metrics,
            "lr_head": optimizer.param_groups[0]["lr"],
        }
        history.append(log)
        print(f"[{epoch:03d}/{args.epochs}] {dt:.1f}s | "
              f"train_loss={train_metrics['loss']:.3f} train_acc={train_metrics['top1']:.3f} | "
              f"val_loss={val_metrics['loss']:.3f} val_top1={val_metrics['top1']:.3f} "
              f"val_top5={val_metrics['top5']:.3f} val_macro={val_metrics['macro_acc']:.3f}")

        # Checkpoint
        torch.save({
            "model": model.state_dict(),
            "backbone": args.backbone,
            "num_classes": num_classes,
            "img_size": img_size,
            "epoch": epoch,
        }, out_dir / "last.pt")

        if val_metrics["top1"] > best_top1:
            best_top1 = val_metrics["top1"]
            epochs_no_improve = 0
            torch.save({
                "model": model.state_dict(),
                "backbone": args.backbone,
                "num_classes": num_classes,
                "img_size": img_size,
                "epoch": epoch,
                "val_top1": best_top1,
            }, out_dir / "best.pt")
            print(f"  ✓ nou millor val_top1={best_top1:.4f}, guardat best.pt")
        else:
            epochs_no_improve += 1
            if epochs_no_improve >= args.patience:
                print(f"  Early stopping a època {epoch} (sense millora {args.patience}).")
                break

        # Persistir mètriques cada època
        with open(out_dir / "metrics.json", "w") as f:
            json.dump({"history": history, "best_val_top1": best_top1}, f, indent=2)

    # Avaluació final amb best.pt
    print("\n>>> Carregant best.pt per a test final...")
    ckpt = torch.load(out_dir / "best.pt", map_location=device)
    model.load_state_dict(ckpt["model"])
    test_metrics = evaluate(model, test_loader, device, num_classes)
    print(f"\n=== Test final ===")
    print(f"top1={test_metrics['top1']:.4f} top5={test_metrics['top5']:.4f} "
          f"macro_acc={test_metrics['macro_acc']:.4f}")

    with open(out_dir / "metrics.json", "w") as f:
        json.dump({
            "history": history,
            "best_val_top1": best_top1,
            "test": test_metrics,
        }, f, indent=2)

    print(f"\nRun guardat a: {out_dir}")


if __name__ == "__main__":
    main()
