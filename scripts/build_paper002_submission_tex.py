#!/usr/bin/env python3
"""Build standalone Paper 002 LaTeX sources from the canonical Markdown."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from itertools import count
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAPER_DIR = ROOT / "docs" / "paper002"

CITATION_KEYS = (
    "ha2018world",
    "hafner2019planet",
    "hafner2025dreamerv3",
    "hou2026survey",
    "janner2019mbpo",
    "ljung1999system",
    "akaike1974identification",
    "ljung1978lack",
    "jacobs1991experts",
    "ostapenko2021lmc",
    "jang2026tmow",
    "jang2026musix",
    "fang2026worldscape",
    "lei2023vcd",
    "yu2024orbit",
    "owen2007pigeonhole",
    "wilson1927inference",
)

LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
IMAGE_RE = re.compile(r"^!\[([^\]]*)\]\(([^)]+)\)$")
CITATION_RE = re.compile(r"\[(\d+(?:-\d+)?(?:,\d+)*)\]")
INLINE_MATH_RE = re.compile(r"(?<!\\)\$([^$\n]+)\$")
LIST_RE = re.compile(r"^(?P<indent>\s*)(?P<mark>-|\d+\.)\s+(?P<text>.*)$")
TABLE_SEPARATOR_RE = re.compile(r"^:?-{3,}:?$")
TOKEN_SEQUENCE = count()


@dataclass(frozen=True)
class Target:
    source: Path
    output: Path
    supplement: bool


TARGETS = (
    Target(
        PAPER_DIR / "paper002_manuscript_model_order_v1.1.md",
        PAPER_DIR / "paper002_manuscript_model_order_v1.1.tex",
        False,
    ),
    Target(
        PAPER_DIR / "paper002_supplement_model_order_v1.1.md",
        PAPER_DIR / "paper002_supplement_model_order_v1.1.tex",
        True,
    ),
)


@dataclass
class Block:
    kind: str
    value: object
    level: int = 0


def is_table_start(lines: list[str], index: int) -> bool:
    if index + 1 >= len(lines) or not lines[index].lstrip().startswith("|"):
        return False
    cells = split_table_row(lines[index + 1])
    return bool(cells) and all(TABLE_SEPARATOR_RE.fullmatch(cell.strip()) for cell in cells)


def split_table_row(line: str) -> list[str]:
    value = line.strip()
    if value.startswith("|"):
        value = value[1:]
    if value.endswith("|"):
        value = value[:-1]
    return [cell.strip() for cell in value.split("|")]


def is_special(lines: list[str], index: int) -> bool:
    line = lines[index]
    return bool(
        not line.strip()
        or line.startswith("#")
        or line.startswith(">")
        or line.startswith("```")
        or IMAGE_RE.fullmatch(line.strip())
        or LIST_RE.match(line)
        or is_table_start(lines, index)
        or line.strip() == "---"
    )


def parse_blocks(source: str) -> list[Block]:
    lines = source.splitlines()
    blocks: list[Block] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        if not line.strip() or line.strip() == "---":
            index += 1
            continue

        heading = re.match(r"^(#{1,3})\s+(.+)$", line)
        if heading:
            blocks.append(Block("heading", heading.group(2).strip(), len(heading.group(1))))
            index += 1
            continue

        if line.startswith(">"):
            values: list[str] = []
            while index < len(lines) and lines[index].startswith(">"):
                values.append(lines[index][1:].strip())
                index += 1
            blocks.append(Block("quote", [value for value in values if value]))
            continue

        if line.startswith("```"):
            language = line[3:].strip()
            index += 1
            values: list[str] = []
            while index < len(lines) and not lines[index].startswith("```"):
                values.append(lines[index])
                index += 1
            if index >= len(lines):
                raise ValueError("unterminated fenced code block")
            index += 1
            blocks.append(Block("code", (language, "\n".join(values))))
            continue

        image = IMAGE_RE.fullmatch(line.strip())
        if image:
            blocks.append(Block("image", (image.group(1), image.group(2))))
            index += 1
            continue

        if is_table_start(lines, index):
            rows = [split_table_row(lines[index])]
            index += 2
            while index < len(lines) and lines[index].lstrip().startswith("|"):
                rows.append(split_table_row(lines[index]))
                index += 1
            blocks.append(Block("table", rows))
            continue

        list_match = LIST_RE.match(line)
        if list_match:
            ordered = list_match.group("mark") != "-"
            items: list[str] = []
            while index < len(lines):
                current = LIST_RE.match(lines[index])
                if current is None or (current.group("mark") != "-") != ordered:
                    break
                parts = [current.group("text").strip()]
                index += 1
                while index < len(lines) and lines[index].strip() and not LIST_RE.match(lines[index]):
                    if is_special(lines, index):
                        break
                    parts.append(lines[index].strip())
                    index += 1
                items.append(" ".join(parts))
                if index < len(lines) and not lines[index].strip():
                    probe = index + 1
                    while probe < len(lines) and not lines[probe].strip():
                        probe += 1
                    if probe >= len(lines) or not LIST_RE.match(lines[probe]):
                        break
                    index = probe
            blocks.append(Block("ordered_list" if ordered else "bullet_list", items))
            continue

        paragraph = [line.strip()]
        index += 1
        while index < len(lines) and not is_special(lines, index):
            paragraph.append(lines[index].strip())
            index += 1
        blocks.append(Block("paragraph", " ".join(paragraph)))
    return blocks


def citation_numbers(spec: str) -> list[int]:
    values: list[int] = []
    for part in spec.split(","):
        if "-" in part:
            start, end = (int(value) for value in part.split("-", 1))
            values.extend(range(start, end + 1))
        else:
            values.append(int(part))
    if not values or min(values) < 1 or max(values) > len(CITATION_KEYS):
        raise ValueError(f"citation outside 1-{len(CITATION_KEYS)}: [{spec}]")
    return values


def escape_text(value: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in value)


def link_label(value: str) -> str:
    code = re.fullmatch(r"`([^`]+)`", value)
    if code:
        return r"\texttt{\detokenize{" + code.group(1) + "}}"
    value = re.sub(r"\*\*([^*]+)\*\*", r"\1", value)
    value = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"\1", value)
    return escape_text(value)


def inline(value: str, *, citations: bool = True) -> str:
    tokens: dict[str, str] = {}

    def protect(latex: str) -> str:
        key = f"ZZLATEXTOKEN{next(TOKEN_SEQUENCE)}ZZ"
        tokens[key] = latex
        return key

    value = value.replace("\u2013", "--").replace("\u2014", "---").replace("\u2212", "-")
    for symbol, latex in (
        ("\u2192", r"\(\rightarrow\)"),
        ("\u00d7", r"\(\times\)"),
        ("\u2264", r"\(\leq\)"),
        ("\u2265", r"\(\geq\)"),
        ("\u03bc", r"\(\mu\)"),
        ("\u0394", r"\(\Delta\)"),
    ):
        value = value.replace(symbol, protect(latex))

    value = INLINE_MATH_RE.sub(
        lambda match: protect(r"\(" + match.group(1).strip() + r"\)"),
        value,
    )

    value = LINK_RE.sub(
        lambda match: protect(
            r"\href{\detokenize{" + match.group(2) + "}}{" + link_label(match.group(1)) + "}"
        ),
        value,
    )
    value = re.sub(
        r"`([^`]+)`",
        lambda match: protect(r"\texttt{\detokenize{" + match.group(1) + "}}"),
        value,
    )
    if citations:
        value = CITATION_RE.sub(
            lambda match: protect(
                r"\cite{" + ",".join(CITATION_KEYS[number - 1] for number in citation_numbers(match.group(1))) + "}"
            ),
            value,
        )
    value = re.sub(
        r"\*\*([^*]+)\*\*",
        lambda match: protect(r"\textbf{" + escape_text(match.group(1)) + "}"),
        value,
    )
    value = re.sub(
        r"(?<!\*)\*([^*]+)\*(?!\*)",
        lambda match: protect(r"\emph{" + escape_text(match.group(1)) + "}"),
        value,
    )
    for pattern, replacement in (
        (r"\bp_\(t-1\)", r"\(p_{t-1}\)"),
        (r"\bp_\(t\+H\)", r"\(p_{t+H}\)"),
        (r"\b([pds])_t\b", r"\(\1_t\)"),
        (r"\bH=10\b", r"\(H=10\)"),
    ):
        value = re.sub(pattern, lambda match, rep=replacement: protect(match.expand(rep)), value)

    rendered = escape_text(value)
    for key, latex in tokens.items():
        rendered = rendered.replace(key, latex)
    return rendered


def strip_heading_number(value: str, supplement: bool) -> str:
    pattern = r"^S\d+\.\s+" if supplement else r"^\d+(?:\.\d+)*\.?\s+"
    return re.sub(pattern, "", value)


def caption_parts(value: str, kind: str) -> tuple[str | None, str]:
    match = re.match(rf"^\*\*{kind}\s+([^.]*)\.\*\*\s*(.*)$", value)
    if match is None:
        return None, value
    return match.group(1).strip().lower().replace(" ", "-"), match.group(2).strip()


def render_table(rows: list[list[str]], caption: str | None, label: str | None) -> str:
    width = max(len(row) for row in rows)
    normalized = [row + [""] * (width - len(row)) for row in rows]
    size = r"\scriptsize" if width >= 6 else r"\small"
    columns = "@{}" + " ".join([r">{\raggedright\arraybackslash}X"] * width) + "@{}"
    lines = [r"\begin{table}[htbp]", r"\centering", size]
    if caption:
        lines.append(r"\caption{" + inline(caption, citations=False) + "}")
    if label:
        lines.append(r"\label{tab:" + label + "}")
    lines.extend([r"\begin{tabularx}{\textwidth}{" + columns + "}", r"\toprule"])
    lines.append(" & ".join(inline(cell) for cell in normalized[0]) + r" \\")
    lines.append(r"\midrule")
    for row in normalized[1:]:
        lines.append(" & ".join(inline(cell) for cell in row) + r" \\")
    lines.extend([r"\bottomrule", r"\end{tabularx}", r"\end{table}"])
    return "\n".join(lines)


def render_figure(path: str, caption: str | None, label: str | None, alt: str) -> str:
    lines = [
        r"\begin{figure}[htbp]",
        r"\centering",
        r"\includegraphics[width=0.96\linewidth]{" + path.replace("\\", "/") + "}",
    ]
    lines.append(r"\caption{" + inline(caption or alt, citations=False) + "}")
    if label:
        lines.append(r"\label{fig:" + label + "}")
    lines.append(r"\end{figure}")
    return "\n".join(lines)


def preamble(title: str, supplement: bool, source_name: str) -> str:
    supplement_numbering = r"\renewcommand{\thesection}{S\arabic{section}}" if supplement else ""
    return f"""% Generated from {source_name} by scripts/build_paper002_submission_tex.py.
