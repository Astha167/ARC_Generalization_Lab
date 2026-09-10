#!/usr/bin/env python3
"""Generate the one-page concept summary PDF for Pathway PS submission.

Strengthened to include:
- Maturity assessment
- Competitive context (o3, Greenblatt, BDH-CQ)
- Explicit strengths-and-limitations analysis
- Where BDH-CQ performs worse / remains untested

Output: docs/concept_summary.pdf
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(SCRIPT_DIR, "concept_summary.pdf")

# Colours
DARK = HexColor("#1a1a2e")
ACCENT = HexColor("#4a90d9")
MUTED = HexColor("#555555")
BORDER = HexColor("#cccccc")

def build_styles():
    ss = getSampleStyleSheet()

    ss.add(ParagraphStyle(
        "DocTitle", parent=ss["Title"],
        fontSize=15, leading=18, spaceAfter=2,
        textColor=DARK, alignment=TA_CENTER,
    ))
    ss.add(ParagraphStyle(
        "Subtitle", parent=ss["Normal"],
        fontSize=9, leading=11, spaceAfter=6,
        textColor=MUTED, alignment=TA_CENTER,
    ))
    ss.add(ParagraphStyle(
        "SectionHead", parent=ss["Heading2"],
        fontSize=10.5, leading=13, spaceBefore=8, spaceAfter=3,
        textColor=DARK, fontName="Helvetica-Bold",
    ))
    ss.add(ParagraphStyle(
        "Body", parent=ss["Normal"],
        fontSize=9, leading=12, spaceAfter=4,
        alignment=TA_JUSTIFY, fontName="Helvetica",
    ))
    ss.add(ParagraphStyle(
        "BodyBold", parent=ss["Normal"],
        fontSize=9, leading=12, spaceAfter=4,
        alignment=TA_JUSTIFY, fontName="Helvetica-Bold",
    ))
    ss.add(ParagraphStyle(
        "SmallNote", parent=ss["Normal"],
        fontSize=7.5, leading=10, spaceAfter=2,
        textColor=MUTED, fontName="Helvetica",
    ))
    ss.add(ParagraphStyle(
        "TableCell", parent=ss["Normal"],
        fontSize=8, leading=10, fontName="Helvetica",
    ))
    ss.add(ParagraphStyle(
        "TableHeader", parent=ss["Normal"],
        fontSize=8, leading=10, fontName="Helvetica-Bold",
        textColor=HexColor("#ffffff"),
    ))
    return ss


def build_pdf():
    doc = SimpleDocTemplate(
        OUTPUT_PATH,
        pagesize=A4,
        leftMargin=18*mm, rightMargin=18*mm,
        topMargin=14*mm, bottomMargin=14*mm,
    )

    ss = build_styles()
    story = []

    # TITLE
    story.append(Paragraph(
        "ARC Generalization Lab — One-Page Concept Summary", ss["DocTitle"]))
    story.append(Paragraph(
        "DataForge 2026: Pathway Track  |  September 2026", ss["Subtitle"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER, spaceAfter=6))

    # 1. CENTRAL CLAIM
    story.append(Paragraph("1. Central Claim", ss["SectionHead"]))
    story.append(Paragraph(
        "High performance on a public benchmark does not, by itself, establish generalization to novel tasks. "
        "A public-versus-fresh, distribution-matched comparison provides <b>diagnostic evidence</b> about a possible "
        "generalization gap—but does not prove memorization. The ARC Generalization Lab operationalises this claim "
        "as an interactive research instrument: the same solver evaluates both public ARC-AGI-1 tasks (which appear "
        "in web-scale training corpora) and freshly generated, distribution-matched tasks (which cannot), letting the "
        "learner observe and interpret the resulting performance gap.",
        ss["Body"]))

    # 2. WHY THIS MATTERS
    story.append(Paragraph("2. Why This Matters", ss["SectionHead"]))
    story.append(Paragraph(
        "Bordes et al. (2024) demonstrated empirically that ARC-AGI-1 evaluation tasks appear verbatim in Common Crawl "
        "and The Pile. Any model pre-trained on these corpora may score higher than its genuine rule-induction ability "
        "warrants. Without a fresh, distribution-matched control set, benchmark scores conflate prior familiarity with "
        "general reasoning. This is the benchmark integrity problem our lab addresses.",
        ss["Body"]))

    # 3. COMPETITIVE CONTEXT & ARCHITECTURAL COMPARISON
    story.append(Paragraph("3. Competitive Context & Architectural Comparison", ss["SectionHead"]))
    story.append(Paragraph(
        "We situate BDH-CQ against two representative approaches on dimensions that genuinely differentiate them:",
        ss["Body"]))

    # Comparison table
    header = [
        Paragraph("<b>Dimension</b>", ss["TableHeader"]),
        Paragraph("<b>OpenAI o3</b>", ss["TableHeader"]),
        Paragraph("<b>TTT (Akyürek 2024)</b>", ss["TableHeader"]),
        Paragraph("<b>BDH-CQ (Engdahl 2026)</b>", ss["TableHeader"]),
    ]
    data = [header]
    rows = [
        ("Public ARC-AGI accuracy", "75.7% pass@3", "~53% (TTT + 8B)", "29.5% pass@2"),
        ("Test-time param updates", "Undisclosed (CoT)", "Yes (gradient-based)", "None (W fixed)"),
        ("Inference cost per task", "~$17–33 (est.)", "Moderate (fine-tune)", "$0.0007"),
        ("Parameters", "Undisclosed (frontier)", "8B (Llama 3)", "150M"),
        ("Fresh-task evaluation", "Not published", "Not published", "Dev-reported only"),
    ]
    for row in rows:
        data.append([Paragraph(cell, ss["TableCell"]) for cell in row])

    col_w = [32*mm, 35*mm, 38*mm, 42*mm]
    t = Table(data, colWidths=col_w, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
        ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#ffffff")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#f8f9fa"), HexColor("#ffffff")]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(t)
    story.append(Spacer(1, 4))

    # 4. MECHANISM
    story.append(Paragraph("4. Mechanism: Optimization vs. Contextual Adaptation", ss["SectionHead"]))
    story.append(Paragraph(
        "Optimization-based approaches (TTT, HRM/TRM) update model weights on each test instance via gradient descent. "
        "BDH-CQ takes the opposite path: weights remain frozen at inference time. Instead, "
        "each demonstration updates an evolving recurrent associative memory state S(t) through forward-pass "
        "binding operations. The model accumulates task-specific context without backpropagation, enabling inference "
        "at $0.0007 per task with 150M parameters.",
        ss["Body"]))

    # 5. STRENGTHS AND LIMITATIONS
    story.append(Paragraph("5. Strengths and Limitations", ss["SectionHead"]))
    story.append(Paragraph(
        "<b>Strengths:</b> BDH-CQ achieves the lowest reported per-task inference cost on ARC-AGI-1 by orders of magnitude. "
        "Its parameter-frozen inference eliminates catastrophic forgetting risk during evaluation and requires no per-task "
        "fine-tuning infrastructure. The 150M parameter footprint makes it deployable on consumer hardware.",
        ss["Body"]))
    story.append(Paragraph(
        "<b>Where BDH-CQ performs worse:</b> Raw accuracy (29.5% pass@2) is substantially below frontier systems—"
        "OpenAI o3 reaches 75.7% and Greenblatt's GPT-4o pipeline achieves 72% pass@2. BDH-CQ has not been "
        "independently evaluated on freshly generated tasks; all published figures are developer-reported on the public "
        "evaluation set. The finite-capacity associative state may saturate on tasks requiring many distinct rules "
        "or long demonstration sequences.",
        ss["Body"]))

    # 6. MATURITY ASSESSMENT
    story.append(Paragraph("6. Maturity Assessment", ss["SectionHead"]))
    story.append(Paragraph(
        "BDH-CQ is at an <b>early evaluation stage</b>. Developer-reported results on public ARC-AGI-1 exist "
        "(Engdahl et al., 2026), but no independent external reproduction has been published as of September 2026. "
        "The architecture has not been stress-tested on out-of-distribution abstract reasoning benchmarks beyond ARC. "
        "Our lab cites all BDH-CQ figures as PUBLISHED RESULT and does not claim independent verification.",
        ss["Body"]))

    # 7. EVIDENCE CLASSIFICATION
    story.append(Paragraph("7. Evidence Classification", ss["SectionHead"]))
    story.append(Paragraph(
        "Every datum in the artifact is labelled: <b>PUBLISHED RESULT</b> (cited from literature), "
        "<b>MEASURED</b> (computed live by local solver), <b>DEMO DATA</b> (hand-crafted tutorials), "
        "or <b>TOY / DIDACTIC</b> (simplified educational model). No result is presented without provenance.",
        ss["Body"]))

    # 8. REFERENCES
    story.append(Paragraph("8. Primary References", ss["SectionHead"]))
    refs = [
        "Engdahl et al. (2026). <i>BDH-CQ: Introducing In-Context Learning with Recurrent Latent Reasoning.</i> arXiv:2608.09888.",
        "Bordes et al. (2024). <i>An In-Depth Look at Gemini's ARC-AGI Capabilities and Contamination.</i> arXiv:2407.00645.",
        "Akyürek et al. (2024). <i>The Surprising Effectiveness of Test-Time Training for Abstract Reasoning.</i> arXiv:2411.07279.",
        "Chollet (2019). <i>On the Measure of Intelligence.</i> arXiv:1911.01547.",
    ]
    for r in refs:
        story.append(Paragraph(f"• {r}", ss["SmallNote"]))

    doc.build(story)
    print(f"Concept summary PDF generated: {OUTPUT_PATH}")
    # Count approximate words
    import re
    text_parts = []
    for item in story:
        if hasattr(item, 'text'):
            clean = re.sub(r'<[^>]+>', '', item.text)
            text_parts.append(clean)
    word_count = len(' '.join(text_parts).split())
    print(f"   Approximate word count: {word_count}")


if __name__ == "__main__":
    build_pdf()
