#!/usr/bin/env python3
"""
Comprehensive Google Search Console Audit for facil.guide
Covers: Indexing, Crawl Errors, Performance, Sitemaps, Mobile Usability, Coverage by URL pattern
"""

import json
import sys
import time
import random
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from datetime import datetime, timedelta

import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build

# ── Config ──────────────────────────────────────────────────────────
SERVICE_ACCOUNT_KEY = "/Users/k/Desktop/labs/dropthe-org-internal/sync/gsc-service-account.json"
SITE_URL = "sc-domain:facil.guide"
SITEMAP_INDEX = "https://facil.guide/sitemap-index.xml"
SCOPES = [
    "https://www.googleapis.com/auth/webmasters.readonly",
    "https://www.googleapis.com/auth/webmasters",
]

# ── Auth ────────────────────────────────────────────────────────────
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_KEY, scopes=SCOPES
)
service = build("searchconsole", "v1", credentials=credentials)


def separator(title):
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


# ── 1. Sitemaps Status ─────────────────────────────────────────────
def check_sitemaps():
    separator("SITEMAPS STATUS")
    try:
        resp = service.sitemaps().list(siteUrl=SITE_URL).execute()
        sitemaps = resp.get("sitemap", [])
        if not sitemaps:
            print("  No sitemaps submitted to GSC.")
            print("  ACTION NEEDED: Submit https://facil.guide/sitemap-index.xml")
            return
        for sm in sitemaps:
            path = sm.get("path", "?")
            status = sm.get("lastSubmitted", "never")
            warnings = sm.get("warnings", 0)
            errors = sm.get("errors", 0)
            is_pending = sm.get("isPending", False)
            contents = sm.get("contents", [])
            print(f"  Sitemap: {path}")
            print(f"    Last submitted: {status}")
            print(f"    Pending: {is_pending}")
            print(f"    Warnings: {warnings}  |  Errors: {errors}")
            for c in contents:
                ctype = c.get("type", "?")
                submitted = c.get("submitted", "?")
                indexed = c.get("indexed", "?")
                print(f"    Content type: {ctype}  |  Submitted: {submitted}  |  Indexed: {indexed}")
            print()
    except Exception as e:
        print(f"  ERROR fetching sitemaps: {e}")


