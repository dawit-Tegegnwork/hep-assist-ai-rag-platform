#!/usr/bin/env python3
"""Capture portfolio screenshots using Playwright.

Prerequisites:
  pip install playwright
  playwright install chromium

Usage:
  # Terminal 1: MEDIMIND_EMBEDDING_PROVIDER=mock PYTHONPATH=backend uvicorn main:app --app-dir backend
  # Terminal 2: cd frontend && npm run dev
  python scripts/capture_screenshots.py
"""

from __future__ import annotations

import sys
from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "docs" / "screenshots"

PAGES = [
    ("ask.png", "http://127.0.0.1:5173/ask"),
    ("answer.png", "http://127.0.0.1:5173/ask"),
    ("review.png", "http://127.0.0.1:5173/review"),
    ("evaluation.png", "http://127.0.0.1:5173/evaluation"),
    ("swagger.png", "http://127.0.0.1:8000/docs"),
    ("dashboard.png", "http://127.0.0.1:8000/dashboard"),
]


def main() -> int:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Install playwright: pip install playwright && playwright install chromium", file=sys.stderr)
        return 1

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 900})

        for filename, url in PAGES:
            print(f"Capturing {filename} from {url}")
            page.goto(url, wait_until="networkidle", timeout=60000)

            if filename == "answer.png":
                page.fill("textarea", "What hepatitis B screening tests are approved?")
                page.click('button[type="submit"]')
                page.wait_for_timeout(2500)
                page.screenshot(path=str(OUTPUT_DIR / filename), full_page=True)
                continue

            page.screenshot(path=str(OUTPUT_DIR / filename), full_page=True)

        browser.close()

    print(f"Screenshots saved to {OUTPUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
