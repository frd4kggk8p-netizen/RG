#!/usr/bin/env python3
"""
tools/lemmatize_tokens.py
Batch-lemmatizes Ancient Greek tokens from Reading Greek using Gemini 3.5 Flash-lite.
Maps inflected verb, noun, and adjective forms to standard dictionary headwords (LSJ lemmata).
Saves results into work/lsj/lemmatized_map.json.
"""

import os
import re
import json
import time
import urllib.request
import unicodedata

def get_api_key():
    key = os.environ.get("GEMINI_API_KEY")
    if not key and os.path.exists(".env"):
        for line in open(".env"):
            if line.startswith("GEMINI_API_KEY="):
                key = line.split("=", 1)[1].strip('"\n ')
                break
    if not key:
        raise ValueError("GEMINI_API_KEY is not set.")
    return key

def normalize_greek(w):
    if not w:
        return ""
    return unicodedata.normalize("NFC", w.strip(".,;·\u2019'\"()[]-–— "))

def call_gemini_lemmatize(words_batch, model="gemini-3.5-flash-lite"):
    key = get_api_key()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
    
    prompt = f"""You are an expert Classical Greek philologist.
For each of the following Ancient Greek word forms from classical texts (Attic Greek), provide the standard dictionary headword (lemma as found in Liddell-Scott-Jones LSJ, e.g. nominative singular for nouns/adjectives, first person singular present indicative active or middle/deponent for verbs).

Words to lemmatize:
{json.dumps(words_batch, ensure_ascii=False)}

Return ONLY a JSON object mapping each input word to its dictionary headword lemma.
Format:
{{
  "κεφαλὴν": "κεφαλή",
  "βασιλεῦ": "βασιλεύς",
  "ἐλάβετε": "λαμβάνω",
  "ἐβόησε": "βοάω"
}}
"""
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "response_mime_type": "application/json",
            "temperature": 0.0
        }
    }
    
    for attempt in range(5):
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(text)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait_time = 5 * (attempt + 1)
                print(f"    [Rate limit 429] Waiting {wait_time}s...")
                time.sleep(wait_time)
            elif e.code == 503:
                time.sleep(3)
            else:
                print(f"    [HTTP Error {e.code}] {e}")
                time.sleep(2)
        except Exception as e:
            print(f"    [Error] {e}")
            time.sleep(2)
    return {}

def main():
    print("=== Lemmatizing Greek Tokens for Full LSJ Coverage ===")
    
    # Existing lemmas
    map_file = "work/lsj/lemmatized_map.json"
    existing_map = {}
    if os.path.exists(map_file):
        with open(map_file, "r", encoding="utf-8") as f:
            existing_map = json.load(f)
    print(f"Existing lemmatized words in cache: {len(existing_map)}")

    # Collect target tokens
    all_tokens = set()
    for s_num in [6, 7, 8, 9, 10]:
        s_file = f"data/text/s{s_num:02d}.json"
        if os.path.exists(s_file):
            with open(s_file, "r", encoding="utf-8") as f:
                sec_data = json.load(f)
            for p in sec_data.get("passages", []):
                for l in p.get("lines", []):
                    for t in l.get("tokens", []):
                        tok = normalize_greek(t.get("surface", ""))
                        if tok and re.match(r"^[\u0370-\u03FF\u1F00-\u1FFF]+$", tok):
                            all_tokens.add(tok)

    # Filter out already lemmatized
    to_process = [w for w in sorted(all_tokens) if w not in existing_map]
    print(f"Total tokens: {len(all_tokens)}, Needs lemmatization: {len(to_process)}")

    if not to_process:
        print("All tokens already lemmatized!")
        return

    batch_size = 150
    for i in range(0, len(to_process), batch_size):
        batch = to_process[i:i+batch_size]
        print(f"Lemmatizing batch {i//batch_size + 1}/{(len(to_process)-1)//batch_size + 1} ({len(batch)} words)...")
        res = call_gemini_lemmatize(batch)
        if res:
            for k, v in res.items():
                existing_map[k] = normalize_greek(v)
            print(f"  Added {len(res)} mappings. Total now: {len(existing_map)}")
            # Save progress incrementally
            os.makedirs("work/lsj", exist_ok=True)
            with open(map_file, "w", encoding="utf-8") as f:
                json.dump(existing_map, f, ensure_ascii=False, indent=2)
        time.sleep(3)

    print(f"Finished lemmatization. Saved {len(existing_map)} total mappings to {map_file}")

if __name__ == "__main__":
    main()
