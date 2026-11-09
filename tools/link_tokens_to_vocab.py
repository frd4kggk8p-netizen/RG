#!/usr/bin/env python3
"""
tools/link_tokens_to_vocab.py
Re-links all Greek tokens across sections 06 to 10 to their book vocabulary entry IDs
in data/vocab/book_text.json using normalized matching.
"""

import json
import unicodedata

def norm(text):
    if not text:
        return ""
    d = unicodedata.normalize("NFD", text.lower())
    s = "".join(c for c in d if not unicodedata.combining(c))
    return unicodedata.normalize("NFC", s).replace("ς", "σ").replace("’", "").replace("'", "").replace("-", "").strip(".,;·\"()[]")

def main():
    print("=== Linking Greek Tokens to Book Vocabulary IDs ===")
    with open("data/vocab/book_text.json", "r", encoding="utf-8") as f:
        vocab = json.load(f)

    vocab_map = {}
    for v in vocab:
        p_norm = norm(v.get("plain", ""))
        d_norm = norm(v.get("display", ""))
        lp_norm = norm(v.get("lemma_plain", "") or "")
        ld_norm = norm(v.get("lemma_display", "") or "")
        
        for key in [p_norm, d_norm]:
            if key:
                vocab_map.setdefault(key, []).append(v["id"])

    total_tokens = 0
    total_linked = 0

    for s_num in [6, 7, 8, 9, 10]:
        file_path = f"data/text/s{s_num:02d}.json"
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        s_tokens = 0
        s_linked = 0

        for p in data.get("passages", []):
            for l in p.get("lines", []):
                for t in l.get("tokens", []):
                    s_tokens += 1
                    t_norm = norm(t.get("surface", ""))
                    ids = vocab_map.get(t_norm, [])
                    if not ids and t_norm.endswith("ν"):
                        ids = vocab_map.get(t_norm[:-1], [])
                    
                    t["entry_ids"] = ids
                    if ids:
                        s_linked += 1

        total_tokens += s_tokens
        total_linked += s_linked

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"Section {s_num:02d}: Linked {s_linked} of {s_tokens} tokens ({s_linked/s_tokens*100:.1f}%)")

    print(f"Successfully linked {total_linked} of {total_tokens} tokens across all sections.")

if __name__ == "__main__":
    main()
