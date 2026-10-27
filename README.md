# cvhtml2doc

**Rebuild a CV (or any one-to-two-page design) faithfully in HTML, print it to a pixel-close PDF, and keep an editable DOCX alongside. Numeric audits, not eyeballing.**

Born from a real failure: an AI-rebuilt CV that "looked about right" and was rejected ("a lot of things are off"). The fix was to stop eyeballing and start measuring — extract the reference PDF's exact tokens with PyMuPDF, rebuild in HTML, print with the same browser engine, then diff the two PDFs line-by-line by y-position and font size until the audit is clean.

## The pipeline

```
reference.pdf ──extract_tokens.py──▶ design tokens (page size, colors, fonts, sizes,
                                      every line's y, all bars/bands/chips)
        │
        ▼
   rebuild as HTML/CSS (the tokens ARE your CSS variables)
        │
        ├──print_pdf.mjs──▶ rebuilt.pdf   (headless Edge/Chrome, no header/footer)
        │
        └──audit_layout.py reference.pdf rebuilt.pdf
                │   MOVED ref y=712 10pt -> new y=702 9.5pt | ...
                ▼   fix → re-print → re-audit → until "LAYOUT MATCHES"
   build_docx.example.mjs ──▶ cv.docx (editable twin: embedded font, twip-true metrics)
```

## Scripts

| Script | What it does |
|---|---|
| `scripts/extract_tokens.py` | PyMuPDF dump of a PDF's design tokens: page size, color palette by usage, fonts, exact sizes, every text line's y-position, all wide flat shapes (bands/bars/chips) with fills |
| `scripts/audit_layout.py` | Numeric diff of two PDFs: per-page line matching by text, reporting any line whose y-position or size moved beyond tolerance. Exit 1 on mismatch — loop-friendly |
| `scripts/print_pdf.mjs` | Headless Edge/Chrome print-to-PDF with no header/footer margins; finds a browser automatically on Windows, honors `CHROME_BIN` |
| `scripts/build_docx.example.mjs` | Editable-DOCX skeleton with the two survival details: **embedded font** (`docx@9` fonts array — without it Word substitutes and the layout walks) and twip-true page metrics |

## Requirements

Python 3 with `pymupdf` (`pip install pymupdf`), Node 18+, and any Chromium-family browser (Edge ships with Windows). The DOCX step additionally needs `npm install docx@9` and Microsoft Word only if you want to re-export the DOCX to PDF via COM.

## The method, in six rules

1. **Measure the reference first.** `extract_tokens.py` on the original PDF gives you page size, the exact palette, the exact font sizes, and every line's y — that document is your CSS.
2. **Rebuild in HTML/CSS**, mapping tokens to variables. Match template spacing before adapting content; never compress spacing to force content to fit.
3. **Print with `print_pdf.mjs`** — same engine you designed in, no header/footer surprises.
4. **Audit with `audit_layout.py`** and fix numbers, not vibes. "Still spacing issues" is not actionable; "page 2 starts at y=10 instead of y=25" is.
5. **Keep the DOCX twin** with the font embedded and page metrics in twips matched to the PDF (15pt = 300 twips margins, sizes in half-points).
6. **One content source, two renderers**: generate both the HTML and the DOCX section calls from the same data file so the twins can't drift.

## Lessons baked into the scripts (from a real rebuild)

- An added `-0.2pt` letter-spacing on the name made it 6.3pt narrower than the original — the owner noticed. Set `letter-spacing: 0` unless measured otherwise.
- Numeric audits catch what eyes miss: page 2 starting at y=10 instead of y=25, over-compressed chip pitch, dividers a point off.
- Word cannot bleed a header band to the page edge (HTML can) — the DOCX band runs margin-to-margin; accept it and note it.
- Headless print sometimes writes the PDF after reporting exit — if a result looks stale, delete and re-print.

## License

MIT.
