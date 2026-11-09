export type BookId = "text" | "grammar" | "guide";

export interface Src {
  book: BookId;
  printed_page: string;
  pdf_page: number;
  bbox?: [number, number, number, number];
}

export interface Uncertain {
  span: string;
  reason: string;
  candidates?: string[];
}

// ---- Text ----
export interface Token {
  id: string;
  surface: string;
  norm: string;
  entry_ids: string[];
}

export interface TextLine {
  id: string;               // e.g. "s06.6A.l012"
  n: number;                // reconstructed line number
  margin?: number;          // printed margin number (5, 10, 15...)
  speaker?: string;         // e.g. "ΣΤΡΕΨ."
  greek?: string;           // NFC
  direction?: { text: string; lang: "en" | "grc" };
  tokens?: Token[];
  src: Src;
  uncertain?: Uncertain[];
}

export interface Box {
  title: string;
  items: string[];
  kind: "grammar-ref" | "world-of-athens" | "vocab-check" | "note" | "other";
}

export interface Figure {
  id: string;
  caption?: string;
  bbox?: [number, number, number, number];
  src: Src;
}

export interface Passage {
  id: string;               // e.g. "6A"
  intro_en?: string;
  lines: TextLine[];
  vocab_ids: string[];
  boxes: Box[];
  figures: Figure[];
}

export type VocabTier = "book-text" | "book-vocab" | "lsj" | "auto";

export interface VocabEntry {
  id: string;
  display: string;          // "ἐ-βόησ-α"
  plain: string;            // "ἐβόησα"
  gloss_en: string;
  lemma_display?: string;   // "βοά-ω"
  lemma_plain?: string;     // "βοάω"
  article?: string;
  adjective_endings?: string;
  decl_code?: string;       // e.g. "2b"
  where: {
    passage: string;
    lines?: number[];
  };
  tier: VocabTier;
  src: Src;
}

// ---- Grammar ----
export interface TableCell {
  text: string;
  lang?: "grc" | "en" | "mixed";
  col_span?: number;
  row_span?: number;
}

export type Block =
  | { t: "para"; no?: number; html: string }
  | { t: "box"; title: string; items: string[]; kind: "cover" | "vocab-check" | "note" | "other" }
  | { t: "table"; caption?: string; header: string[][]; rows: TableCell[][]; col_spans?: any }
  | { t: "example"; greek?: string; en?: string }
  | { t: "list"; marker: string; items: string[] };

export interface ExerciseItem {
  n: number | string;
  prompt: string;
  lang: "grc" | "en" | "mixed";
}

export interface Exercise {
  id: string;
  instruction: string;
  items: ExerciseItem[];
  src: Src;
}

export interface Unit {
  id: string;
  label_new: string;
  label_old?: string;
  para_range: [number, number];
  blocks: Block[];
  exercises: Exercise[];
}

// ---- Guide ----
export interface GuideNote {
  passage: string;
  page_ref: string;
  line: string;
  quoted: string;
  text: string;
  src: Src;
}

export interface GuideTranslation {
  passage: string;
  paragraphs: { speaker?: string; text: string }[];
  src: Src;
}

export interface GuideAnswer {
  exercise_id: string;
  item: number | string;
  answer: string;
  src: Src;
}

export interface XRef {
  from: Src;
  to: {
    book: BookId;
    para?: number;
    page?: string;
    passage?: string;
  };
  raw: string;
}