# ── 2. Search Performance (28 days) ────────────────────────────────
def check_performance():
    separator("SEARCH PERFORMANCE - Last 28 Days")
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=28)).strftime("%Y-%m-%d")

    # Overall totals
    try:
        req = {
            "startDate": start_date,
            "endDate": end_date,
            "dimensions": [],
            "rowLimit": 1,
        }
        resp = service.searchanalytics().query(siteUrl=SITE_URL, body=req).execute()
        rows = resp.get("rows", [])
        if rows:
            r = rows[0]
            clicks = r.get("clicks", 0)
            impressions = r.get("impressions", 0)
            ctr = r.get("ctr", 0) * 100
            position = r.get("position", 0)
            print(f"  Total Clicks:      {clicks:,.0f}")
            print(f"  Total Impressions: {impressions:,.0f}")
            print(f"  Avg CTR:           {ctr:.2f}%")
            print(f"  Avg Position:      {position:.1f}")
        else:
            print("  No performance data available for this period.")
            print("  (Site may be too new or have no search traffic yet)")
    except Exception as e:
        print(f"  ERROR fetching overall performance: {e}")

    # Top 20 queries
    print(f"\n  --- Top 20 Queries ---")
    try:
        req = {
            "startDate": start_date,
            "endDate": end_date,
            "dimensions": ["query"],
            "rowLimit": 20,
        }
        resp = service.searchanalytics().query(siteUrl=SITE_URL, body=req).execute()
        rows = resp.get("rows", [])
        if rows:
            print(f"  {'#':<4} {'Query':<50} {'Clicks':>8} {'Impr':>8} {'CTR':>7} {'Pos':>6}")
            print(f"  {'-'*4} {'-'*50} {'-'*8} {'-'*8} {'-'*7} {'-'*6}")
            for i, r in enumerate(rows, 1):
                q = r["keys"][0][:50]
                print(f"  {i:<4} {q:<50} {r['clicks']:>8.0f} {r['impressions']:>8.0f} {r['ctr']*100:>6.2f}% {r['position']:>5.1f}")
        else:
            print("  No query data available.")
    except Exception as e:
        print(f"  ERROR fetching queries: {e}")

    # Top 20 pages
    print(f"\n  --- Top 20 Pages ---")
    try:
        req = {
            "startDate": start_date,
            "endDate": end_date,
            "dimensions": ["page"],
            "rowLimit": 20,
        }
        resp = service.searchanalytics().query(siteUrl=SITE_URL, body=req).execute()
        rows = resp.get("rows", [])
        if rows:
            print(f"  {'#':<4} {'Page':<60} {'Clicks':>8} {'Impr':>8} {'CTR':>7} {'Pos':>6}")
            print(f"  {'-'*4} {'-'*60} {'-'*8} {'-'*8} {'-'*7} {'-'*6}")
            for i, r in enumerate(rows, 1):
                page = r["keys"][0].replace("https://facil.guide", "")[:60]
                print(f"  {i:<4} {page:<60} {r['clicks']:>8.0f} {r['impressions']:>8.0f} {r['ctr']*100:>6.2f}% {r['position']:>5.1f}")
        else:
            print("  No page data available.")
    except Exception as e:
        print(f"  ERROR fetching pages: {e}")

    # Performance by country
    print(f"\n  --- Top 10 Countries ---")
    try:
        req = {
            "startDate": start_date,
            "endDate": end_date,
            "dimensions": ["country"],
            "rowLimit": 10,
        }
        resp = service.searchanalytics().query(siteUrl=SITE_URL, body=req).execute()
        rows = resp.get("rows", [])
        if rows:
            print(f"  {'#':<4} {'Country':<20} {'Clicks':>8} {'Impr':>8} {'CTR':>7} {'Pos':>6}")
            print(f"  {'-'*4} {'-'*20} {'-'*8} {'-'*8} {'-'*7} {'-'*6}")
            for i, r in enumerate(rows, 1):
                print(f"  {i:<4} {r['keys'][0]:<20} {r['clicks']:>8.0f} {r['impressions']:>8.0f} {r['ctr']*100:>6.2f}% {r['position']:>5.1f}")
        else:
            print("  No country data available.")
    except Exception as e:
        print(f"  ERROR: {e}")

    # Performance by device
    print(f"\n  --- By Device ---")
    try:
        req = {
            "startDate": start_date,
            "endDate": end_date,
            "dimensions": ["device"],
            "rowLimit": 5,
        }
        resp = service.searchanalytics().query(siteUrl=SITE_URL, body=req).execute()
        rows = resp.get("rows", [])
        if rows:
            print(f"  {'Device':<15} {'Clicks':>8} {'Impr':>8} {'CTR':>7} {'Pos':>6}")
            print(f"  {'-'*15} {'-'*8} {'-'*8} {'-'*7} {'-'*6}")
            for r in rows:
                print(f"  {r['keys'][0]:<15} {r['clicks']:>8.0f} {r['impressions']:>8.0f} {r['ctr']*100:>6.2f}% {r['position']:>5.1f}")
        else:
            print("  No device data available.")
    except Exception as e:
        print(f"  ERROR: {e}")

    # Performance by date (daily trend, last 7 days)
    print(f"\n  --- Daily Trend (Last 7 Days) ---")
    try:
        start_7 = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        req = {
            "startDate": start_7,
            "endDate": end_date,
            "dimensions": ["date"],
            "rowLimit": 10,
        }
        resp = service.searchanalytics().query(siteUrl=SITE_URL, body=req).execute()
        rows = resp.get("rows", [])
        if rows:
            print(f"  {'Date':<12} {'Clicks':>8} {'Impr':>8} {'CTR':>7} {'Pos':>6}")
            print(f"  {'-'*12} {'-'*8} {'-'*8} {'-'*7} {'-'*6}")
            for r in rows:
                print(f"  {r['keys'][0]:<12} {r['clicks']:>8.0f} {r['impressions']:>8.0f} {r['ctr']*100:>6.2f}% {r['position']:>5.1f}")
        else:
            print("  No daily data available.")
    except Exception as e:
        print(f"  ERROR: {e}")


# ── 3. URL Inspection (Indexing Status) ─────────────────────────────
def fetch_sitemap_urls():
    """Fetch all URLs from the sitemap."""
    urls = []
    resp = requests.get(SITEMAP_INDEX)
    root = ET.fromstring(resp.content)
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    sitemap_locs = [loc.text for loc in root.findall(".//s:loc", ns)]

    for sm_url in sitemap_locs:
        resp2 = requests.get(sm_url)
        root2 = ET.fromstring(resp2.content)
        for loc in root2.findall(".//s:url/s:loc", ns):
            urls.append(loc.text)
    return urls


