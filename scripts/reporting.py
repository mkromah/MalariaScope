"""Research-only PDF export for the MalariaScope demonstration.

No diagnosis, electronic referral, email, database, or remote data transfer.
"""
from __future__ import annotations
from io import BytesIO
from html import escape
from pathlib import Path

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
)

INK = colors.HexColor('#261738')
ROSE = colors.HexColor('#DF5176')
LAVENDER = colors.HexColor('#F6F3FA')
EDGE = colors.HexColor('#E4DDE9')
SLATE = colors.HexColor('#3A3545')
TEAL = colors.HexColor('#1F7278')
AMBER = colors.HexColor('#B56A1A')
LOGO = Path(__file__).resolve().parents[1] / 'assets' / 'MalariaScope_logo.svg'


def _brand_header_footer(canvas, document):
    """Print the existing vector logo and a discrete research-only footer."""
    canvas.saveState()
    width, height = A4
    canvas.setFillColor(INK)
    canvas.rect(0, height - 86, width, 86, fill=1, stroke=0)
    canvas.setFillColor(ROSE)
    canvas.rect(0, height - 7, width, 7, fill=1, stroke=0)
    rendered = False
    if LOGO.is_file():
        try:
            from reportlab.graphics import renderPDF
            from svglib.svglib import svg2rlg
            mark = svg2rlg(str(LOGO))
            if mark and mark.width and mark.height:
                scale = min(295 / mark.width, 59 / mark.height)
                canvas.saveState()
                canvas.translate(40, height - 72)
                canvas.scale(scale, scale)
                renderPDF.draw(mark, canvas, 0, 0)
                canvas.restoreState()
                rendered = True
        except (ImportError, ValueError, OSError, AttributeError):
            pass
    if not rendered:
        canvas.setFillColor(colors.white)
        canvas.setFont('Helvetica-Bold', 24)
        canvas.drawString(40, height - 53, 'MalariaScope')
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.HexColor('#DED3E7'))
    canvas.drawRightString(width - 42, height - 53, 'AI-ASSISTED MICROSCOPY')
    canvas.setStrokeColor(EDGE)
    canvas.line(42, 47, width - 42, 47)
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.HexColor('#706779'))
    canvas.drawString(42, 32, 'RESEARCH ONLY | NOT A MEDICAL DEVICE')
    canvas.drawRightString(width - 42, 32, f'Page {document.page}')
    canvas.restoreState()



def generate_pdf(current: dict, previous: dict | None, image_bytes: bytes,
                 margin: float, *, handoff: bool = False) -> bytes:
    """Generate a downloadable, non-clinical cell-image research report in memory."""
    stream = BytesIO()
    doc = SimpleDocTemplate(stream, pagesize=A4, leftMargin=42, rightMargin=42,
                            topMargin=102, bottomMargin=60,
                            title="MalariaScope research image report")
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="MSHead", parent=styles["Heading1"],
                               fontSize=18, leading=22, textColor=INK))
    styles.add(ParagraphStyle(name="MSBody", parent=styles["BodyText"], fontSize=8.8,
                               leading=12.5, textColor=SLATE, spaceAfter=6))
    styles.add(ParagraphStyle(name="MSNote", parent=styles["BodyText"], fontSize=7.9,
                               leading=11, textColor=colors.HexColor('#6D6877'), spaceAfter=6))

    def para(s, style="MSBody"):
        return Paragraph(escape(str(s)), styles[style])

    story = [
        para("Manual-review handoff" if handoff else "Research image analysis", "MSHead"),
        para("Individual cropped-cell image | Model output record | No patient identification", "MSNote"),
    ]
    safety = Table([[para(
        "NOT A MEDICAL DEVICE. This report cannot diagnose or rule out malaria. "
        "It is not a clinical report, medical referral, or an assessment of an entire blood smear."
    )]], colWidths=[511])
    safety.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor('#FFF3ED')),
        ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor('#F3D4C2')),
        ("LEFTPADDING", (0, 0), (-1, -1), 11),
        ("RIGHTPADDING", (0, 0), (-1, -1), 11),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story += [safety, Spacer(1, 12)]
    tone = AMBER if current["category"] == "review" else (
        ROSE if current["category"] == "parasitized" else TEAL
    )
    bg = (colors.HexColor('#FFF5E8') if current["category"] == "review"
          else colors.HexColor('#FFF1F5') if current["category"] == "parasitized"
          else colors.HexColor('#EBF5F5'))
    decision = Table([[
        [para("PARASITIZED-CLASS MODEL SCORE", "MSNote"),
         para(f"{float(current['score']):.1%}", "MSHead"),
         para("Uncalibrated score - not a clinical probability", "MSNote")],
        [para("MODEL OUTPUT", "MSNote"), para(current["label"])]
    ]], colWidths=[203, 308])
    decision.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), LAVENDER),
        ("BACKGROUND", (1, 0), (1, 0), bg),
        ("LINEBEFORE", (1, 0), (1, 0), 4, tone),
        ("BOX", (0, 0), (-1, -1), 0.6, EDGE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story += [decision, Spacer(1, 11), para("Analysis details", "Heading2")]

    if handoff:
        story.append(para(
            "This document can be shared offline with a qualified microscopy reviewer. "
            "No clinician has received or reviewed this result through MalariaScope."))
    rows = [
        ("Research sample", f"{int(current['index']):02d}"),
        ("Time (UTC)", current["timestamp"]),
        ("Model", "MobileNetV3-Small; frozen research checkpoint"),
        ("Review status", "Review suggested" if current["category"] == "review"
                          else "Automatic cell classification; not clinician verified"),
        ("Original size", f"{current['width']} x {current['height']} pixels"),
        ("Model input", "224 x 224 pixels (aspect ratio preserved, padded)"),
        ("Frozen review band", f"{0.5-margin:.2f} to {0.5+margin:.2f}"),
    ]
    table = Table([[para(k, "MSNote"), para(v)] for k, v in rows], colWidths=[162, 349])
    table.setStyle(TableStyle([
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [LAVENDER, colors.white]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story += [table, Spacer(1, 9)]
    with PILImage.open(BytesIO(image_bytes)) as src:
        preview = src.convert("RGB")
        preview.thumbnail((380, 380))
    preview_buf = BytesIO()
    preview.save(preview_buf, "PNG")
    preview_buf.seek(0)
    factor = min(112 / preview.width, 112 / preview.height)
    preview_image = Image(preview_buf, width=preview.width * factor,
                          height=preview.height * factor)
    preview_section = Table([[
        preview_image,
        [para("UPLOADED CELL PREVIEW", "MSNote"),
         para("Single cropped cell image; the application does not verify ground-truth labels.", "MSNote"),
         para("Image conditions and microscope differences can affect outputs.", "MSNote")]
    ]], colWidths=[138, 373])
    preview_section.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor('#FAF8FC')),
        ("BOX", (0, 0), (-1, -1), 0.6, EDGE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(preview_section)
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
    story.append(para(
        "The class score is uncalibrated and the review threshold is not clinically validated. "
        "This tool only analyzes already-cropped individual cells; it cannot interpret complete "
        "blood smears, diagnose a patient, or send a referral. All decisions require independent "
        "professional review.", "MSNote"))
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
    doc.build(story, onFirstPage=_brand_header_footer, onLaterPages=_brand_header_footer)
    return stream.getvalue()
