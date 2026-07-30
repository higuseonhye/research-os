#!/usr/bin/env python3
"""Build deterministic, root-main Overleaf upload archives for Paper 002."""

from __future__ import annotations

import argparse
import io
import re
import zipfile
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAPER_DIR = ROOT / "docs" / "paper002"
FIXED_ZIP_TIME = (2026, 7, 30, 0, 0, 0)
ALLOWED_SUFFIXES = {".tex", ".bib", ".png"}


@dataclass(frozen=True)
class ArchiveTarget:
    output: Path
    entries: tuple[tuple[str, Path], ...]
    expected_figures: int
    expects_bibliography: bool


FIGURES = tuple(sorted((PAPER_DIR / "figures").glob("fig*.png")))

TARGETS = (
    ArchiveTarget(
        output=PAPER_DIR / "paper002_overleaf_main_v1.1.zip",
        entries=(
            ("main.tex", PAPER_DIR / "paper002_manuscript_model_order_v1.1.tex"),
            ("paper002_references_v1.1.bib", PAPER_DIR / "paper002_references_v1.1.bib"),
            *((f"figures/{path.name}", path) for path in FIGURES),
        ),
        expected_figures=5,
        expects_bibliography=True,
    ),
    ArchiveTarget(
        output=PAPER_DIR / "paper002_overleaf_supplement_v1.1.zip",
        entries=(("main.tex", PAPER_DIR / "paper002_supplement_model_order_v1.1.tex"),),
        expected_figures=0,
        expects_bibliography=False,
    ),
)


def zip_info(name: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, FIXED_ZIP_TIME)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o100644 << 16
    return info


def build_archive(target: ArchiveTarget) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for name, source in target.entries:
            if not source.is_file():
                raise FileNotFoundError(source)
            archive.writestr(zip_info(name), source.read_bytes())
    payload = buffer.getvalue()
    validate_archive(payload, target)
    return payload


def validate_archive(payload: bytes, target: ArchiveTarget) -> None:
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        names = archive.namelist()
        if not names or names[0] != "main.tex" or "main.tex" not in names:
            raise ValueError(f"{target.output.name}: main.tex must be first and at ZIP root")
        if len(names) != len(set(names)):
            raise ValueError(f"{target.output.name}: duplicate archive entries")
        if any(Path(name).suffix.lower() not in ALLOWED_SUFFIXES for name in names):
            raise ValueError(f"{target.output.name}: unsupported Overleaf file type")
        if any(name.startswith("/") or ".." in Path(name).parts for name in names):
            raise ValueError(f"{target.output.name}: unsafe archive path")

        main = archive.read("main.tex").decode("utf-8")
        if "\\documentclass" not in main or "\\begin{document}" not in main:
            raise ValueError(f"{target.output.name}: root main.tex is not standalone")
        figures = re.findall(r"\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}", main)
        if len(figures) != target.expected_figures:
            raise ValueError(
                f"{target.output.name}: expected {target.expected_figures} figures, found {len(figures)}"
            )
        for figure in figures:
            if figure not in names:
                raise ValueError(f"{target.output.name}: missing referenced figure {figure}")

        has_bibliography = "\\bibliography{paper002_references_v1.1}" in main
        if has_bibliography != target.expects_bibliography:
            raise ValueError(f"{target.output.name}: bibliography expectation mismatch")
        if target.expects_bibliography and "paper002_references_v1.1.bib" not in names:
            raise ValueError(f"{target.output.name}: bibliography file missing")
        if len(payload) >= 50 * 1024 * 1024:
            raise ValueError(f"{target.output.name}: exceeds Overleaf 50 MB upload limit")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify committed ZIP files against freshly rendered archives",
    )
    args = parser.parse_args()

    for target in TARGETS:
        payload = build_archive(target)
        if args.check:
            if not target.output.is_file() or target.output.read_bytes() != payload:
                raise SystemExit(f"[FAIL] stale Overleaf archive: {target.output}")
            print(f"[OK] current: {target.output.relative_to(ROOT)}")
        else:
            target.output.write_bytes(payload)
            print(f"[OK] wrote: {target.output.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
