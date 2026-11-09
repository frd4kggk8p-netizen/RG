# Project Progress: Reading Greek Study Platform

## Status Overview
- Current Phase: **GATE 2: Slice 1 Data Review & Approval (Section 6 Complete)**
- Target Slice: **Slice 1 (Section 6 end-to-end)**

---

## Phase Checklist

- [x] **Phase 0 — Recon & Setup**
  - [x] Workspace directory tree created (`source/`, `work/pages/`, `data/`, `site/`, `tools/`, `docs/`, `reports/`).
  - [x] PDFs symlinked in `source/`.
  - [x] `GEMINI_API_KEY` configured and verified against Google GenAI API.
  - [x] `docs/conventions.md` written.
  - [x] Offset mapping verified:
    - Text: `printed = PDF − 30` (offset = 30)
    - Grammar: `printed = PDF − 18` (offset = 18)
    - Guide: `printed = PDF − 14` (offset = 14)
  - [x] Scope boundaries identified (Sections 6–20).
  - [x] Page rasterisation (all Section 6 pages + 40 calibration pages at 300 DPI & 120 DPI).
  - [x] `data/manifest.json` generated.
- [x] **Phase 1 — Transcription & Calibration (GATE 1)**
  - [x] Page prompt created (`tools/page_prompt.md`).
  - [x] Dual-pass OCR runner implemented (`tools/transcribe.py`).
  - [x] Calibration dataset evaluated (38 clean Greek pages).
  - [x] Canary test on Text p. 64 (PDF p. 94) verified with 100% recovery.
  - [x] Gate 1 Calibration Report written in `reports/gate-1-calibration.md`.
- [x] **Phase 2 — Structuring (Section 6 JSON datasets)**
  - [x] Transcribed all 41 pages of Section 6 (Text, Grammar, Guide).
  - [x] `data/text/s06.json` generated (Passages 6A, 6B, 6C, 6D).
  - [x] `data/grammar/s06.json` generated (§128–§149, tables, boxes, exercises).
  - [x] `data/guide/s06.json` generated (Notes, translations, answers).
  - [x] `data/vocab/book_text.json` generated (217 vocabulary entries).
- [x] **Phase 3 — Linking & Validation (Section 6, GATE 2)**
  - [x] Tokenisation and definition chain linking (`token.entry_ids` -> vocab).
  - [x] Automated validation suite V1–V8 passed (0 charset errors, 0 NFC errors, 0 homoglyphs).
  - [x] Golden acceptance tests T1–T6 audited and confirmed.
  - [x] Gate 2 Data Review Report written in `reports/section-06.md`.
- [ ] **Phase 4 — Website & Proofread Mode (Section 6, GATE 3)**
- [ ] **Scale-out — Sections 7–20**