def classify_url(url):
    """Classify a URL into a pattern category."""
    path = url.replace("https://facil.guide", "")
    parts = path.strip("/").split("/")

    if path == "/" or path == "":
        return "homepage"

    lang = parts[0] if parts[0] in ["en", "fr", "es", "pt", "it"] else None

    if lang and len(parts) == 1:
        return f"/{lang}/ (lang home)"

    if lang and len(parts) >= 2:
        section = parts[1]
        if section == "guide":
            return f"/{lang}/guide/"
        elif section == "compare":
            return f"/{lang}/compare/"
        elif section == "review":
            return f"/{lang}/review/"
        else:
            return f"/{lang}/{section}/ (category)"

    return "other"


def check_indexing():
    separator("URL INSPECTION - Indexing Status")

    all_urls = fetch_sitemap_urls()
    print(f"  Total URLs in sitemap: {len(all_urls)}")

    # Strategic sampling: get URLs from each pattern type
    by_pattern = defaultdict(list)
    for u in all_urls:
        by_pattern[classify_url(u)].append(u)

    print(f"\n  URL patterns found:")
    for pattern, urls in sorted(by_pattern.items()):
        print(f"    {pattern}: {len(urls)} URLs")

    # Sample 50 URLs strategically
    sample_urls = []

    # Always include homepage and language homes
    for u in all_urls:
        path = u.replace("https://facil.guide", "")
        if path == "/" or (path.strip("/") in ["en", "fr", "es", "pt", "it"]):
            sample_urls.append(u)

    # Sample from each guide language
    for lang in ["en", "fr", "es", "pt", "it"]:
        guide_urls = [u for u in all_urls if f"/{lang}/guide/" in u]
        if guide_urls:
            sample_urls.extend(random.sample(guide_urls, min(6, len(guide_urls))))

    # Sample compare pages
    compare_urls = [u for u in all_urls if "/compare/" in u]
    if compare_urls:
        sample_urls.extend(random.sample(compare_urls, min(3, len(compare_urls))))

    # Sample review pages
    review_urls = [u for u in all_urls if "/review/" in u]
    if review_urls:
        sample_urls.extend(random.sample(review_urls, min(3, len(review_urls))))

    # Sample category pages
    category_urls = [u for u in all_urls if "/guide/" not in u and "/compare/" not in u and "/review/" not in u and u.count("/") >= 4]
    if category_urls:
        sample_urls.extend(random.sample(category_urls, min(5, len(category_urls))))

    # Deduplicate
    sample_urls = list(dict.fromkeys(sample_urls))

    print(f"\n  Inspecting {len(sample_urls)} URLs...")
    print(f"  (Rate-limited: ~1 req/sec to avoid quota issues)\n")

    results = {
        "PASS": [],
        "NEUTRAL": [],
        "FAIL": [],
        "ERROR": [],
    }
    coverage_states = Counter()
    indexing_states = Counter()
    crawl_states = Counter()
    robots_states = Counter()

    for i, url in enumerate(sample_urls):
        try:
            req_body = {
                "inspectionUrl": url,
                "siteUrl": SITE_URL,
            }
            resp = service.urlInspection().index().inspect(body=req_body).execute()
            result = resp.get("inspectionResult", {})
            index_status = result.get("indexStatusResult", {})

            verdict = index_status.get("verdict", "UNKNOWN")
            coverage = index_status.get("coverageState", "UNKNOWN")
            indexing_state = index_status.get("indexingState", "UNKNOWN")
            crawl_time = index_status.get("lastCrawlTime", "never")
            page_fetch = index_status.get("pageFetchState", "UNKNOWN")
            robots_txt = index_status.get("robotsTxtState", "UNKNOWN")
            referring_urls = index_status.get("referringUrls", [])
            sitemap_refs = index_status.get("sitemap", [])

            # Mobile usability from inspection
            mobile = result.get("mobileUsabilityResult", {})
            mobile_verdict = mobile.get("verdict", "N/A")
            mobile_issues = mobile.get("issues", [])

            # Rich results
            rich = result.get("richResultsResult", {})
            rich_verdict = rich.get("verdict", "N/A")

            results[verdict if verdict in results else "ERROR"].append({
                "url": url,
                "coverage": coverage,
                "indexing_state": indexing_state,
                "crawl_time": crawl_time,
                "page_fetch": page_fetch,
                "robots_txt": robots_txt,
                "mobile_verdict": mobile_verdict,
                "mobile_issues": mobile_issues,
                "rich_verdict": rich_verdict,
                "referring_urls": referring_urls,
                "sitemaps": sitemap_refs,
            })

            coverage_states[coverage] += 1
            indexing_states[indexing_state] += 1
            crawl_states[page_fetch] += 1
            robots_states[robots_txt] += 1

            short_url = url.replace("https://facil.guide", "")
            status_icon = "OK" if verdict == "PASS" else ("--" if verdict == "NEUTRAL" else "XX")
            print(f"  [{status_icon}] {i+1:>3}/{len(sample_urls)} {short_url:<55} {verdict:<8} {coverage}")

            # Rate limiting - GSC URL Inspection has a quota of ~600/day, ~2/sec
            time.sleep(1.2)

        except Exception as e:
            error_msg = str(e)
            short_url = url.replace("https://facil.guide", "")
            print(f"  [ER] {i+1:>3}/{len(sample_urls)} {short_url:<55} ERROR: {error_msg[:60]}")
            results["ERROR"].append({"url": url, "error": error_msg})
            # If quota error, slow down
            if "429" in error_msg or "quota" in error_msg.lower():
                print("  >>> Quota limit hit, waiting 10s...")
                time.sleep(10)
            else:
                time.sleep(1.2)

    # Summary
    print(f"\n  --- Indexing Verdict Summary ---")
    for verdict in ["PASS", "NEUTRAL", "FAIL", "ERROR"]:
        count = len(results[verdict])
        pct = (count / len(sample_urls) * 100) if sample_urls else 0
        print(f"    {verdict}: {count} ({pct:.1f}%)")

    print(f"\n  --- Coverage State Breakdown ---")
    for state, count in coverage_states.most_common():
        print(f"    {state}: {count}")

    print(f"\n  --- Indexing State ---")
    for state, count in indexing_states.most_common():
        print(f"    {state}: {count}")

    print(f"\n  --- Page Fetch State ---")
    for state, count in crawl_states.most_common():
        print(f"    {state}: {count}")

    print(f"\n  --- Robots.txt State ---")
    for state, count in robots_states.most_common():
        print(f"    {state}: {count}")

    # Group non-indexed URLs by pattern
    print(f"\n  --- Non-Indexed URLs by Pattern ---")
    non_indexed_patterns = Counter()
    non_indexed_urls = []
    for verdict in ["NEUTRAL", "FAIL"]:
        for r in results[verdict]:
            pattern = classify_url(r["url"])
            non_indexed_patterns[pattern] += 1
            non_indexed_urls.append((r["url"], r.get("coverage", "?"), verdict))

    if non_indexed_patterns:
        for pattern, count in non_indexed_patterns.most_common():
            print(f"    {pattern}: {count}")
    else:
        print("    All sampled URLs are indexed!")

    # List specific non-indexed URLs
    if non_indexed_urls:
        print(f"\n  --- Non-Indexed URL Details ---")
        for url, coverage, verdict in non_indexed_urls:
            short = url.replace("https://facil.guide", "")
            print(f"    [{verdict}] {short:<55} {coverage}")

    # Mobile usability from inspection results
    print(f"\n  --- Mobile Usability (from URL Inspection) ---")
    mobile_verdicts = Counter()
    all_mobile_issues = []
    for verdict_key in results:
        for r in results[verdict_key]:
            if isinstance(r, dict) and "mobile_verdict" in r:
                mobile_verdicts[r["mobile_verdict"]] += 1
                if r.get("mobile_issues"):
                    for issue in r["mobile_issues"]:
                        all_mobile_issues.append((r["url"], issue))

    for mv, count in mobile_verdicts.most_common():
        print(f"    {mv}: {count}")

    if all_mobile_issues:
        print(f"\n    Mobile issues found:")
        for url, issue in all_mobile_issues:
            short = url.replace("https://facil.guide", "")
            issue_type = issue.get("severity", "?")
            issue_msg = issue.get("message", str(issue))
            print(f"      {short}: [{issue_type}] {issue_msg}")
    else:
        print("    No mobile usability issues detected in sampled URLs.")

    # Coverage by URL pattern (indexed vs not)
    print(f"\n  --- Coverage by URL Pattern (sampled) ---")
    pattern_results = defaultdict(lambda: {"indexed": 0, "not_indexed": 0, "error": 0})
    for verdict_key in results:
        for r in results[verdict_key]:
            if isinstance(r, dict) and "url" in r:
                pattern = classify_url(r["url"])
                if verdict_key == "PASS":
                    pattern_results[pattern]["indexed"] += 1
                elif verdict_key in ["NEUTRAL", "FAIL"]:
                    pattern_results[pattern]["not_indexed"] += 1
                else:
                    pattern_results[pattern]["error"] += 1

    print(f"  {'Pattern':<35} {'Indexed':>8} {'Not Idx':>8} {'Error':>8} {'Rate':>8}")
    print(f"  {'-'*35} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")
    for pattern in sorted(pattern_results.keys()):
        d = pattern_results[pattern]
        total = d["indexed"] + d["not_indexed"]
        rate = (d["indexed"] / total * 100) if total > 0 else 0
        print(f"  {pattern:<35} {d['indexed']:>8} {d['not_indexed']:>8} {d['error']:>8} {rate:>7.1f}%")

    return results


