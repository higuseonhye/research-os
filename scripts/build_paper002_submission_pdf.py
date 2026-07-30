#!/usr/bin/env python3
"""Build venue-neutral Paper 002 review PDFs from the canonical Markdown."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
from dataclasses import dataclass
from pathlib import Path
from reportlab import rl_config
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    Image,
    KeepTogether,
    PageTemplate,
    Paragraph,
    Preformatted,
    Spacer,
    Table,
    TableStyle,
)


LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
IMAGE_RE = re.compile(r"^!\[([^\]]*)\]\(([^)]+)\)$")
TABLE_SEPARATOR_RE = re.compile(r"^:?-{3,}:?$")

# Stable timestamps and document identifiers make repeated builds byte-identical.
rl_config.invariant = True


@dataclass(frozen=True)
class BuildTarget:
    source: Path
    output: Path
    short_title: str


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inline_markup(text: str) -> str:
    value = html.escape(text.strip(), quote=True)
    value = LINK_RE.sub(
        lambda match: (
            f'<link href="{match.group(2)}" color="#145a7a">'
            f"{match.group(1)}</link>"
        ),
        value,
    )
    value = re.sub(r"`([^`]+)`", r'<font name="Courier">\1</font>', value)
    value = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", value)
    value = re.sub(r"(?<!\*)\*([^*]+)\*", r"<i>\1</i>", value)
    return value


def styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    body = ParagraphStyle(
        "PaperBody",
        parent=base["BodyText"],
        fontName="Times-Roman",
        fontSize=9.4,
        leading=12.2,
        spaceAfter=4.5,
        alignment=TA_LEFT,
        textColor=colors.HexColor("#17212b"),
        allowWidows=0,
        allowOrphans=0,
    )
    return {
        "title": ParagraphStyle(
            "PaperTitle",
            parent=body,
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=21,
            alignment=TA_CENTER,
            spaceAfter=7 * mm,
            textColor=colors.HexColor("#102a43"),
        ),
        "h1": ParagraphStyle(
            "PaperH1",
            parent=body,
            fontName="Helvetica-Bold",
            fontSize=12.4,
            leading=15,
            spaceBefore=5 * mm,
            spaceAfter=2.2 * mm,
            textColor=colors.HexColor("#102a43"),
            keepWithNext=True,
        ),
        "h2": ParagraphStyle(
            "PaperH2",
            parent=body,
            fontName="Helvetica-Bold",
            fontSize=10.4,
            leading=13,
            spaceBefore=3.3 * mm,
            spaceAfter=1.4 * mm,
            textColor=colors.HexColor("#243b53"),
            keepWithNext=True,
        ),
        "body": body,
        "meta": ParagraphStyle(
            "PaperMeta",
            parent=body,
            fontName="Helvetica",
            fontSize=8.2,
            leading=10.5,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#52616b"),
            spaceAfter=1.5 * mm,
        ),
        "caption": ParagraphStyle(
            "PaperCaption",
            parent=body,
            fontName="Times-Italic",
            fontSize=8.1,
            leading=10.2,
            leftIndent=6 * mm,
            rightIndent=6 * mm,
            spaceBefore=1.2 * mm,
            spaceAfter=4 * mm,
            textColor=colors.HexColor("#334e68"),
        ),
        "bullet": ParagraphStyle(
            "PaperBullet",
            parent=body,
            leftIndent=5 * mm,
            firstLineIndent=-3.5 * mm,
            bulletIndent=1.5 * mm,
            spaceAfter=2.3,
        ),
        "code": ParagraphStyle(
            "PaperCode",
            parent=body,
            fontName="Courier",
            fontSize=7.8,
            leading=10,
            leftIndent=5 * mm,
            rightIndent=5 * mm,
            borderColor=colors.HexColor("#bcccdc"),
            borderWidth=0.5,
            borderPadding=5,
            backColor=colors.HexColor("#f5f7fa"),
            spaceBefore=2 * mm,
            spaceAfter=3 * mm,
        ),
    }


def page_decor(canvas, doc, short_title: str) -> None:
    canvas.saveState()
    width, height = A4
    canvas.setStrokeColor(colors.HexColor("#bcccdc"))
    canvas.setLineWidth(0.4)
    canvas.line(18 * mm, height - 13 * mm, width - 18 * mm, height - 13 * mm)
    canvas.setFillColor(colors.HexColor("#52616b"))
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(18 * mm, height - 10 * mm, short_title)
    canvas.drawRightString(width - 18 * mm, 10 * mm, f"Page {doc.page}")
    canvas.restoreState()


class PaperDocTemplate(BaseDocTemplate):
    def __init__(self, filename: str, short_title: str, **kwargs) -> None:
        super().__init__(filename, pagesize=A4, **kwargs)
        frame = Frame(
            18 * mm,
            17 * mm,
            A4[0] - 36 * mm,
            A4[1] - 33 * mm,
            id="main",
            topPadding=3 * mm,
            bottomPadding=3 * mm,
        )
        self.addPageTemplates(
            [
                PageTemplate(
                    id="paper",
                    frames=[frame],
                    onPage=lambda canvas, doc: page_decor(canvas, doc, short_title),
                )
            ]
        )


def parse_table(lines: list[str], style_map: dict[str, ParagraphStyle]) -> Table:
    rows: list[list[Paragraph]] = []
    for index, line in enumerate(lines):
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if index == 1 and all(TABLE_SEPARATOR_RE.match(cell) for cell in cells):
            continue
        cell_style = ParagraphStyle(
            f"TableCell{index}",
            parent=style_map["body"],
            fontName="Helvetica-Bold" if index == 0 else "Helvetica",
            fontSize=7.15,
            leading=8.7,
            textColor=colors.white if index == 0 else colors.HexColor("#17212b"),
        )
        rows.append([Paragraph(inline_markup(cell), cell_style) for cell in cells])

    column_count = max(len(row) for row in rows)
    for row in rows:
        while len(row) < column_count:
            row.append(Paragraph("", style_map["body"]))
    widths = [(A4[0] - 42 * mm) / column_count] * column_count
    table = Table(rows, colWidths=widths, repeatRows=1, hAlign="CENTER")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#243b53")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f7fa")]),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#bcccdc")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def markdown_story(source: Path) -> list:
    style_map = styles()
    lines = source.read_text(encoding="utf-8").splitlines()
    story: list = []
    paragraph: list[str] = []
    in_code = False
    code_lines: list[str] = []
    index = 0

    def flush_paragraph() -> None:
        if paragraph:
            story.append(Paragraph(inline_markup(" ".join(paragraph)), style_map["body"]))
            paragraph.clear()

    while index < len(lines):
        raw = lines[index]
        stripped = raw.strip()

        if stripped.startswith("```"):
            flush_paragraph()
            if in_code:
                story.append(Preformatted("\n".join(code_lines), style_map["code"]))
                code_lines.clear()
                in_code = False
            else:
                in_code = True
            index += 1
            continue
        if in_code:
            code_lines.append(raw)
            index += 1
            continue

        if not stripped:
            flush_paragraph()
            index += 1
            continue

        image_match = IMAGE_RE.match(stripped)
        if image_match:
            flush_paragraph()
            image_path = (source.parent / image_match.group(2)).resolve()
            if not image_path.is_file():
                raise FileNotFoundError(f"missing manuscript image: {image_path}")
            figure = Image(str(image_path))
            max_width = A4[0] - 44 * mm
            max_height = 165 * mm
            scale = min(max_width / figure.imageWidth, max_height / figure.imageHeight, 1.0)
            figure.drawWidth = figure.imageWidth * scale
            figure.drawHeight = figure.imageHeight * scale
            figure.hAlign = "CENTER"
            story.append(Spacer(1, 2 * mm))
            story.append(figure)
            index += 1
            continue

        if stripped.startswith("# "):
            flush_paragraph()
            story.append(Paragraph(inline_markup(stripped[2:]), style_map["title"]))
            index += 1
            continue
        if stripped.startswith("## "):
            flush_paragraph()
            story.append(Paragraph(inline_markup(stripped[3:]), style_map["h1"]))
            story.append(HRFlowable(width="100%", thickness=0.45, color=colors.HexColor("#9fb3c8")))
            index += 1
            continue
        if stripped.startswith("### "):
            flush_paragraph()
            story.append(Paragraph(inline_markup(stripped[4:]), style_map["h2"]))
            index += 1
            continue
        if stripped.startswith(">"):
            flush_paragraph()
            content = stripped.lstrip(">").strip()
            if content:
                story.append(Paragraph(inline_markup(content), style_map["meta"]))
            index += 1
            continue
        if stripped == "---":
            flush_paragraph()
            story.append(Spacer(1, 1.5 * mm))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#9fb3c8")))
            story.append(Spacer(1, 1.5 * mm))
            index += 1
            continue
        if stripped.startswith("|"):
            flush_paragraph()
            table_lines: list[str] = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                table_lines.append(lines[index])
                index += 1
            story.append(Spacer(1, 1.5 * mm))
            story.append(parse_table(table_lines, style_map))
            story.append(Spacer(1, 3 * mm))
            continue
        if stripped.startswith("**Figure") or stripped.startswith("**Table"):
            flush_paragraph()
            index += 1
            caption_lines = [stripped]
            while index < len(lines) and lines[index].strip():
                caption_lines.append(lines[index].strip())
                index += 1
            story.append(
                Paragraph(inline_markup(" ".join(caption_lines)), style_map["caption"])
            )
            continue

        bullet_match = re.match(r"^[-*]\s+(.*)$", stripped)
        numbered_match = re.match(r"^(\d+)\.\s+(.*)$", stripped)
        if bullet_match:
            flush_paragraph()
            story.append(
                Paragraph(inline_markup(bullet_match.group(1)), style_map["bullet"], bulletText="-")
            )
            index += 1
            continue
        if numbered_match:
            flush_paragraph()
            story.append(
                Paragraph(
                    inline_markup(numbered_match.group(2)),
                    style_map["bullet"],
                    bulletText=f"{numbered_match.group(1)}.",
                )
            )
            index += 1
            continue

        if stripped.startswith("**") and stripped.endswith("**"):
            flush_paragraph()
            story.append(Paragraph(inline_markup(stripped), style_map["h2"]))
            index += 1
            continue

        paragraph.append(stripped)
        index += 1

    flush_paragraph()
    return story


def build_pdf(target: BuildTarget) -> None:
    target.output.parent.mkdir(parents=True, exist_ok=True)
    document = PaperDocTemplate(
        str(target.output),
        short_title=target.short_title,
        title=target.short_title,
        author="Anonymous review copy",
        subject="Paper 002 model-order confirmatory study",
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=17 * mm,
        bottomMargin=16 * mm,
    )
    document.build(markdown_story(target.source))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="research-os repository root",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repo = args.repo.resolve()
    paper_dir = repo / "docs" / "paper002"
    targets = [
        BuildTarget(
            source=paper_dir / "paper002_manuscript_model_order_v1.1.md",
            output=paper_dir / "paper002_manuscript_model_order_v1.1.pdf",
            short_title="Paper 002 - Model-Order Expansion",
        ),
        BuildTarget(
            source=paper_dir / "paper002_supplement_model_order_v1.1.md",
            output=paper_dir / "paper002_supplement_model_order_v1.1.pdf",
            short_title="Paper 002 - Supplementary Material",
        ),
    ]
    for target in targets:
        build_pdf(target)
        print(f"[OK] {target.output}")

    references = paper_dir / "paper002_references_v1.1.bib"
    manifest = {
        "version": "paper002-submission-v1.1",
        "sources": {str(target.source.relative_to(repo)): sha256(target.source) for target in targets},
        "bibliography": {str(references.relative_to(repo)): sha256(references)},
        "outputs": {str(target.output.relative_to(repo)): sha256(target.output) for target in targets},
    }
    manifest_path = paper_dir / "paper002_submission_build_v1.1.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"[OK] {manifest_path}")


if __name__ == "__main__":
    main()
