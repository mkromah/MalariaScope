#!/usr/bin/env python3
"""Non-deep-learning baseline: RGB color-histogram logistic regression.

Use validation only for model/threshold comparisons. This is an intentionally
simple reproducible control, NOT an image-level clinical diagnostic.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np
from PIL import Image
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]


def extract_features(img_path: Path) -> np.ndarray:
    with Image.open(img_path) as img:
        rgb = np.asarray(img.convert("RGB").resize((64, 64)), dtype=np.uint8)
    hist = []
    for channel in range(3):
        counts, _ = np.histogram(rgb[:, :, channel], bins=16, range=(0, 256))
        hist.extend((counts / rgb[:, :, channel].size).tolist())
    return np.asarray(hist, dtype=np.float32)


def metrics(y, p):
    preds = (p >= 0.5).astype(int)
    tn, fp, fn, tp = (int(x) for x in confusion_matrix(y, preds, labels=[0, 1]).ravel())
    return {
        "n": int(len(y)), "tn": tn, "fp": fp, "fn": fn, "tp": tp,
        "sensitivity": tp / (tp + fn) if tp + fn else None,
        "specificity": tn / (tn + fp) if tn + fp else None,
        "auroc": float(roc_auc_score(y, p)),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=ROOT / "data/processed/manifest.csv")
    parser.add_argument("--data-root", type=Path, default=ROOT / "data/raw")
    parser.add_argument("--output", type=Path, default=ROOT / "outputs/baseline_validation.json")
    args = parser.parse_args()

    with args.manifest.open(newline="") as f:
        rows = list(csv.DictReader(f))
    # Validate disjointness before using the labels.
    patients = {
        split: {r["patient_id"] for r in rows if r["split"] == split}
        for split in ("train", "val", "test")
    }
    if (patients["train"] & patients["val"]
            or patients["train"] & patients["test"]
            or patients["val"] & patients["test"]):
        raise ValueError("Patient leakage in manifest")
    groups = {}
    for split in ("train", "val"):
        selected = [r for r in rows if r["split"] == split]
        groups[split] = (
            np.stack([extract_features(args.data_root / r["path"]) for r in selected]),
            np.array([int(r["label"]) for r in selected]),
        )

    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1500, random_state=42))
    model.fit(*groups["train"])
    x_val, y_val = groups["val"]
    probs = model.predict_proba(x_val)[:, 1]
    result = {
        "model": "RGB-histogram logistic regression",
        "eval_split": "validation only (never test)",
        "metrics": metrics(y_val, probs),
        "warning": "Image-level research baseline, NOT clinical performance.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