# ── 4. Crawl Errors via Performance Data ────────────────────────────
def check_crawl_errors():
    separator("CRAWL ERROR DETECTION")
    print("  (GSC API doesn't expose crawl errors directly since 2022.)")
    print("  Checking for error signals via URL Inspection results above.")
    print("  Also checking for pages with 0 impressions that might have issues...\n")

    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=28)).strftime("%Y-%m-%d")

    # Check all pages with any impressions to find potential error patterns
    try:
        req = {
            "startDate": start_date,
            "endDate": end_date,
            "dimensions": ["page"],
            "rowLimit": 500,
        }
        resp = service.searchanalytics().query(siteUrl=SITE_URL, body=req).execute()
        rows = resp.get("rows", [])

        if rows:
            print(f"  Pages appearing in search results: {len(rows)}")

            # Check for non-sitemap URLs appearing (could indicate redirects/errors)
            sitemap_urls = set(fetch_sitemap_urls())
            non_sitemap = []
            for r in rows:
                page = r["keys"][0]
                if page not in sitemap_urls and page.rstrip("/") + "/" not in sitemap_urls:
                    non_sitemap.append((page, r["clicks"], r["impressions"]))

            if non_sitemap:
                print(f"\n  Pages in search but NOT in sitemap ({len(non_sitemap)}):")
                for page, clicks, impr in non_sitemap[:20]:
                    short = page.replace("https://facil.guide", "")
                    print(f"    {short:<55} clicks={clicks:.0f}  impr={impr:.0f}")
            else:
                print("  All pages appearing in search are in the sitemap. Good.")

            # Check for pages with high impressions but 0 clicks (potential soft 404s)
            zero_click_high_impr = [(r["keys"][0], r["impressions"], r["position"])
                                    for r in rows
                                    if r["clicks"] == 0 and r["impressions"] > 50]
            if zero_click_high_impr:
                print(f"\n  Pages with 0 clicks but high impressions (potential issues):")
                for page, impr, pos in sorted(zero_click_high_impr, key=lambda x: -x[1])[:10]:
                    short = page.replace("https://facil.guide", "")
                    print(f"    {short:<55} impr={impr:.0f}  pos={pos:.1f}")
        else:
            print("  No pages found in search results for this period.")
    except Exception as e:
        print(f"  ERROR: {e}")


