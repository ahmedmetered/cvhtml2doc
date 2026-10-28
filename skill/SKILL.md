---
name: cv-rebuild
description: Rebuild a reference document (CV, one-pager, certificate) faithfully in HTML/CSS, print it to a pixel-close PDF with a browser engine, numerically audit against the reference, and keep an editable DOCX twin. Use when someone says "match this PDF", "rebuild my CV in the same design", "the spacing is off", or asks for a document in both PDF and editable Word formats.
---

# skill: cv-rebuild

Rebuild a reference document (CV, one-pager, certificate) faithfully in HTML/CSS,
print it to a pixel-close PDF with a browser engine, numerically audit against the
reference, and keep an editable DOCX twin. Use when someone says "match this PDF",
"rebuild my CV in the same design", "the spacing is off", or asks for a document in
both PDF and editable Word formats.

## Workflow

1. **Measure.** Run `python scripts/extract_tokens.py reference.pdf` on the original.
   Record: page size (Letter/A4/custom), color palette, font names, exact sizes,
   every text line's y-position, all wide flat shapes (bands/bars/chips) with fills.
   These numbers ARE the CSS. Do not start writing HTML before this.
2. **Rebuild** the design as a single HTML file with CSS variables holding the
   measured tokens. Match the reference's spacing exactly; adapt only the content.
   Letter-spacing stays 0 unless the tokens measured otherwise (a -0.2pt tracking
   error is visible to the document's owner).
3. **Print.** `node scripts/print_pdf.mjs rebuilt.html rebuilt.pdf` (headless
   Edge/Chrome, no header/footer). If the PDF looks stale, delete and re-print —
   headless sometimes writes after exit.
4. **Audit.** `python scripts/audit_layout.py reference.pdf rebuilt.pdf` and fix the
   reported MOVED/ONLY-IN lines numerically. Repeat until "LAYOUT MATCHES". Never
   declare done from an eyeball comparison.
5. **DOCX twin.** Adapt `scripts/build_docx.example.mjs`: embed the font (docx@9
   fonts array), match page size and margins in twips, sizes in half-points, leading
   in twentieths. Word can't bleed page-edge bands — accept margin-to-margin and note it.
6. **Single source.** Generate the HTML and the DOCX section calls from one content
   file so the twins cannot drift.

## Hard rules

- Every factual claim in the document comes from the user's content, never invented.
- Language conventions belong to the user (e.g. job titles, whether a native language
  takes a CEFR level); ask, don't assume.
- Verify the output by re-reading the produced PDF, not the HTML.
