#!/usr/bin/env python3
"""
tools/build_manifest.py
Build data/manifest.json containing the page map, offsets, scope flags,
and text layer classification across Text, Grammar, and Guide.
"""

import fitz
import json
import os
import re

BOOKS = {
    "text": {
        "file": "source/RG_Text_2014.pdf",
        "offset": 30,
        "slice1_pdf_range": (93, 101),       # Section 6: printed 63–71
        "project_pdf_range": (93, 296),     # Sections 6–20: printed 63–266
        "phase5_pdf_range": (297, 320)      # Vocabularies / proper names
    },
    "grammar": {
        "file": "source/RG_grammar.pdf",
        "offset": 18,
        "slice1_pdf_range": (133, 151),     # Section 6 (§128–§149): printed 115–133
        "project_pdf_range": (133, 386),    # Sections 6–20 (§128–§339): printed 115–368
        "phase5_pdf_range": (387, 561)      # Reference Grammar (§340+) & Vocabs
    },
    "guide": {
        "file": "source/RG_Guide.pdf",
        "offset": 14,
        "slice1_pdf_range": (85, 97),       # Section 6: printed 71–83
        "project_pdf_range": (85, 281),     # Sections 6–20: printed 71–267
        "phase5_pdf_range": None
    }
}

cyr_pat = re.compile(r'[\u0400-\u04FF]')
comb_pat = re.compile(r'[\u0300-\u036F]')
greek_pat = re.compile(r'[\u0370-\u03FF\u1F00-\u1FFF]')

def classify_text_layer(text):
    has_cyrillic = bool(cyr_pat.search(text))
    combining_count = len(comb_pat.findall(text))
    greek_count = len(greek_pat.findall(text))
    
    if greek_count == 0 and not has_cyrillic:
        return "no_greek"
    if has_cyrillic or combining_count > 6:
        return "corrupt"
    if greek_count >= 15:
        return "clean"
    return "mixed"

def determine_printed_page(book, pdf_page, total_pages, offset):
    expected_folio = pdf_page - offset
    if expected_folio > 0:
        return str(expected_folio)
    # Roman numerals for front matter roughly
    return f"front-{pdf_page}"

def main():
    manifest = {
        "metadata": {
            "title": "Reading Greek Digital Platform - Manifest",
            "version": "1.0.0",
            "books": {}
        },
        "pages": {}
    }

    for book_id, info in BOOKS.items():
        doc = fitz.open(info["file"])
        total = len(doc)
        manifest["metadata"]["books"][book_id] = {
            "file": info["file"],
            "total_pages": total,
            "offset": info["offset"],
            "slice1_pdf_range": info["slice1_pdf_range"],
            "project_pdf_range": info["project_pdf_range"],
            "phase5_pdf_range": info["phase5_pdf_range"]
        }

        book_pages = []
        for p in range(total):
            pdf_p = p + 1
            txt = doc[p].get_text()
            layer_status = classify_text_layer(txt)
            printed_p = determine_printed_page(book_id, pdf_p, total, info["offset"])

            in_slice1 = False
            if info["slice1_pdf_range"]:
                in_slice1 = (info["slice1_pdf_range"][0] <= pdf_p <= info["slice1_pdf_range"][1])

            in_project = False
            if info["project_pdf_range"]:
                in_project = (info["project_pdf_range"][0] <= pdf_p <= info["project_pdf_range"][1])

            in_phase5 = False
            if info["phase5_pdf_range"]:
                in_phase5 = (info["phase5_pdf_range"][0] <= pdf_p <= info["phase5_pdf_range"][1])

            entry = {
                "book": book_id,
                "pdf_page": pdf_p,
                "printed_page": printed_p,
                "text_layer_status": layer_status,
                "in_slice1": in_slice1,
                "in_project": in_project,
                "in_phase5": in_phase5,
                "verified": False,
                "raster_300_path": f"work/pages/{book_id}/p{pdf_p:03d}_300dpi.png",
                "preview_120_path": f"work/pages/{book_id}/p{pdf_p:03d}_120dpi.png"
            }
            book_pages.append(entry)
            
        manifest["pages"][book_id] = book_pages
        print(f"[{book_id.upper()}] Processed {total} pages. Slice 1: {info['slice1_pdf_range']}, Project: {info['project_pdf_range']}")

    os.makedirs("data", exist_ok=True)
    with open("data/manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print("Manifest successfully written to data/manifest.json")

if __name__ == "__main__":
    main()
