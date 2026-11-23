"""Pure, testable research-only decision helpers for the MalariaScope demo.

The score is a CNN class score, not a clinical risk or calibrated probability.
"""
from __future__ import annotations

import math


def classify_cell(score: float, margin: float) -> tuple[str, str]:
    """Return category and honest display label using the *frozen* review margin."""
    if not (math.isfinite(score) and 0.0 <= score <= 1.0):
        raise ValueError("Classifier score must be finite and between 0 and 1")
    if not (math.isfinite(margin) and 0.0 <= margin < 0.5):
        raise ValueError("Review margin must be finite and between 0 and 0.5")
    if (0.5 - margin) <= score <= (0.5 + margin):
        return "review", "Uncertain — manual microscopy review suggested"
    if score > 0.5:
        return "parasitized", "Parasite-like features detected — verification required"
    return "uninfected", "No parasite-like features detected in this cell"


def compare_scores(current: dict, previous: dict) -> dict:
    """Compare class scores across two images, never infer clinical change."""
    delta = 100 * (float(current["score"]) - float(previous["score"]))
    return {
        "difference_percentage_points": delta,
        "same_label": current["category"] == previous["category"],
        "notice": (
            "This is a comparison of model outputs for two images, "
            "not evidence of a change in infection status or patient health."
        ),
    }
