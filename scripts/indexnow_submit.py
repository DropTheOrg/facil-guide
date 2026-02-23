#!/usr/bin/env python3
"""
IndexNow URL Submission for facil.guide.

Submits URLs to Bing, Yandex, DuckDuckGo, and other IndexNow-compatible engines.
No authentication needed -- just the key file.

Usage:
  python3 indexnow_submit.py                  # Submit all URLs from sitemap
  python3 indexnow_submit.py --new-only       # Submit only new URLs
  python3 indexnow_submit.py --url URL        # Submit single URL
  python3 indexnow_submit.py --dry-run        # Preview

Quota: 10,000 URLs/day.
"""

import json
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
DIST_DIR = PROJECT_DIR / "dist"
STATE_FILE = SCRIPT_DIR / "indexnow_submitted.json"
SITE_URL = "https://facil.guide"
KEY = "3162d1f6d1a6462d9784f04c9fcc2aa6"

DRY_RUN = "--dry-run" in sys.argv
NEW_ONLY = "--new-only" in sys.argv
SINGLE_URL = None
for i, arg in enumerate(sys.argv):
    if arg == "--url" and i + 1 < len(sys.argv):
        SINGLE_URL = sys.argv[i + 1]


def get_urls_from_sitemap():
    sitemap_path = DIST_DIR / "sitemap-0.xml"
    if not sitemap_path.exists():
        print(f"ERROR: {sitemap_path} not found. Run 'npm run build' first.")
        sys.exit(1)
    tree = ET.parse(sitemap_path)
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    return [loc.text for loc in tree.getroot().findall(".//s:loc", ns)]


def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"submitted": []}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def submit_urls(urls):
    """Submit batch of URLs to IndexNow API."""
    payload = json.dumps({
        "host": "facil.guide",
        "key": KEY,
        "keyLocation": f"{SITE_URL}/{KEY}.txt",
        "urlList": urls,
    }).encode()

    req = urllib.request.Request(
        "https://api.indexnow.org/indexnow",
        data=payload,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as resp:
            print(f"IndexNow response: {resp.status}")
            return resp.status in (200, 202)
    except urllib.error.HTTPError as e:
        print(f"IndexNow error: {e.code} {e.read().decode()}")
        return False


def main():
    if SINGLE_URL:
        urls = [SINGLE_URL]
    else:
        urls = get_urls_from_sitemap()
        if NEW_ONLY:
            state = load_state()
            urls = [u for u in urls if u not in state["submitted"]]
            if not urls:
                print("No new URLs.")
                return

    print(f"Submitting {len(urls)} URLs to IndexNow...")

    if DRY_RUN:
        for u in urls:
            print(f"  [DRY RUN] {u}")
        return

    # IndexNow accepts up to 10,000 per batch
    ok = submit_urls(urls)

    if ok:
        state = load_state()
        state["submitted"] = list(set(state["submitted"] + urls))
        save_state(state)
        print(f"Done. {len(urls)} URLs submitted.")
    else:
        print("Submission failed.")


if __name__ == "__main__":
    main()
