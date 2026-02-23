#!/usr/bin/env python3
"""
Google Indexing API URL Submission for facil.guide.

Submits new/updated URLs to Google for fast indexing.
Also pings sitemap after deploy.

Usage:
  python3 gsc_submit.py                    # Submit all pages from sitemap
  python3 gsc_submit.py --url URL          # Submit single URL
  python3 gsc_submit.py --sitemap          # Ping sitemap only
  python3 gsc_submit.py --new-only         # Submit only URLs not in last_submitted.json
  python3 gsc_submit.py --dry-run          # Preview without submitting
  python3 gsc_submit.py --status URL       # Check indexing status for URL

API quota: 200 URLs/day for Indexing API.

Prerequisites:
  1. facil.guide added to Google Search Console
  2. monkey@dropthe.iam.gserviceaccount.com added as Owner in GSC
  3. pip install google-auth google-api-python-client
"""

import json
import os
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
DIST_DIR = PROJECT_DIR / "dist"
STATE_FILE = SCRIPT_DIR / "last_submitted.json"
KEY_FILE = "/Users/kiddok/.openclaw/workspace/gsc-key.json"
SITE_URL = "https://facil.guide"
SITEMAP_URL = f"{SITE_URL}/sitemap-index.xml"
SCOPES = ["https://www.googleapis.com/auth/indexing"]

DRY_RUN = "--dry-run" in sys.argv
NEW_ONLY = "--new-only" in sys.argv
SITEMAP_ONLY = "--sitemap" in sys.argv
SINGLE_URL = None
CHECK_STATUS = False

for i, arg in enumerate(sys.argv):
    if arg == "--url" and i + 1 < len(sys.argv):
        SINGLE_URL = sys.argv[i + 1]
    if arg == "--status" and i + 1 < len(sys.argv):
        CHECK_STATUS = True
        SINGLE_URL = sys.argv[i + 1]


def get_indexing_service():
    """Build Indexing API service."""
    from google.oauth2 import service_account
    from googleapiclient.discovery import build

    credentials = service_account.Credentials.from_service_account_file(
        KEY_FILE, scopes=SCOPES
    )
    return build("indexing", "v3", credentials=credentials)


def get_urls_from_sitemap():
    """Parse sitemap and extract all URLs."""
    sitemap_path = DIST_DIR / "sitemap-0.xml"
    if not sitemap_path.exists():
        print(f"ERROR: Sitemap not found at {sitemap_path}")
        print("Run 'npm run build' first.")
        sys.exit(1)

    tree = ET.parse(sitemap_path)
    root = tree.getroot()
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = [loc.text for loc in root.findall(".//s:loc", ns)]
    return urls


def load_state():
    """Load previously submitted URLs."""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"submitted": {}, "last_run": None}


def save_state(state):
    """Save submitted URLs state."""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def submit_url(service, url, action="URL_UPDATED"):
    """Submit a single URL to Google Indexing API."""
    body = {"url": url, "type": action}
    try:
        response = service.urlNotifications().publish(body=body).execute()
        return True, response
    except Exception as e:
        return False, str(e)


def ping_sitemap():
    """Ping Google with sitemap URL."""
    ping_url = f"https://www.google.com/ping?sitemap={SITEMAP_URL}"
    try:
        req = urllib.request.Request(ping_url)
        with urllib.request.urlopen(req) as resp:
            status = resp.status
        print(f"Sitemap ping: {status} ({ping_url})")
        return status == 200
    except Exception as e:
        print(f"Sitemap ping failed: {e}")
        return False


def check_status(service, url):
    """Check indexing status for a URL."""
    try:
        response = service.urlNotifications().getMetadata(url=url).execute()
        print(f"\nStatus for {url}:")
        print(json.dumps(response, indent=2))
    except Exception as e:
        print(f"Status check failed: {e}")


def main():
    now = datetime.now(timezone.utc).isoformat()

    # Sitemap ping only
    if SITEMAP_ONLY:
        ping_sitemap()
        return

    # Build service
    service = get_indexing_service()

    # Status check
    if CHECK_STATUS and SINGLE_URL:
        check_status(service, SINGLE_URL)
        return

    # Single URL submission
    if SINGLE_URL:
        if DRY_RUN:
            print(f"[DRY RUN] Would submit: {SINGLE_URL}")
            return
        ok, resp = submit_url(service, SINGLE_URL)
        print(f"{'OK' if ok else 'FAIL'}: {SINGLE_URL}")
        if not ok:
            print(f"  Error: {resp}")
        return

    # Batch submission from sitemap
    urls = get_urls_from_sitemap()
    state = load_state()

    if NEW_ONLY:
        urls = [u for u in urls if u not in state["submitted"]]
        if not urls:
            print("No new URLs to submit.")
            return

    print(f"URLs to submit: {len(urls)}")
    if len(urls) > 200:
        print(f"WARNING: API quota is 200/day. Submitting first 200.")
        urls = urls[:200]

    submitted = 0
    failed = 0

    for url in urls:
        if DRY_RUN:
            print(f"  [DRY RUN] {url}")
            submitted += 1
            continue

        ok, resp = submit_url(service, url)
        if ok:
            state["submitted"][url] = now
            submitted += 1
            print(f"  OK: {url}")
        else:
            failed += 1
            print(f"  FAIL: {url} -- {resp}")

    state["last_run"] = now
    if not DRY_RUN:
        save_state(state)

    print(f"\nDone. Submitted: {submitted}, Failed: {failed}")

    # Ping sitemap after batch
    ping_sitemap()


if __name__ == "__main__":
    main()