# ── 5. Coverage Summary Estimation ──────────────────────────────────
def estimate_coverage():
    separator("COVERAGE ESTIMATION - Indexed Pages vs Sitemap")

    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")  # 90 days for wider coverage

    all_urls = fetch_sitemap_urls()
    print(f"  Sitemap URLs: {len(all_urls)}")

    # Get all pages that have appeared in search (wider window)
    try:
        req = {
            "startDate": start_date,
            "endDate": end_date,
            "dimensions": ["page"],
            "rowLimit": 5000,
        }
        resp = service.searchanalytics().query(siteUrl=SITE_URL, body=req).execute()
        rows = resp.get("rows", [])

        search_pages = set()
        for r in rows:
            search_pages.add(r["keys"][0])
            # Also add with/without trailing slash variant
            page = r["keys"][0]
            if page.endswith("/"):
                search_pages.add(page.rstrip("/"))
            else:
                search_pages.add(page + "/")

        print(f"  Pages appearing in search (90 days): {len(rows)}")

        # Match sitemap URLs against search pages
        matched = 0
        unmatched_by_pattern = defaultdict(list)
        for url in all_urls:
            if url in search_pages or url.rstrip("/") in search_pages:
                matched += 1
            else:
                pattern = classify_url(url)
                unmatched_by_pattern[pattern].append(url)

        pct = (matched / len(all_urls) * 100) if all_urls else 0
        print(f"\n  Sitemap URLs seen in search: {matched}/{len(all_urls)} ({pct:.1f}%)")
        print(f"  Sitemap URLs NOT seen in search: {len(all_urls) - matched}")

        print(f"\n  --- Not-seen URLs by Pattern ---")
        for pattern, urls in sorted(unmatched_by_pattern.items(), key=lambda x: -len(x[1])):
            print(f"    {pattern}: {len(urls)} URLs not seen in search")

        # Performance by language
        print(f"\n  --- Performance by Language (90 days) ---")
        lang_stats = defaultdict(lambda: {"clicks": 0, "impressions": 0, "pages": 0})
        for r in rows:
            page = r["keys"][0].replace("https://facil.guide", "")
            parts = page.strip("/").split("/")
            lang = parts[0] if parts and parts[0] in ["en", "fr", "es", "pt", "it"] else "root"
            lang_stats[lang]["clicks"] += r["clicks"]
            lang_stats[lang]["impressions"] += r["impressions"]
            lang_stats[lang]["pages"] += 1

        print(f"  {'Lang':<8} {'Pages':>8} {'Clicks':>10} {'Impressions':>12}")
        print(f"  {'-'*8} {'-'*8} {'-'*10} {'-'*12}")
        for lang in sorted(lang_stats.keys()):
            s = lang_stats[lang]
            print(f"  {lang:<8} {s['pages']:>8} {s['clicks']:>10,.0f} {s['impressions']:>12,.0f}")

    except Exception as e:
        print(f"  ERROR: {e}")


