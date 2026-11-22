#!/usr/bin/env python3
"""Evaluate a frozen MalariaScope checkpoint on the untouched test patients.

Only run after selecting hyperparameters and review threshold on validation.
    python scripts/evaluate.py
Produces outputs/test_metrics.json; never tune from these results.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import (average_precision_score, confusion_matrix,
                             f1_score, roc_auc_score)
from torch.utils.data import DataLoader

from train import ROOT, CellDataset, load_manifest, make_model, predictions


def summarize(y: np.ndarray, p: np.ndarray, margin: float) -> dict:
    pred = (p >= 0.5).astype(int)
    tn, fp, fn, tp = (int(x) for x in confusion_matrix(y, pred, labels=[0, 1]).ravel())
    accepted = (p < (0.5 - margin)) | (p > (0.5 + margin))
    a_y, a_pred = y[accepted], pred[accepted]
    a_tn, a_fp, a_fn, a_tp = (
        int(x) for x in confusion_matrix(a_y, a_pred, labels=[0, 1]).ravel()
    )
    return {
        "n_cell_images": int(len(y)),
        "infected_cells": int((y == 1).sum()),
        "uninfected_cells": int((y == 0).sum()),
        "plain_classifier": {
            "tn": tn, "fp": fp, "fn": fn, "tp": tp,
            "sensitivity": tp / (tp + fn) if tp + fn else None,
            "specificity": tn / (tn + fp) if tn + fp else None,
            "f1": float(f1_score(y, pred, zero_division=0)),
            "auroc": float(roc_auc_score(y, p)),
            "average_precision": float(average_precision_score(y, p)),
        },
        "review_policy": {
            "margin": margin,
            "n_auto": int(accepted.sum()),
            "n_referred_for_review": int((~accepted).sum()),
            "fraction_referred_for_review": float((~accepted).mean()),
            "auto_tn": a_tn, "auto_fp": a_fp,
            "auto_fn": a_fn, "auto_tp": a_tp,
            "auto_sensitivity": a_tp / (a_tp + a_fn) if a_tp + a_fn else None,
            "auto_specificity": a_tn / (a_tn + a_fp) if a_tn + a_fp else None,
            "missed_infected_as_fraction_of_all_infected": (
                a_fn / max(1, int((y == 1).sum()))
            ),
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=ROOT / "data/processed/manifest.csv")
    parser.add_argument("--data-root", type=Path, default=ROOT / "data/raw")
    parser.add_argument("--checkpoint", type=Path, default=ROOT / "outputs/model_best.pt")
    parser.add_argument("--selection", type=Path, default=ROOT / "outputs/selection.json")
    parser.add_argument("--output", type=Path, default=ROOT / "outputs/test_metrics.json")
    parser.add_argument("--batch-size", type=int, default=64)
    args = parser.parse_args()

    with args.selection.open() as f:
        selection = json.load(f)
    margin = float(selection["selection"]["margin"])
    if not 0 <= margin < 0.5:
        raise ValueError("Invalid preselected review threshold")
    rows = load_manifest(args.manifest)
    test = [r for r in rows if r["split"] == "test"]
    if not test:
        raise ValueError("Test split is empty")
    patient_count = len({r["patient_id"] for r in test})
    loader = DataLoader(CellDataset(test, args.data_root),
                        batch_size=args.batch_size, num_workers=2)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    checkpoint = torch.load(args.checkpoint, map_location="cpu", weights_only=True)
    model = make_model(pretrained=False)
    model.load_state_dict(checkpoint["state_dict"])
    model.to(device)
    y, p = predictions(model, loader, device)
    results = summarize(y, p, margin)
    results["n_patients"] = patient_count
    results["evaluation_scope"] = "Held-out patients, cropped cell images; NOT patient-level malaria diagnosis."
    results["limitations"] = [
        "No evaluation on full clinical blood smears or external microscopy sites.",
        "Patient-level clustering reduces independent information; no clinical validation.",
        "Review of uncertain individual cells does not replace human diagnosis.",
        "The test set should not be reused for model or threshold selection."
    ]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w") as f:
        json.dump(results, f, indent=2)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
