"""Research-only PDF export for the MalariaScope demonstration.

No diagnosis, electronic referral, email, database, or remote data transfer.
"""
from __future__ import annotations
from io import BytesIO
from html import escape

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
)


def generate_pdf(current: dict, previous: dict | None, image_bytes: bytes,
                 margin: float, *, handoff: bool = False) -> bytes:
    """Generate a downloadable, non-clinical cell-image research report in memory."""
    stream = BytesIO()
    doc = SimpleDocTemplate(stream, pagesize=A4, leftMargin=48, rightMargin=48,
                            topMargin=45, bottomMargin=45,
                            title="MalariaScope research image report")
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="MSHead", parent=styles["Heading1"],
                               fontSize=20, leading=25, textColor=colors.HexColor("#291739")))
    styles.add(ParagraphStyle(name="MSBody", parent=styles["BodyText"], fontSize=9,
                               leading=14, spaceAfter=8))
    styles.add(ParagraphStyle(name="MSNote", parent=styles["BodyText"], fontSize=8,
                               leading=12, textColor=colors.HexColor("#555064"), spaceAfter=8))

    def para(s, style="MSBody"):
        return Paragraph(escape(str(s)), styles[style])

    story = [
        para("MalariaScope", "MSHead"),
        para("AI-assisted microscopy | Individual-cell research output", "MSNote"),
        para("NOT A MEDICAL DEVICE. This report cannot diagnose or rule out malaria. "
             "It is not a clinical report, medical referral, or assessment of a complete smear."),
        Spacer(1, 10),
        para("Manual-review handoff — not sent to anyone" if handoff
             else "Current research image analysis", "Heading2"),
    ]
    if handoff:
        story.append(para(
            "This document can be shared offline with a qualified microscopy reviewer. "
            "No clinician has received or reviewed this result through MalariaScope."))
    rows = [
        ("Research sample", f"{int(current['index']):02d}"),
        ("Time (UTC)", current["timestamp"]),
        ("Model", "MobileNetV3-Small; frozen research checkpoint"),
        ("Parasitized-class score", f"{float(current['score']):.1%} (uncalibrated)"),
        ("Model output", current["label"]),
        ("Review status", "Review suggested" if current["category"] == "review"
                          else "Automatic cell classification; not clinician verified"),
        ("Original size", f"{current['width']} x {current['height']} pixels"),
        ("Model input", "224 x 224 pixels (aspect ratio preserved, padded)"),
        ("Frozen review band", f"{0.5-margin:.2f} to {0.5+margin:.2f}"),
    ]
    table = Table([[para(k, "MSNote"), para(v)] for k, v in rows], colWidths=[173, 304])
    table.setStyle(TableStyle([
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.HexColor("#f5eff6"), colors.white]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
    ]))
    story += [table, Spacer(1, 12)]
    with PILImage.open(BytesIO(image_bytes)) as src:
        preview = src.convert("RGB")
        preview.thumbnail((380, 380))
    preview_buf = BytesIO()
    preview.save(preview_buf, "PNG")
    preview_buf.seek(0)
    factor = min(125 / preview.width, 125 / preview.height)
    story.append(Image(preview_buf, width=preview.width * factor,
                       height=preview.height * factor))
    story.append(para("Preview: uploaded cropped cell. The app does not verify ground-truth labels.",
                      "MSNote"))
    story.append(para("Comparison with previous image", "Heading2"))
    if previous:
        delta = 100 * (float(current["score"]) - float(previous["score"]))
        story.append(para(
            f"Previous sample {int(previous['index']):02d}: {float(previous['score']):.1%}; "
            f"current sample: {float(current['score']):.1%}; difference: {delta:+.1f} percentage points."))
        story.append(para(
            "These scores describe two cell images only. They do not demonstrate a "
            "change in patient status, parasitemia, or clinical risk.", "MSNote"))
    else:
        story.append(para("No earlier sample in this browser session."))
    story.append(para("Limitations and necessary independent review", "Heading2"))
    for note in (
        "The class score is not a calibrated clinical probability.",
        "The review threshold was selected using validation data and is not clinically validated.",
        "Individual cropped cells cannot represent an entire smear or diagnose a patient.",
        "An automatic classification still requires appropriate professional verification.",
        "No clinical or electronic referral is performed by this application.",
    ):
        story.append(para("- " + note, "MSNote"))
    if handoff:
        story += [
            PageBreak(),
            para("Qualified reviewer worksheet", "MSHead"),
            para("Optional offline documentation. Independently inspect the actual specimen."),
            Spacer(1, 18),
            para("Microscopy / specimen observations:"),
        ]
        story += [para("_" * 78) for _ in range(5)]
        story += [Spacer(1, 12), para("Independent findings / follow-up under local procedures:")]
        story += [para("_" * 78) for _ in range(4)]
        story += [Spacer(1, 15), para("Reviewer and date (completed offline): " + "_" * 38)]
    story.append(para(
        "MalariaScope educational research prototype | "
        "https://github.com/mkromah/MalariaScope", "MSNote"))
    doc.build(story)
    return stream.getvalue()
