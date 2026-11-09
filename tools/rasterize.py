#!/usr/bin/env python3
"""
tools/rasterize.py
Rasterizes PDF pages to 300 DPI master PNGs and 120 DPI web previews.
Supports selective rendering (Slice 1, calibration set, custom ranges, or --all).
"""

import argparse
import fitz
import json
import os
import sys

def rasterize_page(doc, pdf_page, out_300, out_120, force=False):
    os.makedirs(os.path.dirname(out_300), exist_ok=True)
    os.makedirs(os.path.dirname(out_120), exist_ok=True)

    if not force and os.path.exists(out_300) and os.path.exists(out_120):
        return False  # Already exists

    page = doc[pdf_page - 1]
    
    # 300 DPI master
    pix_300 = page.get_pixmap(dpi=300)
    pix_300.save(out_300)
    
    # 120 DPI preview
    pix_120 = page.get_pixmap(dpi=120)
    pix_120.save(out_120)
    
    return True

def main():
    parser = argparse.ArgumentParser(description="Rasterize PDF pages to PNG at 300 & 120 DPI")
    parser.add_argument("--book", choices=["text", "grammar", "guide", "all"], default="all")
    parser.add_argument("--slice1", action="store_true", help="Rasterize all Slice 1 (Section 6) pages")
    parser.add_argument("--calibration", action="store_true", help="Rasterize calibration dataset")
    parser.add_argument("--all", action="store_true", help="Rasterize all project scope pages (6-20)")
    parser.add_argument("--pages", type=str, help="Comma-separated or range e.g. 93-101")
    parser.add_argument("--force", action="store_true", help="Overwrite existing renders")
    args = parser.parse_args()

    manifest_path = "data/manifest.json"
    if not os.path.exists(manifest_path):
        print("Error: data/manifest.json not found. Run tools/build_manifest.py first.")
        sys.exit(1)

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    books_to_process = ["text", "grammar", "guide"] if args.book == "all" else [args.book]

    total_rendered = 0
    total_skipped = 0

    for book in books_to_process:
        meta = manifest["metadata"]["books"][book]
        doc = fitz.open(meta["file"])
        page_entries = manifest["pages"][book]

        target_pdf_pages = set()

        if args.pages:
            for part in args.pages.split(","):
                if "-" in part:
                    s, e = map(int, part.split("-"))
                    target_pdf_pages.update(range(s, e + 1))
                else:
                    target_pdf_pages.add(int(part))
        elif args.slice1 or args.calibration:
            for p in page_entries:
                if args.slice1 and p["in_slice1"]:
                    target_pdf_pages.add(p["pdf_page"])
        elif args.all:
            for p in page_entries:
                if p["in_project"]:
                    target_pdf_pages.add(p["pdf_page"])
        else:
            # Default: render Slice 1
            for p in page_entries:
                if p["in_slice1"]:
                    target_pdf_pages.add(p["pdf_page"])

        print(f"[{book.upper()}] Rasterizing {len(target_pdf_pages)} pages...")
        for p_num in sorted(target_pdf_pages):
            out_300 = f"work/pages/{book}/p{p_num:03d}_300dpi.png"
            out_120 = f"work/pages/{book}/p{p_num:03d}_120dpi.png"
            rendered = rasterize_page(doc, p_num, out_300, out_120, force=args.force)
            if rendered:
                total_rendered += 1
            else:
                total_skipped += 1

    print(f"Rasterization finished: {total_rendered} newly rendered, {total_skipped} skipped.")

if __name__ == "__main__":
    main()
