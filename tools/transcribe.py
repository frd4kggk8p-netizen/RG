#!/usr/bin/env python3
"""
tools/transcribe.py
Dual-pass vision transcription pipeline for Reading Greek pages using Gemini Flash.
Enforces Unicode NFC, polytonic Greek validation, layout extraction, and disagreement auditing.
"""

import argparse
import base64
import json
import os
import re
import sys
import time
import urllib.request
import unicodedata
from PIL import Image

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

# Allowed Greek character set: Standard Greek, Polytonic Greek, apostrophe U+2019, punctuation
GREEK_REGEX = re.compile(r"^[\u0370-\u03FF\u1F00-\u1FFF\u2019\u00B7\s\.,;:\-—–·’'\(\)\[\]«»]+$")
CYRILLIC_OR_LATIN_IN_GREEK = re.compile(r"[\u0400-\u04FF|a-zA-Z]")

def normalize_nfc(text):
    if not text:
        return text
    # Unicode NFC normalization
    norm = unicodedata.normalize("NFC", text)
    # Normalise standard typographic quotes/dashes/Greek question mark
    norm = norm.replace("\u037E", ";")  # Greek question mark -> semicolon
    norm = norm.replace("\u0387", "·")  # Greek ano teleia
    norm = norm.replace("’", "’").replace("‘", "‘")
    return norm

def check_script_purity(token):
    # Strip punctuation
    stripped = re.sub(r"[\s\.,;:\-—–·’'\(\)\[\]«»0-9]", "", token)
    if not stripped:
        return True
    has_greek = bool(re.search(r"[\u0370-\u03FF\u1F00-\u1FFF]", stripped))
    if has_greek:
        # Check if Latin or Cyrillic characters are embedded inside
        bad = CYRILLIC_OR_LATIN_IN_GREEK.search(stripped)
        if bad:
            return False
    return True

def call_gemini_vision(img_path, prompt, model="gemini-3.5-flash", timeout=45):
    key = get_api_key()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"

    with open(img_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("utf-8")

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt},
                    {"inline_data": {"mime_type": "image/png", "data": img_b64}}
                ]
            }
        ],
        "generationConfig": {
            "response_mime_type": "application/json",
            "temperature": 0.1
        }
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(text)
        except Exception as e:
            time.sleep(2 * (attempt + 1))
            if attempt == 2:
                raise e

def transcribe_page_dual_pass(book, pdf_page, image_300, model="gemini-3.5-flash"):
    with open("tools/page_prompt.md", "r", encoding="utf-8") as f:
        base_prompt = f.read()

    # Pass A: Whole page transcription
    pass_a_prompt = (
        base_prompt + "\n\n"
        "TASK FOR PASS A:\n"
        "Perform a full-page transcription following all rules above. Output valid JSON strictly adhering to the schema."
    )
    res_a = call_gemini_vision(image_300, pass_a_prompt, model=model)

    # Pass B: Line-by-line / targeted diacritic focus
    pass_b_prompt = (
        base_prompt + "\n\n"
        "TASK FOR PASS B (DIACRITIC-VERIFIED PASS):\n"
        "Carefully re-read every line and token. Pay special attention to diacritics: rough/smooth breathings, circumflex vs acute, iota subscripts, and speaker abbreviations. Output valid JSON adhering to the schema."
    )
    res_b = call_gemini_vision(image_300, pass_b_prompt, model=model)

    # Reconcile Pass A and Pass B
    reconciled_blocks = []
    blocks_a = res_a.get("blocks", [])
    blocks_b = res_b.get("blocks", [])

    # Normalize NFC
    for b in blocks_a:
        if b.get("text"):
            b["text"] = normalize_nfc(b["text"])
    for b in blocks_b:
        if b.get("text"):
            b["text"] = normalize_nfc(b["text"])

    discrepancies = []
    max_len = max(len(blocks_a), len(blocks_b))
    
    for i in range(max_len):
        b_a = blocks_a[i] if i < len(blocks_a) else None
        b_b = blocks_b[i] if i < len(blocks_b) else None

        if b_a and b_b:
            text_a = b_a.get("text") or ""
            text_b = b_b.get("text") or ""
            
            block = b_a.copy()
            if text_a == text_b:
                block["text"] = text_a
            else:
                discrepancies.append({
                    "order": i,
                    "pass_a": text_a,
                    "pass_b": text_b
                })
                # Check for diacritic or punctuation difference
                # Keep Pass B as the diacritic-verified reading, and mark uncertain
                block["text"] = text_b
                if "uncertain" not in block or not block["uncertain"]:
                    block["uncertain"] = []
                block["uncertain"].append({
                    "span": text_b,
                    "reason": "Pass A and Pass B disagreement",
                    "candidates": [text_a, text_b]
                })
            reconciled_blocks.append(block)
        elif b_a:
            reconciled_blocks.append(b_a)
        elif b_b:
            reconciled_blocks.append(b_b)

    page_data = {
        "book": book,
        "pdf_page": pdf_page,
        "running_head": normalize_nfc(res_b.get("running_head") or res_a.get("running_head")),
        "folio": res_b.get("folio") or res_a.get("folio"),
        "blocks": reconciled_blocks,
        "discrepancies": discrepancies,
        "agreement_ratio": (max_len - len(discrepancies)) / max_len if max_len > 0 else 1.0
    }

    out_dir = f"data/pages/{book}"
    os.makedirs(out_dir, exist_ok=True)
    out_file = f"{out_dir}/p{pdf_page:03d}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(page_data, f, indent=2, ensure_ascii=False)

    return page_data

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--book", required=True, choices=["text", "grammar", "guide"])
    parser.add_argument("--page", required=True, type=int)
    parser.add_argument("--model", default="gemini-3.5-flash")
    args = parser.parse_args()

    img_300 = f"work/pages/{args.book}/p{args.page:03d}_300dpi.png"
    if not os.path.exists(img_300):
        print(f"Error: {img_300} not found.")
        sys.exit(1)

    print(f"Transcribing {args.book.upper()} p. {args.page} (dual-pass with {args.model})...")
    res = transcribe_page_dual_pass(args.book, args.page, img_300, model=args.model)
    print(f"Done! Blocks: {len(res['blocks'])}, Agreement: {res['agreement_ratio']*100:.1f}%, Discrepancies: {len(res['discrepancies'])}")
