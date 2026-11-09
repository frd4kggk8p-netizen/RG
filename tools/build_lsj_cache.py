#!/usr/bin/env python3
"""
Reading Greek — LSJ Lexicon Cache Builder
Extracts complete Liddell-Scott-Jones (LSJ) entries for all vocabulary words
and reading tokens across Reading Greek sections into a compact, offline JSON database.
"""

import os
import re
import json
import unicodedata

def clean_tag(s):
    if not s:
        return ""
    return re.sub(r"<[^>]+>", "", s).strip()

def strip_accents(s):
    if not s:
        return ""
    decomposed = unicodedata.normalize("NFD", s.lower())
    stripped = "".join(c for c in decomposed if not unicodedata.combining(c))
    stripped = stripped.replace("ς", "σ").replace("’", "").replace("'", "")
    return unicodedata.normalize("NFC", stripped)

def normalize_greek(w):
    if not w:
        return ""
    w = unicodedata.normalize("NFC", w.strip(".,;·\u2019'\"()[]-–— "))
    return w

def main():
    print("=== Building LSJ Lexicon Offline Cache ===")
    
    # 1. Load LSJ sources
    dict_path = "work/lsj/dictionary.json"
    exact_path = "work/lsj/exact-match.json"
    greek_match_path = "work/lsj/greek-match.json"
    
    if not os.path.exists(dict_path):
        print(f"Error: {dict_path} not found.")
        return

    print("Loading Perseids LSJ dictionary...")
    with open(dict_path, "r", encoding="utf-8") as f:
        dictionary = json.load(f)
    print(f"Loaded {len(dictionary)} entries from LSJ.")

    exact_matches = {}
    if os.path.exists(exact_path):
        with open(exact_path, "r", encoding="utf-8") as f:
            exact_matches = json.load(f)

    greek_matches = {}
    if os.path.exists(greek_match_path):
        with open(greek_match_path, "r", encoding="utf-8") as f:
            greek_matches = json.load(f)

    # 2. Collect words from book vocabulary and lemmatized map
    vocab_file = "data/vocab/book_text.json"
    book_vocab = []
    if os.path.exists(vocab_file):
        with open(vocab_file, "r", encoding="utf-8") as f:
            book_vocab = json.load(f)

    target_words = set()
    lemma_hints = {}

    # Load lemmatized map if exists
    lem_map_file = "work/lsj/lemmatized_map.json"
    if os.path.exists(lem_map_file):
        with open(lem_map_file, "r", encoding="utf-8") as f:
            lem_map = json.load(f)
            for k, v in lem_map.items():
                lemma_hints[normalize_greek(k)] = normalize_greek(v)
                target_words.add(normalize_greek(k))
                target_words.add(normalize_greek(v))

    for v in book_vocab:
        p = normalize_greek(v.get("plain", ""))
        disp = normalize_greek(v.get("display", ""))
        lp = normalize_greek(v.get("lemma_plain", "") or "")
        ld = normalize_greek(v.get("lemma_display", "") or "")
        
        for w in [p, disp, lp, ld]:
            if w and re.search(r"[\u0370-\u03FF\u1F00-\u1FFF]", w):
                target_words.add(w)
                
        lemma = lp or ld
        if lemma and p:
            lemma_hints[p] = lemma
            lemma_hints[disp] = lemma

    # 3. Collect tokens from sections 06 to 10
    for s_num in [6, 7, 8, 9, 10]:
        s_file = f"data/text/s{s_num:02d}.json"
        if os.path.exists(s_file):
            with open(s_file, "r", encoding="utf-8") as f:
                sec_data = json.load(f)
            for p in sec_data.get("passages", []):
                for l in p.get("lines", []):
                    for t in l.get("tokens", []):
                        tok = normalize_greek(t.get("surface", ""))
                        if tok and re.search(r"[\u0370-\u03FF\u1F00-\u1FFF]", tok):
                            target_words.add(tok)

    print(f"Total unique target words to index: {len(target_words)}")

    # 4. Lookup each target word
    lsj_cache = {}
    
    # Pre-map dictionary keys by stripped accents for fast fuzzy match
    print("Indexing dictionary keys...")
    dict_key_map = {}
    for k in dictionary.keys():
        clean_k = normalize_greek(k)
        dict_key_map[clean_k] = k
        dict_key_map[clean_k.replace("-", "")] = k
        stripped_k = strip_accents(clean_k.replace("-", ""))
        if stripped_k not in dict_key_map:
            dict_key_map[stripped_k] = k

    found_count = 0
    for word in sorted(target_words):
        candidates = []
        
        # Priority 1: lemma hint
        if word in lemma_hints:
            lem = lemma_hints[word]
            candidates.append(lem)
            candidates.append(lem.replace("-", ""))
        
        # Priority 2: exact word
        candidates.append(word)
        candidates.append(word.replace("-", ""))
        
        # Priority 3: exact_matches lookup
        if word in exact_matches:
            candidates.extend(exact_matches[word])
            
        # Priority 4: greek_matches (accent-stripped)
        stripped = strip_accents(word)
        if stripped in greek_matches:
            candidates.extend(greek_matches[stripped])

        # Priority 5: dict_key_map
        if word in dict_key_map:
            candidates.append(dict_key_map[word])
        if stripped in dict_key_map:
            candidates.append(dict_key_map[stripped])

        # Find best entry
        matched_hw = None
        entry_html = None
        for cand in candidates:
            cand_norm = normalize_greek(cand)
            if cand_norm in dictionary:
                matched_hw = cand_norm
                entry_html = dictionary[cand_norm]
                break
            elif cand_norm in dict_key_map and dict_key_map[cand_norm] in dictionary:
                actual_key = dict_key_map[cand_norm]
                matched_hw = actual_key
                entry_html = dictionary[actual_key]
                break

        if entry_html:
            found_count += 1
            plain_def = clean_tag(entry_html)
            # Create a concise summary (first 250 chars)
            short_def = plain_def[:300]
            if len(plain_def) > 300:
                short_def += "..."
                
            lsj_cache[word] = {
                "headword": matched_hw,
                "html": entry_html,
                "short_def": short_def
            }

    print(f"Successfully cached LSJ entries for {found_count} of {len(target_words)} words ({found_count/len(target_words)*100:.1f}%)")

    # 5. Save cache
    out_paths = ["data/vocab/lsj_cache.json", "site/data/lsj_cache.json"]
    for path in out_paths:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(lsj_cache, f, ensure_ascii=False, indent=2)
        print(f"Wrote {len(lsj_cache)} entries to {path} ({os.path.getsize(path)/1024:.1f} KB)")

if __name__ == "__main__":
    main()
