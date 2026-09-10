#!/usr/bin/env python3
"""Generate the blog PDF for Pathway PS submission.

This is a SEPARATE deliverable from the concept summary.
A narrative, accessible technical blog post (~1500-2500 words).

Output: docs/blog.pdf
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable,
    PageBreak, KeepTogether
)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(SCRIPT_DIR, "blog.pdf")

DARK = HexColor("#1a1a2e")
ACCENT = HexColor("#4a90d9")
MUTED = HexColor("#555555")
BORDER = HexColor("#cccccc")
LIGHT_BG = HexColor("#f0f4f8")


def build_styles():
    ss = getSampleStyleSheet()

    ss.add(ParagraphStyle(
        "BlogTitle", parent=ss["Title"],
        fontSize=20, leading=24, spaceAfter=4,
        textColor=DARK, alignment=TA_CENTER,
        fontName="Helvetica-Bold",
    ))
    ss.add(ParagraphStyle(
        "BlogSubtitle", parent=ss["Normal"],
        fontSize=11, leading=14, spaceAfter=4,
        textColor=MUTED, alignment=TA_CENTER,
        fontName="Helvetica-Oblique",
    ))
    ss.add(ParagraphStyle(
        "AuthorLine", parent=ss["Normal"],
        fontSize=9, leading=12, spaceAfter=10,
        textColor=MUTED, alignment=TA_CENTER,
    ))
    ss.add(ParagraphStyle(
        "H1", parent=ss["Heading1"],
        fontSize=14, leading=17, spaceBefore=14, spaceAfter=6,
        textColor=DARK, fontName="Helvetica-Bold",
    ))
    ss.add(ParagraphStyle(
        "H2", parent=ss["Heading2"],
        fontSize=11.5, leading=14, spaceBefore=10, spaceAfter=4,
        textColor=DARK, fontName="Helvetica-Bold",
    ))
    ss.add(ParagraphStyle(
        "Body", parent=ss["Normal"],
        fontSize=10, leading=14, spaceAfter=6,
        alignment=TA_JUSTIFY, fontName="Helvetica",
    ))
    ss.add(ParagraphStyle(
        "Quote", parent=ss["Normal"],
        fontSize=10, leading=14, spaceAfter=8, spaceBefore=4,
        alignment=TA_LEFT, fontName="Helvetica-Oblique",
        leftIndent=20, rightIndent=20, textColor=MUTED,
        borderWidth=0, borderPadding=0,
    ))
    ss.add(ParagraphStyle(
        "BulletItem", parent=ss["Normal"],
        fontSize=10, leading=14, spaceAfter=3,
        fontName="Helvetica", leftIndent=16,
        bulletIndent=4,
    ))
    ss.add(ParagraphStyle(
        "SmallRef", parent=ss["Normal"],
        fontSize=8, leading=11, spaceAfter=3,
        textColor=MUTED, fontName="Helvetica",
    ))
    ss.add(ParagraphStyle(
        "Caption", parent=ss["Normal"],
        fontSize=8.5, leading=11, spaceAfter=8,
        textColor=MUTED, fontName="Helvetica-Oblique",
        alignment=TA_CENTER,
    ))
    ss.add(ParagraphStyle(
        "TableCell", parent=ss["Normal"],
        fontSize=8.5, leading=11, fontName="Helvetica",
    ))
    ss.add(ParagraphStyle(
        "TableHeader", parent=ss["Normal"],
        fontSize=8.5, leading=11, fontName="Helvetica-Bold",
        textColor=HexColor("#ffffff"),
    ))
    return ss


def build_pdf():
    doc = SimpleDocTemplate(
        OUTPUT_PATH,
        pagesize=A4,
        leftMargin=22*mm, rightMargin=22*mm,
        topMargin=18*mm, bottomMargin=18*mm,
    )

    ss = build_styles()
    story = []

    # ===== TITLE =====
    story.append(Paragraph(
        "Does Your AI Benchmark Measure Intelligence—<br/>or Just Memory?",
        ss["BlogTitle"]))
    story.append(Paragraph(
        "Building an interactive lab to stress-test whether ARC-AGI performance<br/>"
        "survives freshly generated tasks",
        ss["BlogSubtitle"]))
    story.append(Paragraph(
        "ARC Generalization Lab  •  DataForge 2026: Pathway Track  •  September 2026",
        ss["AuthorLine"]))
    story.append(HRFlowable(width="100%", thickness=0.8, color=ACCENT, spaceAfter=10))

    # ===== 1. THE HOOK =====
    story.append(Paragraph("The Uncomfortable Question", ss["H1"]))
    story.append(Paragraph(
        "Imagine you built a model that scores 85% on a well-known AI reasoning benchmark. "
        "You announce the result, the community celebrates, and the leaderboard updates. "
        "But here is the uncomfortable truth: <b>that benchmark has been publicly available since 2019</b>. "
        "Every task, every input-output pair, every transformation rule—indexed, crawled, and ingested "
        "into the very training corpora your model learned from.",
        ss["Body"]))
    story.append(Paragraph(
        "So when your model \"solves\" a benchmark task, is it genuinely reasoning about abstract patterns? "
        "Or is it retrieving a familiar answer from its training data? This is the question that keeps "
        "benchmark researchers up at night—and it is the question that the <b>ARC Generalization Lab</b> "
        "was built to investigate.",
        ss["Body"]))

    # ===== 2. THE PROBLEM =====
    story.append(Paragraph("The Contamination Problem", ss["H1"]))
    story.append(Paragraph(
        "The Abstraction and Reasoning Corpus (ARC-AGI), created by François Chollet in 2019, is widely "
        "regarded as one of the most challenging AI benchmarks. Each task presents a few input → output grid "
        "pairs that demonstrate a transformation rule. The test: infer the rule and apply it to a new input. "
        "No natural language description is provided. Pure visual pattern recognition and rule induction.",
        ss["Body"]))
    story.append(Paragraph(
        "The problem? <b>Bordes et al. (2024)</b> showed empirically that ARC-AGI evaluation tasks appear "
        "verbatim in Common Crawl and The Pile—the massive web-scraped datasets used to train modern LLMs. "
        "This means any model trained on these corpora has likely \"seen\" the test set. Its score may reflect "
        "familiarity rather than genuine generalization.",
        ss["Body"]))
    story.append(Paragraph(
        '"An In-Depth Look at Gemini\'s ARC-AGI Capabilities and Contamination revealed that '
        'significant portions of ARC evaluation data appear in standard pretraining corpora, '
        'calling into question whether measured performance reflects true abstract reasoning."',
        ss["Quote"]))

    # ===== 3. OUR APPROACH =====
    story.append(Paragraph("Our Approach: The Fresh-Task Diagnostic", ss["H1"]))
    story.append(Paragraph(
        "The ARC Generalization Lab takes a direct approach to this problem. Instead of debating whether "
        "contamination matters in theory, we <b>measure its potential effect empirically</b>.",
        ss["Body"]))
    story.append(Paragraph(
        "The method is straightforward:", ss["Body"]))
    story.append(Paragraph(
        "• <b>Step 1:</b> Take a solver—any solver—and evaluate it on a sample of public ARC-AGI-1 tasks.",
        ss["BulletItem"]))
    story.append(Paragraph(
        "• <b>Step 2:</b> Generate fresh, never-before-seen ARC-style tasks whose measurable properties "
        "(grid size, colour count, pair count) match the public evaluation distribution.",
        ss["BulletItem"]))
    story.append(Paragraph(
        "• <b>Step 3:</b> Evaluate the exact same solver on these fresh tasks.",
        ss["BulletItem"]))
    story.append(Paragraph(
        "• <b>Step 4:</b> Compare. If performance drops on fresh tasks, something interesting is happening.",
        ss["BulletItem"]))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "We call this the <b>public-vs-fresh diagnostic</b>. The performance gap is not proof of memorization—it "
        "is a diagnostic signal consistent with multiple hypotheses: benchmark familiarity, distribution mismatch "
        "in unmeasured dimensions, generator artifacts, task ambiguity, or solver baseline limitations. "
        "Scientific honesty demands we present all five.",
        ss["Body"]))

    # ===== 4. ARCHITECTURE =====
    story.append(Paragraph("How the Lab Works", ss["H1"]))
    story.append(Paragraph(
        "The ARC Generalization Lab is a full-stack interactive research instrument:", ss["Body"]))

    story.append(Paragraph("Frontend (Vite + Vanilla JS)", ss["H2"]))
    story.append(Paragraph(
        "An interactive single-page application featuring ARC grid rendering, a 5-step guided learner journey, "
        "an experiment control panel, a recurrent state sandbox, and a check-your-understanding quiz. "
        "Every piece of data displayed is explicitly labelled with its source category.",
        ss["Body"]))

    story.append(Paragraph("Backend (FastAPI)", ss["H2"]))
    story.append(Paragraph(
        "A Python API server that serves public ARC tasks, executes solvers (heuristic baseline, random baseline, "
        "optional LLM), runs evaluations, and wraps the upstream arc-task-gen pipeline for live generation. "
        "A strict evidence-labelling middleware ensures no result is returned without provenance metadata.",
        ss["Body"]))

    story.append(Paragraph("Task Generation (pathwaycom/arc-task-gen)", ss["H2"]))
    story.append(Paragraph(
        "Fresh tasks are generated through a rigorous multi-stage pipeline: distribution analysis of the public "
        "evaluation set, joint constraint sampling (preserving natural covariance between grid properties), "
        "LLM-based rule generation, structural validation, semantic deduplication, and public-eval similarity "
        "filtering. The result: tasks that are measurably similar to public ARC tasks but genuinely novel.",
        ss["Body"]))

    # ===== 5. THE GUIDED JOURNEY =====
    story.append(Paragraph("The 60-Second Guided Experience", ss["H1"]))
    story.append(Paragraph(
        "First-time visitors are guided through a 5-step journey designed to build understanding incrementally:",
        ss["Body"]))
    story.append(Paragraph(
        "• <b>TRY:</b> Interact with a real ARC task—inspect input/output pairs, run a heuristic solver, reveal ground truth.",
        ss["BulletItem"]))
    story.append(Paragraph(
        "• <b>QUESTION:</b> Confront the core question: does high public accuracy prove generalization? (Answer: no.)",
        ss["BulletItem"]))
    story.append(Paragraph(
        "• <b>TEST:</b> Trigger the public-vs-fresh diagnostic comparison using the exact same solver on both task sets.",
        ss["BulletItem"]))
    story.append(Paragraph(
        "• <b>INTERPRET:</b> Learn that a performance gap is diagnostic evidence, not proof of memorization. "
        "Five competing explanations are explicitly presented.",
        ss["BulletItem"]))
    story.append(Paragraph(
        "• <b>ADAPT:</b> Discover BDH-CQ's approach to test-time adaptation via recurrent associative memory "
        "without parameter updates.",
        ss["BulletItem"]))

    # ===== 6. BDH-CQ =====
    story.append(Paragraph("BDH-CQ: A Different Kind of Test-Time Adaptation", ss["H1"]))
    story.append(Paragraph(
        "The benchmark integrity question naturally leads to a deeper one: <b>how should a model adapt to new "
        "tasks at evaluation time?</b>",
        ss["Body"]))
    story.append(Paragraph(
        "Optimization-based approaches like Test-Time Training (Akyürek et al., 2024) perform gradient-based "
        "weight updates on each test instance. This is effective—TTT with Llama-3 8B achieves ~53% on ARC—but "
        "requires backpropagation infrastructure at inference time and risks catastrophic forgetting.",
        ss["Body"]))
    story.append(Paragraph(
        "BDH-CQ (Engdahl et al., 2026) takes the opposite path. Its 150M parameters remain <b>completely frozen</b> "
        "during evaluation. Instead of updating weights, BDH-CQ accumulates each demonstration into an evolving "
        "recurrent associative memory state through forward-pass binding operations. No gradients, no backpropagation, "
        "no parameter updates at test time.",
        ss["Body"]))
    story.append(Paragraph(
        "The result: 29.5% pass@2 on public ARC-AGI-1 at <b>$0.0007 per task</b>—orders of magnitude cheaper "
        "than frontier approaches. Our lab includes an interactive toy sandbox where learners can manipulate "
        "this recurrent state directly: changing demonstration patterns, adjusting retention rates, and observing "
        "how the 4×4 associative state matrix evolves in real time.",
        ss["Body"]))

    # Comparison table
    header = [
        Paragraph("<b>Dimension</b>", ss["TableHeader"]),
        Paragraph("<b>OpenAI o3</b>", ss["TableHeader"]),
        Paragraph("<b>TTT (Akyürek 2024)</b>", ss["TableHeader"]),
        Paragraph("<b>BDH-CQ (Engdahl 2026)</b>", ss["TableHeader"]),
    ]
    tdata = [header]
    rows = [
        ("ARC-AGI accuracy", "75.7% pass@3", "~53% (8B)", "29.5% pass@2"),
        ("Test-time weight updates", "Undisclosed", "Yes (gradients)", "None (W frozen)"),
        ("Cost per task", "~$17-33 est.", "Moderate", "$0.0007"),
        ("Parameters", "Frontier-scale", "8B", "150M"),
    ]
    for row in rows:
        tdata.append([Paragraph(cell, ss["TableCell"]) for cell in row])

    col_w = [34*mm, 34*mm, 36*mm, 42*mm]
    t = Table(tdata, colWidths=col_w, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
        ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#ffffff")),
        ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#f8f9fa"), HexColor("#ffffff")]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(Spacer(1, 4))
    story.append(t)
    story.append(Paragraph(
        "Table: Architectural comparison across test-time adaptation approaches on ARC-AGI-1.",
        ss["Caption"]))

    # ===== 7. EVIDENCE DISCIPLINE =====
    story.append(Paragraph("Radical Transparency: Evidence Labelling", ss["H1"]))
    story.append(Paragraph(
        "One of our strongest design commitments is that <b>no number appears without a source label</b>. "
        "Every datum in the interface is explicitly categorized:",
        ss["Body"]))
    story.append(Paragraph(
        "• <b>PUBLISHED RESULT — PATHWAY:</b> Figures cited directly from Engdahl et al. (2026) or Pathway "
        "technical documentation. We did not retrain BDH-CQ or independently verify these numbers.",
        ss["BulletItem"]))
    story.append(Paragraph(
        "• <b>MEASURED:</b> Computed live by our local solver on real tasks during the experiment.",
        ss["BulletItem"]))
    story.append(Paragraph(
        "• <b>DEMO DATA:</b> Hand-crafted tutorial tasks (DEMO-001 through DEMO-003), clearly labelled and "
        "never presented as experimental evidence.",
        ss["BulletItem"]))
    story.append(Paragraph(
        "• <b>TOY / DIDACTIC:</b> The in-browser 4×4 recurrent state sandbox, explicitly badged as an "
        "educational simplification inspired by BDH-CQ—not the official implementation.",
        ss["BulletItem"]))
    story.append(Spacer(1, 2))
    story.append(Paragraph(
        "This taxonomy prevents the most common scientific communication failure: presenting derivative or "
        "simulated results as if they were primary experimental evidence.",
        ss["Body"]))

    # ===== 8. LIMITATIONS =====
    story.append(Paragraph("What We Don't Know (And Why That Matters)", ss["H1"]))
    story.append(Paragraph(
        "Scientific honesty requires us to be explicit about the boundaries of our findings:", ss["Body"]))
    story.append(Paragraph(
        "• <b>Solvability is not guaranteed.</b> Generated tasks pass structural validation but may have ambiguous "
        "or unsolvable rules. We mitigate this with blind human audits, but cannot eliminate it.",
        ss["BulletItem"]))
    story.append(Paragraph(
        "• <b>Distribution matching is partial.</b> We match measurable properties (grid size, colour count, "
        "pair count), but cognitive complexity, visual salience, and transformation-type diversity may differ "
        "between public and generated tasks in ways we cannot currently measure.",
        ss["BulletItem"]))
    story.append(Paragraph(
        "• <b>Small samples yield wide confidence intervals.</b> Demo-mode experiments with N=5 or N=10 are "
        "exploratory, not definitive. We prominently warn users about this in the interface.",
        ss["BulletItem"]))
    story.append(Paragraph(
        "• <b>The gap has multiple possible causes.</b> We never claim that a performance drop \"proves\" "
        "memorization. Five competing hypotheses are presented with equal weight.",
        ss["BulletItem"]))
    story.append(Paragraph(
        "• <b>BDH-CQ maturity is early-stage.</b> Developer-reported results exist, but no independent "
        "reproduction has been published as of September 2026. All cited figures are clearly labelled as such.",
        ss["BulletItem"]))

    # ===== 9. TAKEAWAYS =====
    story.append(Paragraph("What We Learned Building This", ss["H1"]))
    story.append(Paragraph(
        "Building the ARC Generalization Lab reinforced three convictions:", ss["Body"]))
    story.append(Paragraph(
        "<b>First, benchmark integrity matters more than benchmark scores.</b> A leaderboard number is meaningless "
        "if we cannot distinguish skill from familiarity. The community needs more diagnostic tools—not just "
        "better models.",
        ss["Body"]))
    story.append(Paragraph(
        "<b>Second, scientific honesty is a design decision, not an afterthought.</b> Every label, every disclaimer, "
        "every alternative hypothesis we surface in the interface was a deliberate choice. It would have been easier "
        "to show a single dramatic accuracy gap and call it proof. We chose not to.",
        ss["Body"]))
    story.append(Paragraph(
        "<b>Third, interactivity changes understanding.</b> Reading about recurrent associative memory is one thing. "
        "Watching a state matrix evolve as you add demonstrations, adjust retention, and switch patterns is another. "
        "The guided journey consistently helps learners grasp concepts that paragraphs of text cannot convey alone.",
        ss["Body"]))

    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER, spaceAfter=8))

    # ===== REFERENCES =====
    story.append(Paragraph("References", ss["H2"]))
    refs = [
        "Engdahl, B., et al. (2026). BDH-CQ: Introducing In-Context Learning with Recurrent Latent Reasoning. arXiv:2608.09888.",
        "Bordes, F., et al. (2024). An In-Depth Look at Gemini's ARC-AGI Capabilities and Contamination. arXiv:2407.00645.",
        "Akyürek, E., et al. (2024). The Surprising Effectiveness of Test-Time Training for Abstract Reasoning. arXiv:2411.07279.",
        "Chollet, F. (2019). On the Measure of Intelligence. arXiv:1911.01547.",
    ]
    for r in refs:
        story.append(Paragraph(f"• {r}", ss["SmallRef"]))

    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "Live demonstration: https://frontend-fwohgombc-astha167s-projects.vercel.app/<br/>"
        "Source code: https://github.com/Astha167/ARC_Generalization_Lab",
        ss["SmallRef"]))

    doc.build(story)
    print(f"Blog PDF generated: {OUTPUT_PATH}")
    print(f"   File size: {os.path.getsize(OUTPUT_PATH)} bytes")


if __name__ == "__main__":
    build_pdf()
