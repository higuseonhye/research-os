#!/usr/bin/env python3
"""Add independent-research disclaimer to paper001_recoverability_en.pdf title page."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import fitz


DISCLAIMER = (
    "Independent research - not lab-supervised or institution-endorsed. "
    "Views are the author's and do not represent the lab."
)


def add_disclaimer(src: Path, dst: Path) -> None:
    doc = fitz.open(src)
    page = doc[0]

    # Between date line and Abstract heading (~255–278 pt on letter/A4 layout).
    rect = fitz.Rect(55, 254, 540, 276)
    page.insert_textbox(
        rect,
        DISCLAIMER,
        fontsize=8,
        fontname="helv",
        color=(0.25, 0.25, 0.25),
        align=fitz.TEXT_ALIGN_CENTER,
    )

    dst.parent.mkdir(parents=True, exist_ok=True)
    doc.save(dst, garbage=4, deflate=True)
    doc.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("src", type=Path)
    parser.add_argument(
        "-o",
        "--out",
        type=Path,
        help="Output path (default: overwrite src)",
    )
    args = parser.parse_args()
    out = args.out or args.src
    if not args.src.is_file():
        print(f"Missing: {args.src}", file=sys.stderr)
        return 1
    add_disclaimer(args.src, out)
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
