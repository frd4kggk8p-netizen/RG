#!/usr/bin/env python3
"""
tools/transcribe_section_06.py
Batch transcribe all pages of Section 6 across Text, Grammar, and Guide.
Saves structured page JSON to data/pages/{book}/p{pdf_page:03d}.json.
"""

import json
import os
import sys
import time

sys.path.insert(0, os.path.abspath("."))
from tools.run_calibration import call_gemini

SECTION_06_PAGES = {
    "text": list(range(93, 102)),       # PDF 93–101 (printed 63–71)
    "grammar": list(range(133, 152)),   # PDF 133–151 (printed 115–133)
    "guide": list(range(85, 98))        # PDF 85–97 (printed 71–83)
}

def main():
    with open("tools/page_prompt.md", "r", encoding="utf-8") as f:
        prompt = f.read()

    total_pages = sum(len(pages) for pages in SECTION_06_PAGES.values())
    processed = 0
    cached = 0

    print(f"Targeting Section 6: {total_pages} pages total.")

    for book, pages in SECTION_06_PAGES.items():
        out_dir = f"data/pages/{book}"
        os.makedirs(out_dir, exist_ok=True)

        for p_num in pages:
            out_file = f"{out_dir}/p{p_num:03d}.json"
            if os.path.exists(out_file):
                cached += 1
                continue

            img_path = f"work/pages/{book}/p{p_num:03d}_300dpi.png"
            if not os.path.exists(img_path):
                img_path = f"work/pages/{book}/p{p_num:03d}_120dpi.png"
            if not os.path.exists(img_path):
                print(f"Error: image for {book} p.{p_num} not found!")
                continue

            t0 = time.time()
            try:
                page_data, model_used = call_gemini(img_path, prompt)
                page_data["book"] = book
                page_data["pdf_page"] = p_num

                with open(out_file, "w", encoding="utf-8") as f:
                    json.dump(page_data, f, indent=2, ensure_ascii=False)

                processed += 1
                elapsed = time.time() - t0
                print(f"[{processed + cached}/{total_pages}] Transcribed {book.upper()} p.{p_num} in {elapsed:.1f}s ({model_used}) - {len(page_data.get('blocks', []))} blocks")
                time.sleep(1) # respectful rate pacing
            except Exception as e:
                print(f"Failed to transcribe {book} p.{p_num}: {e}")

    print(f"\nSection 6 transcription complete: {processed} newly processed, {cached} cached.")

if __name__ == "__main__":
    main()
