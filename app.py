"""MalariaScope educational prototype; individual cell image predictions only."""
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st
import torch
from PIL import Image, UnidentifiedImageError
from scripts.preprocessing import image_transform

ROOT = Path(__file__).resolve().parent
WEIGHTS = ROOT / "outputs" / "model_best.pt"
SELECTION = ROOT / "outputs" / "selection.json"

st.set_page_config(page_title="MalariaScope", page_icon="🔬", layout="centered")
st.title("🔬 MalariaScope")
st.write("Research demonstration: malaria parasite detection in **cropped individual blood-cell images**.")
st.error("NOT A MEDICAL DEVICE. This application cannot diagnose or rule out malaria. Do not use its output to make patient-care decisions.")


@st.cache_resource
def load_model():
    from torchvision import models
    model = models.mobilenet_v3_small(weights=None)
    model.classifier[3] = torch.nn.Linear(model.classifier[3].in_features, 2)
    checkpoint = torch.load(WEIGHTS, map_location="cpu", weights_only=True)
    model.load_state_dict(checkpoint["state_dict"])
    model.eval()
    with SELECTION.open() as f:
        settings = json.load(f)
    return model, float(settings["selection"]["margin"])


if not WEIGHTS.is_file() or not SELECTION.is_file():
    st.info("Model not trained or published yet. This page is a UI scaffold only. Train and evaluate the model before making any predictions.")
    st.stop()

model, margin = load_model()
uploaded = st.file_uploader("Upload one cropped red-blood-cell image (PNG or JPEG)", type=["png", "jpg", "jpeg"])
if uploaded:
    if uploaded.size > 10 * 1024 * 1024:
        st.warning("Maximum image size: 10 MB.")
        st.stop()
    try:
        picture = Image.open(uploaded)
        picture.verify()
        uploaded.seek(0)
        picture = Image.open(uploaded).convert("RGB")
    except (UnidentifiedImageError, OSError):
        st.error("Could not read this image.")
        st.stop()
    st.image(picture, caption="Uploaded individual-cell image", width=300)
    transform = image_transform(augment=False)
    with torch.inference_mode():
        prob = float(torch.softmax(model(transform(picture).unsqueeze(0)), dim=1)[0, 1])
    st.caption("These are model scores, not calibrated patient-level disease probabilities.")
    if (0.5 - margin) <= prob <= (0.5 + margin):
        st.warning("Uncertain — refer for manual review")
    elif prob > 0.5:
        st.warning("Parasite-like features detected — professional verification required")
    else:
        st.info("No parasite-like features detected in this cell — this does NOT rule out malaria")
    st.metric("Model score for parasitized cell", f"{prob:.1%}")
    st.caption(f"Validation-selected review band: {0.5 - margin:.2f} to {0.5 + margin:.2f}. Performance and safety have not been clinically established.")
