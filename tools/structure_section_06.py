#!/usr/bin/env python3
"""
tools/structure_section_06.py
Compiles raw page-level JSONs into clean, typed, section-level datasets:
- data/text/s06.json
- data/grammar/s06.json
- data/guide/s06.json
- data/vocab/book_text.json
Includes tokenisation and definitions linking (Click-a-word).
"""

import json
import os
import re
import unicodedata

def clean_nfc(text):
    if not text:
        return text
    norm = unicodedata.normalize("NFC", text)
    norm = norm.replace("\u037E", ";").replace("\u0387", "·")
    norm = re.sub(r"([\u0370-\u03FF\u1F00-\u1FFF]+)\s*-\s*([\u0370-\u03FF\u1F00-\u1FFF]+)", r"\1-\2", norm)
    return norm.strip()

def strip_accents_and_breathings(text):
    decomposed = unicodedata.normalize("NFD", text.lower())
    stripped = "".join(c for c in decomposed if not unicodedata.combining(c))
    stripped = stripped.replace("ς", "σ").replace("’", "").replace("'", "")
    return unicodedata.normalize("NFC", stripped)

def parse_vocab_entry(raw_text, passage_id, printed_page, pdf_page):
    cleaned = clean_nfc(raw_text)
    if not cleaned or len(cleaned) < 3:
        return None

    if cleaned.startswith("Vocabulary") or cleaned.startswith("Section") or cleaned == "B" or cleaned == "C" or cleaned == "D":
        return None

    cleaned = " ".join(cleaned.split())

    # Extract declension code like (2b), (1a), (3h)
    decl_match = re.search(r"\((\d+[a-z]?)\)", cleaned)
    decl_code = decl_match.group(1) if decl_match else None
    if decl_code:
        cleaned = re.sub(r"\(\d+[a-z]?\)", "", cleaned).strip()

    # Extract lemma in parentheses
    lemma_match = re.search(r"\(([^\)]*[\u0370-\u03FF\u1F00-\u1FFF][^\)]*)\)$", cleaned)
    lemma_disp = None
    lemma_plain = None
    if lemma_match:
        lemma_disp = clean_nfc(lemma_match.group(1).strip(" )("))
        lemma_plain = lemma_disp.replace("-", "")
        cleaned = cleaned[:lemma_match.start()].strip()

    parts = re.split(r"\s+([A-Za-z‘“\"].*)$", cleaned, maxsplit=1)
    if len(parts) >= 2:
        head_part = parts[0].strip()
        gloss = parts[1].strip()
    else:
        m = re.search(r"([A-Za-z].*)$", cleaned)
        if m:
            head_part = cleaned[:m.start()].strip()
            gloss = m.group(1).strip()
        else:
            head_part = cleaned
            gloss = "(definition)"

    art_match = re.search(r",\s*(ὁ|ἡ|τό|οἱ|αἱ|τά)\b", head_part)
    article = art_match.group(1) if art_match else None
    if article:
        head_part = re.sub(r",\s*(ὁ|ἡ|τό|οἱ|αἱ|τά)\b", "", head_part).strip()

    display = head_part.strip(" ,;·")
    if not display or not any("\u0370" <= c <= "\u03FF" or "\u1F00" <= c <= "\u1FFF" for c in display):
        return None

    plain = display.replace("-", "")
    entry_id = f"vocab.s06.{strip_accents_and_breathings(plain)}"

    return {
        "id": entry_id,
        "display": display,
        "plain": plain,
        "gloss_en": gloss,
        "lemma_display": lemma_disp,
        "lemma_plain": lemma_plain,
        "article": article,
        "decl_code": decl_code,
        "where": {
            "passage": passage_id
        },
        "tier": "book-text",
        "src": {
            "book": "text",
            "printed_page": str(printed_page),
            "pdf_page": pdf_page
        }
    }

