# Reading Greek — Conventions & Encoding Standards

This document formalises the typographical, transliteration, and data conventions enforced across all tools, pipelines, and structured datasets in the *Reading Greek* study platform.

---

## 1. Greek Unicode Normalisation

- **Form**: Strict Unicode **NFC** (Normalization Form C) everywhere.
- **Code points**: Precomposed polytonic Greek characters in the `U+1F00`–`U+1FFF` range and standard Greek range `U+0370`–`U+03FF`.
- **NFC Mappings**:
  - Oxia is folded to tonos (`U+03AC`, etc.).
  - Greek question mark is normalized to `;` (`U+003B`).
  - Ano teleia (Greek semicolon) is normalized to `·` (`U+00B7`).
- **Apostrophes & Crasis**:
  - Elision and aphaeresis: Right single quotation mark **`’`** (`U+2019`).
  - Crasis (koronis): **`᾽`** (`U+1FBD`) only when crasis is explicitly typeset with a distinct koronis.
  - No straight ASCII apostrophes (`'`) in polytonic tokens.
- **Hyphens**:
  - Morpheme segmentations in vocabulary (`ἐ-βόησ-α`, `παύ-ομαι`) are **linguistic content**. They are preserved in `display` / `lemma_display` fields and stripped in `plain` / `lemma_plain`.
- **Tie marks**:
  - Ligature ties from the PDF text layer (e.g., `⁀` `U+2040`) are excluded unless verified to be visually printed.

---

## 2. Script Purity & Anti-Homoglyph Rules

- **Zero Tolerance for Latin/Cyrillic Homoglyphs**:
  Under no circumstances may a Greek token contain look-alikes (Latin `o`, `a`, `v`, `p`, `h`, `x`, `i`, `e` or Cyrillic `а`, `о`, `р`, `с`, `х`, `е`, `у`).
- **Validation**: Any Greek string failing regex `^[\u0370-\u03FF\u1F00-\u1FFF\u2019\u00B7\s\.,;:\-—–·’]+$` is rejected by the validation suite (V1/V3).

---

## 3. English Typographical Normalisation

- Ligatures (`ﬁ`, `ﬂ`, `ﬀ`, `ﬃ`, `ﬄ`) extracted from fonts are normalized to ASCII pairs (`fi`, `fl`, `ff`, `ffi`, `ffl`).
- Quotation marks and dashes: standard curly quotes (`“`, `”`, `‘`, `’`) and em/en dashes (`—`, `–`) are preserved as in the books.

---

## 4. Semantic Markers (Bullets, Badges & Footers)

- Drop footers containing `"Downloaded from Cambridge Books Online"`.
- Replace decorative font glyphs (which decay to `©`, `n`, `c` in corrupted text layers) with semantic marker tokens:
  - `©` / round bullet → `bullet`
  - `c` / tick/arrow → `arrow` or `check`
  - Table headers → `table-title-marker`

---

## 5. Provenance Requirements

Every atomic block, line, vocabulary item, and exercise must include provenance:
```json
"src": {
  "book": "text" | "grammar" | "guide",
  "printed_page": "63",
  "pdf_page": 93,
  "bbox": [x0, y0, x1, y1]
}
```
