#!/usr/bin/env python3
"""Train MalariaScope and select uncertainty threshold using validation ONLY.

Run on Kaggle or a GPU environment with downloaded NIH data.
    python scripts/train.py --epochs 8 --batch-size 64

Saves a selected model checkpoint and validation results in outputs/.
No test-set metrics are computed here.
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import sys
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from sklearn.metrics import confusion_matrix, roc_auc_score
from torch import nn
from torch.utils.data import DataLoader, Dataset
from torchvision import models, transforms

ROOT = Path(__file__).resolve().parents[1]
MEAN = [0.485, 0.456, 0.406]
STD = [0.229, 0.224, 0.225]


class CellDataset(Dataset):
    def __init__(self, records, root: Path, augment: bool = False):
        self.records = records
        self.root = root
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            *([transforms.RandomHorizontalFlip(), transforms.RandomVerticalFlip()]
              if augment else []),
            transforms.ToTensor(),
            transforms.Normalize(MEAN, STD),
        ])

    def __len__(self):
        return len(self.records)

    def __getitem__(self, i):
        row = self.records[i]
        with Image.open(self.root / row["path"]) as img:
            x = self.transform(img.convert("RGB"))
        return x, torch.tensor(int(row["label"]), dtype=torch.long)


def load_manifest(path: Path):
    with path.open(newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    if not rows:
        raise ValueError("Manifest is empty")
    ids = {
        split: {r["patient_id"] for r in rows if r["split"] == split}
        for split in ("train", "val", "test")
    }
    if ids["train"] & ids["val"] or ids["train"] & ids["test"] or ids["val"] & ids["test"]:
        raise ValueError("Patient leakage detected")
    return rows


def make_model(pretrained=True):
    model = models.mobilenet_v3_small(
        weights=models.MobileNet_V3_Small_Weights.DEFAULT if pretrained else None
    )
    model.classifier[3] = nn.Linear(model.classifier[3].in_features, 2)
    return model


@torch.inference_mode()
def predictions(model, loader, device):
    model.eval()
    probs, labels = [], []
    for x, y in loader:
        logits = model(x.to(device))
        probs.extend(torch.softmax(logits, dim=1)[:, 1].cpu().tolist())
        labels.extend(y.tolist())
    return np.asarray(labels, dtype=int), np.asarray(probs, dtype=float)


def threshold_metrics(y, p, threshold: float = 0.5):
    pred = (p >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    return {
        "sensitivity": float(tp / (tp + fn)) if tp + fn else None,
        "specificity": float(tn / (tn + fp)) if tn + fp else None,
        "false_negatives": int(fn),
        "false_positives": int(fp),
        "auroc": float(roc_auc_score(y, p)) if len(set(y.tolist())) == 2 else None,
    }


def choose_review_margin(y, p, min_coverage=0.70):
    """Select a symmetric deferral band around 0.5 using validation labels only.

    Objective: minimize missed infected cells among automatic decisions, with
    >= min_coverage overall automatic decision rate. Tie: prefer wider coverage.
    This is a research choice, not a clinical safety guarantee.
    """
    best = None
    for margin in np.linspace(0, 0.49, 50):
        accepted = (p < (0.5 - margin)) | (p > (0.5 + margin))
        coverage = float(accepted.mean())
        if coverage < min_coverage or not accepted.any():
            continue
        false_negatives = int(((p < 0.5) & (y == 1) & accepted).sum())
        false_negative_rate_total = false_negatives / max(1, int((y == 1).sum()))
        score = (false_negative_rate_total, -coverage)
        if best is None or score < best["score"]:
            best = {
                "score": score,
                "margin": float(margin),
                "validation_coverage": coverage,
                "validation_false_negative_count": false_negatives,
            }
    if best is None:
        raise ValueError("No margin satisfies minimum coverage")
    del best["score"]
    return best


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=ROOT / "data/processed/manifest.csv")
    parser.add_argument("--data-root", type=Path, default=ROOT / "data/raw")
    parser.add_argument("--output", type=Path, default=ROOT / "outputs")
    parser.add_argument("--epochs", type=int, default=8)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--lr", type=float, default=0.0003)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--no-pretrained", action="store_true")
    args = parser.parse_args()
    if args.epochs < 1 or args.batch_size < 1:
        parser.error("epochs and batch-size must be positive")
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training on {device}", flush=True)
    rows = load_manifest(args.manifest)
    train = [r for r in rows if r["split"] == "train"]
    val = [r for r in rows if r["split"] == "val"]
    if not train or not val:
        raise ValueError("Train and validation splits must be nonempty")
    train_loader = DataLoader(CellDataset(train, args.data_root, True),
                              batch_size=args.batch_size, shuffle=True, num_workers=2)
    val_loader = DataLoader(CellDataset(val, args.data_root),
                            batch_size=args.batch_size, num_workers=2)
    model = make_model(not args.no_pretrained).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr)
    criterion = nn.CrossEntropyLoss()
    args.output.mkdir(parents=True, exist_ok=True)
    best_loss = float("inf")
    ckpt = args.output / "model_best.pt"
    for epoch in range(args.epochs):
        model.train()
        running, count = 0.0, 0
        for x, y in train_loader:
            x, y = x.to(device), y.to(device)
            optimizer.zero_grad()
            logits = model(x)
            loss = criterion(logits, y)
            loss.backward()
            optimizer.step()
            running += loss.item() * len(y)
            count += len(y)
        model.eval()
        vloss, vcount = 0.0, 0
        with torch.inference_mode():
            for x, y in val_loader:
                logits = model(x.to(device))
                loss = criterion(logits, y.to(device))
                vloss += loss.item() * len(y)
                vcount += len(y)
        avg = vloss / max(1, vcount)
        print(f"Epoch {epoch+1}/{args.epochs}: train_loss={running/max(1,count):.4f}, val_loss={avg:.4f}", flush=True)
        if avg < best_loss:
            best_loss = avg
            torch.save({
                "state_dict": model.state_dict(),
                "arch": "mobilenet_v3_small",
                "seed": args.seed,
                "epoch": epoch + 1,
            }, ckpt)

    checkpoint = torch.load(ckpt, map_location=device, weights_only=True)
    model.load_state_dict(checkpoint["state_dict"])
    y, p = predictions(model, val_loader, device)
    selected = choose_review_margin(y, p)
    config = {
        "model": "mobilenet_v3_small",
        "seed": args.seed,
        "pretrained": not args.no_pretrained,
        "epochs_requested": args.epochs,
        "best_epoch": checkpoint["epoch"],
        "batch_size": args.batch_size,
        "lr": args.lr,
        "validation_metrics": threshold_metrics(y, p),
        "selection": selected,
        "warning": "Research-only individual-cell predictions, not clinical diagnosis",
    }
    with (args.output / "selection.json").open("w") as f:
        json.dump(config, f, indent=2)
    print(json.dumps(config, indent=2))
    print("Next step: python scripts/evaluate.py --checkpoint outputs/model_best.pt --selection outputs/selection.json")


if __name__ == "__main__":
    main()
