"""MalariaScope educational prototype; individual cell image predictions only."""
from __future__ import annotations

import base64
from datetime import datetime, timezone
from hashlib import sha256
from io import BytesIO
from html import escape
import json
from pathlib import Path

import streamlit as st
import torch
from PIL import Image, UnidentifiedImageError
from scripts.preprocessing import image_transform
from scripts.dashboard_logic import classify_cell, compare_scores
from scripts.reporting import generate_pdf

ROOT = Path(__file__).resolve().parent
WEIGHTS = ROOT / "outputs" / "model_best.pt"
SELECTION = ROOT / "outputs" / "selection.json"
BRAND_LOGO = ROOT / "assets" / "MalariaScope_logo.svg"
BRAND_BANNER = ROOT / "assets" / "MalariaScope_banner.svg"
METRICS_FILE = ROOT / "results" / "test_metrics.json"
THEME_FILE = ROOT / "assets" / "theme.css"

st.set_page_config(
    page_title="MalariaScope | AI-Assisted Microscopy",
    page_icon="🔬",
    layout="wide",
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
            max-width: 1180px;
            padding-top: 1.8rem;
            padding-bottom: 3.8rem;
        }}
        [data-testid="stSidebar"] {{ background: #1b1427; }}
        [data-testid="stMetric"] {{ background: #24192e; border: 1px solid #49344e; border-radius: 12px; padding: 12px 16px; }}
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
        .ms-credit {{
            color: #dccfe9;
            font: 500 12px/1.5 system-ui, sans-serif;
            margin-top: 13px;
            letter-spacing: .01em;
        }}
        .ms-credit strong {{ color: #ff9ab0; font-weight: 700; }}
        @media (max-width: 600px) {{
            .ms-hero {{ padding: 22px 19px; border-radius: 16px; }}
            .block-container {{ padding-top: 1rem; }}
        }}
        </style>
        <section class="ms-hero" aria-label="MalariaScope project introduction">
            <img class="ms-logo" src="{logo_uri}"
                 alt="MalariaScope — microscope and blood cell logo" />
            <div class="ms-eyebrow">Research prototype · AI-assisted microscopy</div>
            <h1 class="ms-headline">Microscopy insights, clearly presented.</h1>
            <p class="ms-description">
                Analyze individual cropped blood-cell images, compare session results,
                and export research reports for independent professional review.
            </p>
            <p class="ms-credit">Developed by <strong>M.A. Kromah</strong></p>
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
# Load responsive visual theme after the branded hero markup.
# This resolves the fixed Streamlit top bar overlapping the dashboard header.
if THEME_FILE.is_file():
    st.markdown("<style>" + THEME_FILE.read_text(encoding="utf-8") + "</style>", unsafe_allow_html=True)

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

# Session-only research comparisons. These entries contain no image pixels or identifiers.
if "ms_history" not in st.session_state:
    st.session_state.ms_history = []
if "ms_image_hash" not in st.session_state:
    st.session_state.ms_image_hash = None
if "ms_next_index" not in st.session_state:
    st.session_state.ms_next_index = 1

with st.sidebar:
    st.header("Research model")
    st.caption("A frozen, non-clinical cell-image classifier")
    st.markdown("**Architecture:** MobileNetV3-Small")
    st.markdown("**Input:** cropped individual cell")
    st.markdown("**Preprocessing:** padded 224 × 224 RGB")
    st.markdown(f"**Review band:** {0.5-margin:.2f}–{0.5+margin:.2f}")
    st.divider()
    st.metric("Images this session", len(st.session_state.ms_history))
    if st.button("Clear session comparisons", use_container_width=True):
        st.session_state.ms_history = []
        st.session_state.ms_image_hash = None
        st.session_state.ms_next_index = 1
        st.rerun()
    st.caption("Only image scores, dimensions and time are kept in this browser session's history. "
               "No stored image archive or clinician messaging is provided.")
    st.markdown("[Source code & limitations](https://github.com/mkromah/MalariaScope)")

st.markdown("### Cell image workbench")
info_cols = st.columns(3, gap="small")
for column, number, title, description in zip(
    info_cols,
    ("01", "02", "03"),
    ("Upload a cell", "Review model output", "Export a report"),
    ("PNG or JPEG only", "Research-only classification", "PDF and offline handoff"),
):
    with column:
        st.markdown(
            '<div class="ms-guide"><span class="ms-step">' + number + '</span>'
            '<div><strong>' + title + '</strong><small>' + description + '</small></div></div>',
            unsafe_allow_html=True,
        )
st.caption("Upload PNG or JPEG of one cropped blood cell. Avoid patient identifiers and full-smear images.")
uploaded = st.file_uploader(
    "Upload a cropped cell image", type=["png", "jpg", "jpeg"],
    help="Maximum 10 MB. This is a research-only demonstration.",
)

if uploaded is None:
    st.info("Upload a cropped cell image to get started. Analyze a second image to compare scores.")
    with st.expander("What can this dashboard do?"):
        st.write("It can classify a cropped cell image, identify scores within the saved "
                 "manual-review band, compare two cell-image scores from the same browser "
                 "session, and generate a research or manual-review PDF. It cannot diagnose "
                 "malaria, evaluate a full blood smear or send a referral.")
    st.stop()

image_bytes = uploaded.getvalue()
if len(image_bytes) > 10 * 1024 * 1024:
    st.error("Maximum image size is 10 MB.")
    st.stop()

try:
    with Image.open(BytesIO(image_bytes)) as probe:
        probe.verify()
    with Image.open(BytesIO(image_bytes)) as source:
        image_width, image_height = source.size
        image_format = source.format or "Image"
        if min(image_width, image_height) < 10 or image_width * image_height > 20_000_000:
            st.error("Unsupported dimensions. Please upload a single cropped cell image.")
            st.stop()
        picture = source.convert("RGB")
except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError):
    st.error("Could not read the file as a valid PNG or JPEG.")
    st.stop()

image_hash = sha256(image_bytes).hexdigest()
if image_hash != st.session_state.ms_image_hash:
    with torch.inference_mode():
        score = float(torch.softmax(
            model(image_transform(augment=False)(picture).unsqueeze(0)),
            dim=1,
        )[0, 1])
    category, label = classify_cell(score, margin)
    st.session_state.ms_history.append({
        "index": st.session_state.ms_next_index,
        "score": score,
        "category": category,
        "label": label,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "width": image_width,
        "height": image_height,
    })
    st.session_state.ms_history = st.session_state.ms_history[-8:]
    st.session_state.ms_next_index += 1
    st.session_state.ms_image_hash = image_hash

current = st.session_state.ms_history[-1]
previous = st.session_state.ms_history[-2] if len(st.session_state.ms_history) >= 2 else None

analysis_tab, comparison_tab, report_tab = st.tabs([
    "🔬 Current analysis", "📊 Compare results", "📄 Report & review",
])

with analysis_tab:
    image_col, results_col = st.columns([1, 1.45], gap="large")
    with image_col:
        st.image(picture, caption="Current cropped cell image", use_container_width=True)
        st.caption("The app does not independently verify the original image label.")
    with results_col:
        score_col, review_col = st.columns(2)
        score_col.metric("Parasitized-class model score", f"{current['score']:.1%}")
        review_col.metric("Review decision",
                          "Manual review" if current["category"] == "review" else "Automatic")
        # A color-coded research status is easier to scan, but the negative class
        # is intentionally blue/neutral rather than a clinical green 'all clear'.
        safe_label = escape(current["label"])
        st.markdown(
            f'<div class="ms-outcome ms-outcome--{current["category"]}">'
            f'<strong>{safe_label}</strong>'
            '<span>Research-only output. Professional verification remains necessary.'</span></div>',
            unsafe_allow_html=True,
        )
        st.progress(current["score"], text="Parasitized-class model score")
        st.caption("This is an uncalibrated neural-network score, NOT a patient-level "
                   "disease probability or clinical certainty.")
        st.markdown(
            f"**Image #{current['index']:02d}**  ·  "
            f"**Dimensions:** {image_width} × {image_height} px  ·  "
            f"**Format:** {image_format}"
        )
        st.caption(f"Frozen review band: {0.5-margin:.2f}–{0.5+margin:.2f}. "
                   "This has not been clinically validated.")
    with st.expander("Historical research benchmark (not this uploaded image)"):
        if METRICS_FILE.is_file():
            with METRICS_FILE.open(encoding="utf-8") as fp:
                benchmark = json.load(fp)
            historical = benchmark["plain_classifier"]
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Test sensitivity", f"{historical['sensitivity']:.2%}")
            c2.metric("Test specificity", f"{historical['specificity']:.2%}")
            c3.metric("Test AUROC", f"{historical['auroc']:.4f}")
            c4.metric("Test cells", f"{benchmark['n_cell_images']:,}")
            st.caption("These measured results describe the original held-out NIH/NLM "
                       "research dataset and cannot predict performance for your new image.")

with comparison_tab:
    st.subheader("Comparison with the previous image")
    if previous is None:
        st.info("Analyze another image to see a comparison of two model scores.")
    else:
        delta = compare_scores(current, previous)
        old, new, difference = st.columns(3)
        old.metric(f"Previous image #{previous['index']:02d}", f"{previous['score']:.1%}")
        new.metric(f"Current image #{current['index']:02d}", f"{current['score']:.1%}")
        difference.metric("Score difference", f"{delta['difference_percentage_points']:+.1f} pp")
        st.markdown("**Previous model output:** " + previous["label"])
        st.markdown("**Current model output:** " + current["label"])
        st.info(delta["notice"])
        st.caption("Different cells can produce different model scores. This does not measure "
                   "parasitemia, disease progression or clinical risk.")

with report_tab:
    st.subheader("Downloadable research documentation")
    st.write("A PDF includes the image preview, model score, review decision, "
             "processing details, comparison where available, and study limitations.")
    full_pdf = generate_pdf(current, previous, image_bytes, margin)
    handoff_pdf = generate_pdf(current, previous, image_bytes, margin, handoff=True)
    first, second = st.columns(2)
    with first:
        st.download_button(
            "⬇ Download full research report (PDF)", full_pdf,
            file_name=f"MalariaScope_Research_{current['index']:02d}.pdf",
            mime="application/pdf", use_container_width=True,
        )
    with second:
        st.download_button(
            "⬇ Prepare professional-review handoff (PDF)", handoff_pdf,
            file_name=f"MalariaScope_Review_Handoff_{current['index']:02d}.pdf",
            mime="application/pdf", use_container_width=True,
        )
    st.warning("**No clinician referral has been sent.** The handoff is a printable "
               "research document for optional independent microscopy review. "
               "It is not an electronic referral, clinical interpretation or diagnosis.")
st.divider()
st.caption("MalariaScope · Developed by M.A. Kromah · Research and education only · "
           "NIH/NLM cell-image dataset. Illustrative branding is not microscopy evidence.")
