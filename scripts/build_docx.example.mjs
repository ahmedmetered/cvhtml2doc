// build_docx.example.mjs — minimal editable-DOCX skeleton with the two things
// that make a rebuilt CV survive Word: an embedded font (so it renders on
// machines that don't have it) and page metrics matched to the PDF.
//
// Requires: npm install docx@9   (node build_docx.example.mjs)
// The real pipeline generates the section/content calls from the same data
// that renders the HTML — one source of truth, two renderers.
import { readFileSync } from "node:fs";
import {
  Document, Packer, Paragraph, TextRun, AlignmentType, PageBreak,
} from "docx";

const fontName = "Manrope"; // whatever your reference PDF measured
const fontData = readFileSync("./fonts/Manrope.ttf"); // variable TTF works

const NAVY = "002A52";      // from extract_tokens.py
const BODY = 10;            // sizes in HALF-points below: 10pt = 20

const p = (text, opts = {}) =>
  new Paragraph({
    spacing: { after: 40, line: 274 }, // 13.7pt leading for 10pt body
    children: [new TextRun({ text, font: fontName, size: BODY * 2, color: NAVY, ...opts })],
    ...opts.para,
  });

const doc = new Document({
  styles: { default: { document: { run: { font: fontName, size: BODY * 2, color: NAVY } } } },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },  // US Letter in twips (A4: 11906x16838)
        margin: { top: 240, bottom: 240, left: 300, right: 300 }, // 15pt ≈ 300 twips
      },
    },
    children: [
      p("Full Name", { size: 18 * 2, bold: true }),           // 18pt name
      p("email@example.com · City · +00 000 000", { size: 9 * 2 }),
      p(""), new PageBreak(),                                   // page 2 starts here
      p("Edit everything in this skeleton freely; the point is the scaffolding:"),
      p("font embedding, twip-true margins, half-point sizes, matched leading."),
    ],
  }],
  // THE key line: without this, Word substitutes a default font and the layout walks.
  fonts: [{ name: fontName, data: fontData }],
});

const buf = await Packer.toBuffer(doc);
writeFileOut: {
  const { writeFileSync } = await import("node:fs");
  writeFileSync("cv.docx", buf);
  console.log("wrote cv.docx");
}
