#!/usr/bin/env python3
from __future__ import annotations

import html
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "SUBMISSION.md"
OUTPUT = ROOT / "output" / "pdf" / "Wes_Jones_Beat_Claude_General_000.pdf"


def inline_markup(text: str) -> str:
    text = html.escape(text.strip())
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`(.+?)`", r"<font name='Courier'>\1</font>", text)
    return text


def styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "Title",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=17,
            leading=19,
            textColor=colors.HexColor("#121826"),
            alignment=TA_CENTER,
            spaceAfter=4,
        ),
        "meta": ParagraphStyle(
            "Meta",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8.2,
            leading=10,
            textColor=colors.HexColor("#455267"),
            alignment=TA_CENTER,
            spaceAfter=7,
        ),
        "h2": ParagraphStyle(
            "H2",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=11.2,
            leading=13,
            textColor=colors.HexColor("#0F5C5E"),
            spaceBefore=7,
            spaceAfter=3,
            keepWithNext=True,
        ),
        "h3": ParagraphStyle(
            "H3",
            parent=base["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=9.2,
            leading=11,
            textColor=colors.HexColor("#243244"),
            spaceBefore=4,
            spaceAfter=2,
            keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=7.7,
            leading=9.45,
            textColor=colors.HexColor("#202B3A"),
            spaceAfter=3.2,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=7.55,
            leading=9.2,
            leftIndent=10,
            firstLineIndent=-6,
            bulletIndent=2,
            textColor=colors.HexColor("#202B3A"),
            spaceAfter=1.6,
        ),
        "table": ParagraphStyle(
            "Table",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=6.3,
            leading=7.4,
            textColor=colors.HexColor("#202B3A"),
        ),
    }


def page_footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#D5DCE5"))
    canvas.setLineWidth(0.5)
    canvas.line(doc.leftMargin, 0.38 * inch, letter[0] - doc.rightMargin, 0.38 * inch)
    canvas.setFont("Helvetica", 6.5)
    canvas.setFillColor(colors.HexColor("#667085"))
    canvas.drawString(doc.leftMargin, 0.24 * inch, "Wes Jones | Beat Claude General 000 | Brief 2026-07")
    canvas.drawRightString(letter[0] - doc.rightMargin, 0.24 * inch, f"Page {doc.page}")
    canvas.restoreState()


def parse_table(lines: list[str], style) -> Table:
    rows = []
    for line in lines:
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if all(set(cell) <= set("-: ") for cell in cells):
            continue
        rows.append([Paragraph(inline_markup(cell), style) for cell in cells])
    column_count = len(rows[0])
    if column_count == 4:
        widths = [2.02 * inch, 1.42 * inch, 0.58 * inch, 3.1 * inch]
    else:
        widths = [7.12 * inch / column_count] * column_count
    table = Table(rows, colWidths=widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8F2F2")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#123B3C")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#C9D2DD")),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 2.5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7F9FB")]),
            ]
        )
    )
    return table


def build():
    s = styles()
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    story = []
    paragraph_buffer: list[str] = []

    def flush_paragraph():
        if paragraph_buffer:
            story.append(Paragraph(inline_markup(" ".join(paragraph_buffer)), s["body"]))
            paragraph_buffer.clear()

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            flush_paragraph()
            i += 1
            continue
        if stripped.startswith("|"):
            flush_paragraph()
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i])
                i += 1
            story.append(parse_table(table_lines, s["table"]))
            story.append(Spacer(1, 3))
            continue
        if stripped.startswith("# "):
            flush_paragraph()
            story.append(Paragraph(inline_markup(stripped[2:]), s["title"]))
            i += 1
            continue
        if stripped.startswith("## "):
            flush_paragraph()
            heading = stripped[3:]
            if heading == "3. Evidence Log":
                story.append(PageBreak())
            story.append(Paragraph(inline_markup(heading), s["h2"]))
            i += 1
            continue
        if stripped.startswith("### "):
            flush_paragraph()
            story.append(Paragraph(inline_markup(stripped[4:]), s["h3"]))
            i += 1
            continue
        if stripped.startswith("- "):
            flush_paragraph()
            story.append(Paragraph(inline_markup(stripped[2:]), s["bullet"], bulletText="-"))
            i += 1
            continue
        if stripped.startswith("**Candidate:**"):
            flush_paragraph()
            meta_lines = []
            while i < len(lines) and lines[i].strip().startswith("**"):
                meta_lines.append(lines[i].replace("  ", " ").strip())
                i += 1
            story.append(Paragraph(" | ".join(inline_markup(x) for x in meta_lines), s["meta"]))
            continue
        paragraph_buffer.append(stripped)
        i += 1
    flush_paragraph()

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=letter,
        leftMargin=0.44 * inch,
        rightMargin=0.44 * inch,
        topMargin=0.38 * inch,
        bottomMargin=0.48 * inch,
        title="Wes Jones - Beat Claude General 000",
        author="Wes Jones",
    )
    doc.build(story, onFirstPage=page_footer, onLaterPages=page_footer)
    print(OUTPUT)


if __name__ == "__main__":
    build()