% The Markdown and BibTeX files remain the synchronized content sources.
\\documentclass[10pt]{{article}}
\\usepackage[a4paper,margin=25mm]{{geometry}}
\\usepackage[T1]{{fontenc}}
\\usepackage[utf8]{{inputenc}}
\\usepackage{{amsmath,amssymb}}
\\usepackage{{graphicx}}
\\usepackage{{booktabs,tabularx,array}}
\\usepackage{{enumitem}}
\\usepackage{{fancyvrb}}
\\usepackage{{caption}}
\\usepackage[numbers,sort&compress]{{natbib}}
\\usepackage{{xurl}}
\\usepackage[colorlinks=true,allcolors=blue]{{hyperref}}
\\setlength{{\\parindent}}{{0pt}}
\\setlength{{\\parskip}}{{0.55em}}
\\renewcommand{{\\arraystretch}}{{1.12}}
\\graphicspath{{{{figures/}}}}
{supplement_numbering}
\\title{{{inline(title, citations=False)}}}
\\author{{Author and affiliation omitted pending venue selection}}
\\date{{}}
\\begin{{document}}
\\maketitle
"""


def render_document(source_path: Path, supplement: bool) -> str:
    blocks = parse_blocks(source_path.read_text(encoding="utf-8"))
    if not blocks or blocks[0].kind != "heading" or blocks[0].level != 1:
        raise ValueError(f"missing document title in {source_path}")
    title = str(blocks[0].value)
    output = [preamble(title, supplement, source_path.name)]
    in_abstract = False
    index = 1
    while index < len(blocks):
        block = blocks[index]
        if block.kind == "heading":
            heading = str(block.value)
            if not supplement and heading == "References":
                break
            if not supplement and heading == "Abstract":
                output.append(r"\begin{abstract}")
                in_abstract = True
                index += 1
                continue
            if in_abstract:
                output.append(r"\end{abstract}")
                in_abstract = False
            clean = strip_heading_number(heading, supplement)
            command = "section" if block.level == 2 else "subsection"
            if clean == "Ethics, Data, Code, And Reproducibility":
                command = "section*"
            output.append("\\" + command + "{" + inline(clean, citations=False) + "}")
            index += 1
            continue

        if block.kind == "quote":
            values = [str(value) for value in block.value if not str(value).startswith("Author and affiliation")]
            if values:
                output.extend([r"\begin{center}", r"\small"])
                output.append(r" \\".join(inline(value) for value in values))
                output.append(r"\end{center}")
            index += 1
            continue

        if block.kind == "code":
            language, code = block.value
            if language == "math":
                output.append(
                    "\n".join([r"\begin{align*}", str(code), r"\end{align*}"])
                )
            else:
                output.append(
                    "\n".join(
                        [
                            r"\begin{Verbatim}[fontsize=\small]",
                            str(code),
                            r"\end{Verbatim}",
                        ]
                    )
                )
            index += 1
            continue

        if block.kind == "image":
            alt, path = (str(value) for value in block.value)
            caption = None
            label = None
            if index + 1 < len(blocks) and blocks[index + 1].kind == "paragraph":
                label, caption = caption_parts(str(blocks[index + 1].value), "Figure")
                if label is not None:
                    index += 1
            output.append(render_figure(path, caption, label, alt))
            index += 1
            continue

        if block.kind == "paragraph":
            table_label, table_caption = caption_parts(str(block.value), "Table")
            if table_label is not None and index + 1 < len(blocks) and blocks[index + 1].kind == "table":
                output.append(render_table(blocks[index + 1].value, table_caption, table_label))
                index += 2
                continue
            output.append(inline(str(block.value)))
            index += 1
            continue

        if block.kind == "table":
            output.append(render_table(block.value, None, None))
            index += 1
            continue

        if block.kind in {"ordered_list", "bullet_list"}:
            environment = "enumerate" if block.kind == "ordered_list" else "itemize"
            output.append(r"\begin{" + environment + "}[leftmargin=*]")
            output.extend(r"\item " + inline(str(item)) for item in block.value)
            output.append(r"\end{" + environment + "}")
            index += 1
            continue

        raise ValueError(f"unsupported block: {block.kind}")

    if in_abstract:
        output.append(r"\end{abstract}")
    if not supplement:
        output.extend(
            [
                r"\bibliographystyle{unsrtnat}",
                r"\bibliography{paper002_references_v1.1}",
            ]
        )
    output.append(r"\end{document}")
    return "\n\n".join(output) + "\n"


def bib_keys(path: Path) -> set[str]:
    return set(re.findall(r"@[A-Za-z]+\{([^,]+),", path.read_text(encoding="utf-8")))


def validate_tex(tex: str, output_path: Path) -> None:
    stack: list[str] = []
    for match in re.finditer(r"\\(begin|end)\{([^}]+)\}", tex):
        action, environment = match.groups()
        if action == "begin":
            stack.append(environment)
        elif not stack or stack.pop() != environment:
            raise ValueError(f"environment mismatch near {match.group(0)} in {output_path.name}")
    if stack:
        raise ValueError(f"unclosed environments in {output_path.name}: {stack}")

    depth = 0
    escaped = False
    for char in tex:
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth < 0:
                raise ValueError(f"unbalanced closing brace in {output_path.name}")
    if depth:
        raise ValueError(f"unbalanced braces in {output_path.name}: depth={depth}")

    known_keys = bib_keys(PAPER_DIR / "paper002_references_v1.1.bib")
    used_keys = {
        key
        for group in re.findall(r"\\cite\{([^}]+)\}", tex)
        for key in group.split(",")
    }
    missing_keys = used_keys - known_keys
    if missing_keys:
        raise ValueError(f"unknown BibTeX keys in {output_path.name}: {sorted(missing_keys)}")

    for relative in re.findall(r"\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}", tex):
        if not (output_path.parent / relative).exists():
            raise ValueError(f"missing figure in {output_path.name}: {relative}")
    if "ZZLATEXTOKEN" in tex:
        raise ValueError(f"unresolved inline token in {output_path.name}")
    if "```" in tex or re.search(r"(?m)^#{1,3}\s", tex):
        raise ValueError(f"unconverted Markdown marker in {output_path.name}")
    for body in re.findall(r"\\begin\{align\*\}(.*?)\\end\{align\*\}", tex, re.DOTALL):
        if not body.strip() or "\n\n" in body:
            raise ValueError(f"invalid blank paragraph in math block in {output_path.name}")
    if re.search(r"\b(?:p_hat|v_hat|p_\(t|alpha \*|beta \*)", tex):
        raise ValueError(f"unconverted pseudo-math notation in {output_path.name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify that committed TeX matches freshly rendered output",
    )
    args = parser.parse_args()

    for target in TARGETS:
        rendered = render_document(target.source, target.supplement)
        validate_tex(rendered, target.output)
        if args.check:
            if not target.output.exists() or target.output.read_text(encoding="utf-8") != rendered:
                raise SystemExit(f"[FAIL] stale LaTeX output: {target.output}")
            print(f"[OK] current: {target.output.relative_to(ROOT)}")
        else:
            target.output.write_text(rendered, encoding="utf-8", newline="\n")
            print(f"[OK] wrote: {target.output.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