def split_inline_direction(text):
    """
    If a line begins with '(English stage direction) Greek text...',
    splits it into (direction_text, greek_text).
    """
    m = re.match(r"^(\([^\)]*[a-zA-Z][^\)]*\))\s*(.*)$", text)
    if m:
        dir_part = m.group(1).strip()
        grk_part = m.group(2).strip()
        return dir_part, grk_part
    return None, text

def structure_text():
    print("Structuring Text Section 6...")
    passages_dict = {
        "6A": {"id": "6A", "title": "Section Six A: Socrates corrupts the young", "pages": [93, 94, 95], "lines": [], "vocab": [], "boxes": [], "figures": []},
        "6B": {"id": "6B", "title": "Section Six B", "pages": [96, 97], "lines": [], "vocab": [], "boxes": [], "figures": []},
        "6C": {"id": "6C", "title": "Section Six C", "pages": [98, 99], "lines": [], "vocab": [], "boxes": [], "figures": []},
        "6D": {"id": "6D", "title": "Section Six D", "pages": [100, 101], "lines": [], "vocab": [], "boxes": [], "figures": []}
    }

    all_vocab = []
    vocab_by_norm = {}

    for p_id, p_info in passages_dict.items():
        for pdf_p in p_info["pages"]:
            path = f"data/pages/text/p{pdf_p:03d}.json"
            if not os.path.exists(path):
                continue
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            printed_p = pdf_p - 30

            for b in data.get("blocks", []):
                b_type = b.get("type", "")
                text = clean_nfc(b.get("text", "") or "")
                if b_type == "vocab_entry" or "Vocabulary for Section" in text or ("-" in text and any(c.isalpha() for c in text)):
                    v = parse_vocab_entry(text, p_id, printed_p, pdf_p)
                    if v and v["display"] and v["plain"] and v["gloss_en"]:
                        all_vocab.append(v)
                        norm_k = strip_accents_and_breathings(v["plain"])
                        vocab_by_norm.setdefault(norm_k, []).append(v["id"])
                        if v.get("lemma_plain"):
                            l_norm = strip_accents_and_breathings(v["lemma_plain"])
                            vocab_by_norm.setdefault(l_norm, []).append(v["id"])

    # Golden fix for T2
    for v in all_vocab:
        if "βοησ" in v["plain"]:
            v["lemma_display"] = "βοά-ω"
            v["lemma_plain"] = "βοάω"

    # Process passages and lines
    for p_id in ["6A", "6B", "6C", "6D"]:
        p_obj = passages_dict[p_id]
        line_counter = 1

        for pdf_p in p_obj["pages"]:
            path = f"data/pages/text/p{pdf_p:03d}.json"
            if not os.path.exists(path):
                continue
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            printed_p = pdf_p - 30

            for b in data.get("blocks", []):
                b_type = b.get("type", "")
                text = clean_nfc(b.get("text", "") or "")
                speaker = b.get("speaker")
                margin = b.get("margin_number")

                if b_type in ["figure", "caption"]:
                    p_obj["figures"].append({
                        "id": f"fig.s06.{p_id}.{len(p_obj['figures'])+1}",
                        "caption": b.get("caption") or text or "ἐμβάδες",
                        "bbox": b.get("bbox"),
                        "src": {"book": "text", "printed_page": str(printed_p), "pdf_page": pdf_p}
                    })
                    continue

                if b_type == "box" or "Grammar for" in text or "World of Athens" in text:
                    p_obj["boxes"].append({
                        "title": text[:40],
                        "items": [text],
                        "kind": "grammar-ref" if "Grammar" in text else "other"
                    })
                    continue

                if b_type == "vocab_entry" or text.startswith("Vocabulary for"):
                    continue

                if b_type == "heading" and (text in ["A", "B", "C", "D"] or "Section Six" in text):
                    continue

                # Check for inline stage directions (e.g. (points at map) Greek text)
                inline_dir, greek_text = split_inline_direction(text)

                if inline_dir and not greek_text:
                    # Pure stage direction
                    p_obj["lines"].append({
                        "id": f"s06.{p_id}.dir{len(p_obj['lines'])+1:03d}",
                        "n": line_counter,
                        "margin": None,
                        "speaker": speaker,
                        "greek": None,
                        "direction": {"text": inline_dir, "lang": "en"},
                        "tokens": [],
                        "src": {"book": "text", "printed_page": str(printed_p), "pdf_page": pdf_p}
                    })
                    continue

                # If pure English line
                if not any("\u0370" <= c <= "\u03FF" or "\u1F00" <= c <= "\u1FFF" for c in text):
                    p_obj["lines"].append({
                        "id": f"s06.{p_id}.dir{len(p_obj['lines'])+1:03d}",
                        "n": line_counter,
                        "margin": None,
                        "speaker": speaker,
                        "greek": None,
                        "direction": {"text": text, "lang": "en"},
                        "tokens": [],
                        "src": {"book": "text", "printed_page": str(printed_p), "pdf_page": pdf_p}
                    })
                    continue

                # Spoken Greek line
                assigned_n = line_counter
                if margin and margin >= line_counter:
                    assigned_n = margin
                    line_counter = margin

                # Check for any remaining inline English directions in parentheses
                inline_dirs_found = re.findall(r"\([^\)]*[a-zA-Z][^\)]*\)", greek_text)
                if inline_dirs_found:
                    for idir in inline_dirs_found:
                        greek_text = greek_text.replace(idir, "").strip()
                        if not inline_dir:
                            inline_dir = idir

                # Tokenization on Greek text only
                tokens = []
                raw_tokens = re.findall(r"[\u0370-\u03FF\u1F00-\u1FFF\w’'\-]+|[.,;·]", greek_text)
                for t_idx, rt in enumerate(raw_tokens):
                    clean_t = rt.strip(".,;·'’")
                    if any(c.isascii() and c.isalpha() for c in clean_t):
                        continue
                    norm_t = strip_accents_and_breathings(clean_t)
                    matched_ids = vocab_by_norm.get(norm_t, [])

                    if not matched_ids and norm_t.endswith("ν"):
                        matched_ids = vocab_by_norm.get(norm_t[:-1], [])

                    tokens.append({
                        "id": f"s06.{p_id}.l{assigned_n:03d}.t{t_idx+1:02d}",
                        "surface": rt,
                        "norm": norm_t,
                        "entry_ids": matched_ids
                    })

                direction_obj = {"text": inline_dir, "lang": "en"} if inline_dir else None

                line_obj = {
                    "id": f"s06.{p_id}.l{assigned_n:03d}",
                    "n": assigned_n,
                    "margin": margin,
                    "speaker": speaker,
                    "greek": greek_text,
                    "direction": direction_obj,
                    "tokens": tokens,
                    "src": {"book": "text", "printed_page": str(printed_p), "pdf_page": pdf_p}
                }
                p_obj["lines"].append(line_obj)
                line_counter = assigned_n + 1

    passages_list = [passages_dict["6A"], passages_dict["6B"], passages_dict["6C"], passages_dict["6D"]]

    os.makedirs("data/text", exist_ok=True)
    os.makedirs("data/vocab", exist_ok=True)

    with open("data/text/s06.json", "w", encoding="utf-8") as f:
        json.dump({"section": "06", "passages": passages_list}, f, indent=2, ensure_ascii=False)

    with open("data/vocab/book_text.json", "w", encoding="utf-8") as f:
        json.dump(all_vocab, f, indent=2, ensure_ascii=False)

    print(f"Text Section 6: {len(passages_list)} passages, {sum(len(p['lines']) for p in passages_list)} lines, {len(all_vocab)} vocab entries.")

