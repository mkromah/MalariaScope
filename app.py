"""MalariaScope educational prototype; individual cell image predictions only."""
from __future__ import annotations

import base64
import json
from pathlib import Path

import streamlit as st
import torch
from PIL import Image, UnidentifiedImageError
from scripts.preprocessing import image_transform

ROOT = Path(__file__).resolve().parent
WEIGHTS = ROOT / "outputs" / "model_best.pt"
SELECTION = ROOT / "outputs" / "selection.json"
BRAND_LOGO = ROOT / "assets" / "MalariaScope_logo.svg"
BRAND_BANNER = ROOT / "assets" / "MalariaScope_banner.svg"

st.set_page_config(
    page_title="MalariaScope | AI-Assisted Microscopy",
    page_icon="🔬",
    layout="centered",
)

def svg_data_uri(path: Path) -> str:
    """Use locally versioned SVG brand assets; no third-party image hosting."""
    return "data:image/svg+xml;base64," + base64.b64encode(path.read_bytes()).decode("ascii")

# Branded header assets are visual only; they do not alter model inference.
if BRAND_LOGO.is_file() and BRAND_BANNER.is_file():
    logo_uri = svg_data_uri(BRAND_LOGO)
    banner_uri = svg_data_uri(BRAND_BANNER)
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: radial-gradient(ellipse at 80% -10%, #392039 0%, transparent 43%),
                        linear-gradient(145deg, #130e1e, #110d1a 70%, #201029);
        }}
        .block-container {{
            max-width: 900px;
            padding-top: 1.8rem;
            padding-bottom: 3.8rem;
        }}
        .ms-hero {{
            position: relative;
            overflow: hidden;
            border-radius: 22px;
            border: 1px solid rgba(242, 117, 150, 0.26);
            background: linear-gradient(90deg, rgba(21, 11, 36, .24),
                                              rgba(21, 11, 36, .08)),
                        url('{banner_uri}') center/cover no-repeat;
            padding: 34px 35px 32px;
            margin: 0 0 22px;
            min-height: 225px;
            box-shadow: 0 16px 42px rgba(0, 0, 0, .18);
        }}
        .ms-logo {{
            display: block;
            width: min(100%, 350px);
            height: auto;
            margin: -4px 0 12px;
        }}
        .ms-eyebrow {{
            color: #f8a9bb;
            font: 700 11px/1.6 system-ui, sans-serif;
            letter-spacing: .12em;
            text-transform: uppercase;
            margin: 0 0 9px;
        }}
        .ms-headline {{
            color: #fff8fc;
            font: 700 clamp(20px, 3.2vw, 28px)/1.22 system-ui, sans-serif;
            letter-spacing: -.03em;
            max-width: 550px;
            margin: 0 0 7px;
        }}
        .ms-description {{
            max-width: 550px;
            margin: 0;
            color: #e6dbe9;
            line-height: 1.5;
            font-size: 14px;
        }}
        @media (max-width: 600px) {{
            .ms-hero {{ padding: 22px 19px; border-radius: 16px; }}
            .block-container {{ padding-top: 1rem; }}
        }}
        </style>
        <section class="ms-hero" aria-label="MalariaScope project introduction">
            <img class="ms-logo" src="{logo_uri}"
                 alt="MalariaScope — microscope and blood cell logo" />
            <div class="ms-eyebrow">Research prototype · AI-assisted microscopy</div>
            <h1 class="ms-headline">One cell. A clear result. A safer review workflow.</h1>
            <p class="ms-description">
                Classify cropped individual blood-cell images and flag uncertain
                predictions for further review.
            </p>
        </section>
        """,
        unsafe_allow_html=True,
    )
else:
    st.title("🔬 MalariaScope")
    st.write("Research demonstration: malaria cell-image classification.")

st.error(
    "NOT A MEDICAL DEVICE. This application cannot diagnose or rule out malaria. "
    "Do not use its output to make patient-care decisions."
)
st.caption(
    "Evaluated on cropped individual cells from the NIH/NLM research dataset; "
    "not on complete blood smears or clinical patients."
)


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
