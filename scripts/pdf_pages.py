#!/usr/bin/env python
"""Render selected PDF pages to PNG (drawings for the design agent) and dump their text.

  python scripts/pdf_pages.py paper.pdf out/ --pages 12,13 --dpi 220 --prefix drawing-
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pymupdf


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pdf", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--pages", default="", help="1-based page numbers, comma list; default all")
    ap.add_argument("--dpi", type=int, default=200)
    ap.add_argument("--prefix", default="page-")
    ap.add_argument("--text", action="store_true", help="also write <prefix>text.md with the extracted text of those pages")
    a = ap.parse_args(argv)
    a.out.mkdir(parents=True, exist_ok=True)
    doc = pymupdf.open(a.pdf)
    pages = [int(p) for p in a.pages.split(",") if p] or list(range(1, doc.page_count + 1))
    texts = []
    for n in pages:
        page = doc[n - 1]
        pix = page.get_pixmap(dpi=a.dpi)
        out = a.out / f"{a.prefix}{n:02d}.png"
        pix.save(out)
        print(out, pix.width, "x", pix.height)
        if a.text:
            texts.append(f"## Page {n}\n\n{page.get_text()}\n")
    if a.text:
        (a.out / f"{a.prefix}text.md").write_text("\n".join(texts), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
