#!/usr/bin/env python
"""extract_tokens.py — measure a reference PDF's design tokens with PyMuPDF.

The first step of rebuilding a CV (or any single-page design) faithfully: stop
eyeballing, start measuring. This dumps the facts you need to rebuild the layout
in HTML/CSS: page size, the full color palette actually used, font names and the
exact set of sizes, and the y-position of every text line (so columns, bars,
chips and margins can be read off the numbers).

Usage:
  python extract_tokens.py reference.pdf [--page 1]

Output: a compact report to stdout. Feed it straight into your CSS variables.
"""
import sys
from collections import Counter

import pymupdf  # PyMuPDF


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    page_no = 1
    if "--page" in sys.argv:
        page_no = int(sys.argv[sys.argv.index("--page") + 1])
    if not args:
        sys.exit(__doc__)
    doc = pymupdf.open(args[0])
    page = doc[page_no - 1]

    w, h = page.rect.width, page.rect.height
    print(f"PAGE {page_no}: {w:.1f} x {h:.1f} pt ({'US Letter' if abs(w - 612) < 1 and abs(h - 792) < 1 else 'A4' if abs(w - 595) < 1 and abs(h - 842) < 1 else 'custom'})")

    colors, fonts, sizes = Counter(), Counter(), Counter()
    lines = []
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                if not span["text"].strip():
                    continue
                c = span["color"]
                colors[f"#{c >> 16 & 255:02x}{c >> 8 & 255:02x}{c & 255:02x}"] += len(span["text"])
                fonts[span["font"]] += len(span["text"])
                sizes[round(span["size"], 1)] += len(span["text"])
            # one entry per visual line: y of the top, first span's size, joined text
            spans = [s for s in line["spans"] if s["text"].strip()]
            if spans:
                lines.append((round(line["bbox"][1], 1), round(spans[0]["size"], 1), " ".join(s["text"].strip() for s in spans)[:60]))

    print("\nCOLORS (by characters):")
    for c, n in colors.most_common(8):
        print(f"  {c}  x{n}")
    print("\nFONTS:")
    for f, n in fonts.most_common(6):
        print(f"  {f}  x{n}")
    print("\nFONT SIZES (pt):")
    for s, n in sorted(sizes.items()):
        print(f"  {s}  x{n}")
    print(f"\nLINES ({len(lines)}) — y-top, size, text:")
    for y, s, t in sorted(lines):
        print(f"  y={y:7.1f}  {s:4.1f}pt  {t}")

    # vector graphics: the horizontal bars/dividers/bands of a CV layout
    ys = []
    for d in page.get_drawings():
        r = d["rect"]
        if r.width > 100 and r.height < 20:  # wide + flat = band/bar/divider/chip
            fill = d.get("fill")
            col = f"#{fill[0]*255:02.0f}{fill[1]*255:02.0f}{fill[2]*255:02.0f}" if fill else "-"
            ys.append((round(r.y0, 1), round(r.x0, 1), round(r.width, 1), round(r.height, 1), col))
    if ys:
        print("\nWIDE FLAT SHAPES (y, x, w, h, fill) — bands/bars/dividers:")
        for y in sorted(ys):
            print(f"  y={y[0]:7.1f} x={y[1]:6.1f} {y[2]:6.1f} x {y[3]:4.1f}  {y[4]}")


if __name__ == "__main__":
    main()