# ── 6. Performance by URL Type ──────────────────────────────────────
def performance_by_type():
    separator("PERFORMANCE BY URL TYPE")

    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=28)).strftime("%Y-%m-%d")

    try:
        req = {
            "startDate": start_date,
            "endDate": end_date,
            "dimensions": ["page"],
            "rowLimit": 5000,
        }
        resp = service.searchanalytics().query(siteUrl=SITE_URL, body=req).execute()
        rows = resp.get("rows", [])

        type_stats = defaultdict(lambda: {"clicks": 0, "impressions": 0, "pages": 0, "position_sum": 0})

        for r in rows:
            pattern = classify_url(r["keys"][0])
            type_stats[pattern]["clicks"] += r["clicks"]
            type_stats[pattern]["impressions"] += r["impressions"]
            type_stats[pattern]["pages"] += 1
            type_stats[pattern]["position_sum"] += r["position"]

        if type_stats:
            print(f"  {'Type':<35} {'Pages':>6} {'Clicks':>8} {'Impr':>10} {'Avg Pos':>8}")
            print(f"  {'-'*35} {'-'*6} {'-'*8} {'-'*10} {'-'*8}")
            for pattern in sorted(type_stats.keys(), key=lambda x: -type_stats[x]["impressions"]):
                s = type_stats[pattern]
                avg_pos = s["position_sum"] / s["pages"] if s["pages"] > 0 else 0
                print(f"  {pattern:<35} {s['pages']:>6} {s['clicks']:>8,.0f} {s['impressions']:>10,.0f} {avg_pos:>7.1f}")
        else:
            print("  No data available.")
    except Exception as e:
        print(f"  ERROR: {e}")


# ── Run Everything ──────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 80)
    print("  GOOGLE SEARCH CONSOLE AUDIT - facil.guide")
    print(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"  Property: {SITE_URL}")
    print("=" * 80)

    # Run in order: quick checks first, then the slow URL inspection
    check_sitemaps()
    check_performance()
    performance_by_type()
    check_crawl_errors()
    estimate_coverage()

    # URL Inspection is slow (rate limited) - run last
    indexing_results = check_indexing()

    separator("AUDIT COMPLETE")
    print("  All sections completed. Review findings above.")
    print("  Key actions should be taken for any FAIL/NEUTRAL verdicts.")
    print()
