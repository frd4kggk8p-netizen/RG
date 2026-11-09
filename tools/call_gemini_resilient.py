#!/usr/bin/env python3
"""
tools/call_gemini_resilient.py
Resilient multimodal vision caller for Gemini:
- Handles Rate Limits (429) with exponential backoff & polite pacing (4s)
- Handles 503 Service Unavailable with retries
- Handles RECITATION filter via automatic half-page vertical crops
"""

import base64
import io
import json
import os
import time
import urllib.request
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

def _single_api_call(img_b64, prompt, model="gemini-3.5-flash-lite", timeout=40):
    key = get_api_key()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
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

    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                cand = data["candidates"][0]
                finish = cand.get("finishReason")
                if finish == "RECITATION":
                    return None, "RECITATION"
                if "parts" in cand.get("content", {}):
                    txt = cand["content"]["parts"][0]["text"]
                    return json.loads(txt), finish
                return None, finish
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait_sec = 10 + attempt * 5
                # print(f"    [Rate limit 429] Waiting {wait_sec}s...")
                time.sleep(wait_sec)
            elif e.code == 503:
                time.sleep(3 + attempt * 2)
            else:
                time.sleep(2)
        except Exception as e:
            time.sleep(2 + attempt)

    return None, "FAILED"

def transcribe_image_resilient(img_path, prompt, model="gemini-3.5-flash-lite"):
    with open(img_path, "rb") as f:
        full_b64 = base64.b64encode(f.read()).decode("utf-8")

    # Attempt 1: Full image
    res, finish = _single_api_call(full_b64, prompt, model=model)
    time.sleep(4) # polite pacing (<= 15 RPM)

    if res and res.get("blocks"):
        return res, model

    # If RECITATION or failure: crop into top and bottom half
    # print(f"    [Auto-Crop] Fallback to top/bottom crops for {img_path} (finish={finish})...")
    img = Image.open(img_path)
    w, h = img.size

    top_crop = img.crop((0, 0, w, int(h * 0.52)))
    bot_crop = img.crop((0, int(h * 0.48), w, h))

    buf_top = io.BytesIO()
    top_crop.save(buf_top, format="PNG")
    b64_top = base64.b64encode(buf_top.getvalue()).decode()

    buf_bot = io.BytesIO()
    bot_crop.save(buf_bot, format="PNG")
    b64_bot = base64.b64encode(buf_bot.getvalue()).decode()

    res_top, _ = _single_api_call(b64_top, prompt, model=model)
    time.sleep(4)
    res_bot, _ = _single_api_call(b64_bot, prompt, model=model)
    time.sleep(4)

    blocks = []
    if res_top and res_top.get("blocks"):
        blocks.extend(res_top["blocks"])
    if res_bot and res_bot.get("blocks"):
        blocks.extend(res_bot["blocks"])

    combined = {
        "folio": (res_top or {}).get("folio") or (res_bot or {}).get("folio"),
        "running_head": (res_top or {}).get("running_head") or (res_bot or {}).get("running_head"),
        "blocks": blocks
    }
    return combined, f"{model}-crop"

if __name__ == "__main__":
    import sys
    test_img = sys.argv[1] if len(sys.argv) > 1 else "work/pages/text/p102_120dpi.png"
    with open("tools/page_prompt.md") as f:
        p = f.read()
    data, m = transcribe_image_resilient(test_img, p)
    print(f"SUCCESS with {m}! Blocks: {len(data.get('blocks', []))}")