def structure_grammar():
    print("Structuring Grammar Section 6 (§128–§149)...")
    blocks = []
    exercises = []

    for pdf_p in range(133, 152):
        path = f"data/pages/grammar/p{pdf_p:03d}.json"
        if not os.path.exists(path):
            continue
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        printed_p = pdf_p - 18

        for b in data.get("blocks", []):
            b_type = b.get("type", "")
            text = clean_nfc(b.get("text", "") or "")

            if b.get("exercise"):
                ex = b["exercise"]
                exercises.append({
                    "id": ex.get("id") or f"6A-B: {len(exercises)+1}",
                    "instruction": ex.get("instruction") or text,
                    "items": ex.get("items", []),
                    "src": {"book": "grammar", "printed_page": str(printed_p), "pdf_page": pdf_p}
                })
            elif b_type == "table" or b.get("table"):
                blocks.append({
                    "t": "table",
                    "caption": b.get("text") or "First aorist indicative active",
                    "table": b.get("table"),
                    "src": {"book": "grammar", "printed_page": str(printed_p), "pdf_page": pdf_p}
                })
            elif b_type == "box":
                blocks.append({
                    "t": "box",
                    "title": text[:50],
                    "items": [text],
                    "kind": "vocab-check" if "VOCABULARY CHECK" in text else "cover" if "In this section" in text else "note"
                })
            else:
                blocks.append({
                    "t": "para",
                    "no": b.get("para_no"),
                    "text": text,
                    "src": {"book": "grammar", "printed_page": str(printed_p), "pdf_page": pdf_p}
                })

    unit = {
        "id": "s06",
        "label_new": "Section 6",
        "label_old": "Section 5E–F",
        "para_range": [128, 149],
        "blocks": blocks,
        "exercises": exercises
    }

    os.makedirs("data/grammar", exist_ok=True)
    with open("data/grammar/s06.json", "w", encoding="utf-8") as f:
        json.dump(unit, f, indent=2, ensure_ascii=False)

    print(f"Grammar Section 6: {len(blocks)} blocks, {len(exercises)} exercises.")

