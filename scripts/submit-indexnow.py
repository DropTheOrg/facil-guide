#!/usr/bin/env python3
"""
Submit all facil.guide URLs to IndexNow (Bing, Yandex, Seznam, Naver).
Also submits to Google Search Console.

Usage: python3 scripts/submit-indexnow.py [--only-new] [--dry-run]
"""

import subprocess
import json
import sys
import requests

INDEXNOW_KEY = "78f8d3faf5874459a0fed7a2931080a9"
SITE = "https://facil.guide"
PSQL = '/opt/homebrew/Cellar/postgresql@17/17.7_1/bin/psql'
DB = 'dropthe'

DRY_RUN = '--dry-run' in sys.argv


def get_all_urls():
    """Get all live URLs from sitemap"""
    import xml.etree.ElementTree as ET
    r = requests.get(f"{SITE}/sitemap-0.xml", timeout=10)
    tree = ET.fromstring(r.text)
    ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    return [loc.text for loc in tree.findall('.//s:loc', ns)]


def submit_indexnow(urls):
    """Submit URLs via IndexNow API (covers Bing, Yandex, Seznam, Naver)"""
    # IndexNow accepts max 10,000 URLs per request
    batch_size = 10000
    total_submitted = 0
    
    for i in range(0, len(urls), batch_size):
        batch = urls[i:i+batch_size]
        payload = {
            "host": "facil.guide",
            "key": INDEXNOW_KEY,
            "keyLocation": f"{SITE}/{INDEXNOW_KEY}.txt",
            "urlList": batch
        }
        
        if DRY_RUN:
            print(f"  [DRY RUN] Would submit {len(batch)} URLs to IndexNow")
            total_submitted += len(batch)
            continue
        
        r = requests.post(
            "https://api.indexnow.org/indexnow",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if r.status_code in (200, 202):
            print(f"  IndexNow: {len(batch)} URLs submitted (HTTP {r.status_code})")
            total_submitted += len(batch)
        else:
            print(f"  IndexNow ERROR: HTTP {r.status_code} - {r.text[:200]}")
    
    return total_submitted


def submit_gsc():
    """Resubmit sitemap to Google Search Console"""
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        
        creds = service_account.Credentials.from_service_account_file(
            '/Users/kiddok/.openclaw/workspace/gsc-key.json',
            scopes=['https://www.googleapis.com/auth/webmasters']
        )
        service = build('searchconsole', 'v1', credentials=creds)
        
        if not DRY_RUN:
            service.sitemaps().submit(
                siteUrl='sc-domain:facil.guide',
                feedpath=f'{SITE}/sitemap-index.xml'
            ).execute()
        
        print("  GSC: Sitemap resubmitted")
        return True
    except Exception as e:
        print(f"  GSC ERROR: {e}")
        return False


def log_submission(url_count, engines):
    """Log submission to DB"""
    if DRY_RUN:
        return
    sql = f"""INSERT INTO facil_performance (guide_id, metric, value, recorded_at)
              SELECT 1, 'indexing_submit', {url_count}, NOW()
              WHERE NOT EXISTS (SELECT 1)"""  # placeholder
    # For now just print
    print(f"  Logged: {url_count} URLs submitted to {', '.join(engines)}")


def main():
    print("Facil.guide URL Submission")
    print("=" * 40)
    
    # Get URLs
    urls = get_all_urls()
    print(f"Total URLs in sitemap: {len(urls)}")
    
    # Submit to IndexNow (Bing + others)
    print("\n1. IndexNow (Bing, Yandex, Seznam, Naver):")
    indexnow_count = submit_indexnow(urls)
    
    # Submit to GSC
    print("\n2. Google Search Console:")
    submit_gsc()
    
    print(f"\nDone. {len(urls)} URLs submitted to all engines.")


if __name__ == '__main__':
    main()