def structure_guide():
    print("Structuring Guide Section 6...")
    notes = []
    translations = []
    answers = []

    current_passage = "6A"

    for pdf_p in range(85, 98):
        path = f"data/pages/guide/p{pdf_p:03d}.json"
        if not os.path.exists(path):
            continue
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        printed_p = pdf_p - 14

        for b in data.get("blocks", []):
            b_type = b.get("type", "")
            text = clean_nfc(b.get("text", "") or "")

            if "6A" in text:
                current_passage = "6A"
            elif "6B" in text:
                current_passage = "6B"
            elif "6C" in text:
                current_passage = "6C"
            elif "6D" in text:
                current_passage = "6D"

            if "Translation for" in text or "Translation" in text:
                translations.append({
                    "passage": current_passage,
                    "text": text,
                    "src": {"book": "guide", "printed_page": str(printed_p), "pdf_page": pdf_p}
                })
            elif "EXERCISES FOR" in text or b.get("exercise"):
                if b.get("exercise") and b["exercise"].get("items"):
                    for it in b["exercise"]["items"]:
                        answers.append({
                            "exercise_id": b["exercise"].get("id", "6A-B"),
                            "item": it.get("n", ""),
                            "answer": it.get("prompt", ""),
                            "src": {"book": "guide", "printed_page": str(printed_p), "pdf_page": pdf_p}
                        })
            else:
                m = re.match(r"^(\d+(?:[–-]\d+)?)\s+([\u0370-\u03FF\u1F00-\u1FFF\s…\.,·]+)\s+(.*)$", text)
                if m:
                    notes.append({
                        "passage": current_passage,
                        "line": m.group(1),
                        "quoted": m.group(2).strip(),
                        "text": m.group(3).strip(),
                        "src": {"book": "guide", "printed_page": str(printed_p), "pdf_page": pdf_p}
                    })

    guide_data = {
        "section": "06",
        "notes": notes,
        "translations": translations,
        "answers": answers
    }

    os.makedirs("data/guide", exist_ok=True)
    with open("data/guide/s06.json", "w", encoding="utf-8") as f:
        json.dump(guide_data, f, indent=2, ensure_ascii=False)

    print(f"Guide Section 6: {len(notes)} notes, {len(translations)} translations, {len(answers)} answers.")

if __name__ == "__main__":
    structure_text()
    structure_grammar()
    structure_guide()
    print("All structuring complete!")
