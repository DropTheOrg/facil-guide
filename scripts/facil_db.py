#!/usr/bin/env python3
"""
facil_db.py -- Single entry point for all Facil.guide database operations.
Every guide creation, update, deploy, or query flows through here.

Usage:
    python3 facil_db.py sync              # Sync all files to DB (backfill/refresh)
    python3 facil_db.py gaps              # Show translation gaps
    python3 facil_db.py stats             # Full stats dashboard
    python3 facil_db.py register <slug> <lang> <file>  # Register a new guide
    python3 facil_db.py deployed <slug> <lang>         # Mark as deployed
    python3 facil_db.py suggest <n>       # Generate n topic suggestions
    python3 facil_db.py next <n>          # Show next n guides to write (by priority)
    python3 facil_db.py stale             # Show stale guides needing refresh
    python3 facil_db.py journey <name>    # Show a user journey
    python3 facil_db.py audit <slug>      # Show audit trail for a topic
    python3 facil_db.py quality           # Run quality checks on all guides
"""

import os, sys, yaml, hashlib, json, subprocess
from datetime import datetime, timezone

GUIDE_DIR = "/Users/kiddok/Desktop/labs/facil-guide/src/content/guides"
PSQL = "/opt/homebrew/Cellar/postgresql@17/17.7_1/bin/psql"
DB = "dropthe"

# ============================================================
# DB helpers
# ============================================================

def run_sql(sql, fetch=True):
    """Run SQL, return rows as list of dicts or just execute."""
    if fetch:
        p = subprocess.run(
            [PSQL, '-d', DB, '-t', '-A', '-F', '\t', '-c', sql],
            capture_output=True, text=True
        )
        if p.returncode != 0:
            print(f"SQL ERROR: {p.stderr}", file=sys.stderr)
            return []
        rows = []
        for line in p.stdout.strip().split('\n'):
            if line:
                rows.append(line.split('\t'))
        return rows
    else:
        p = subprocess.run([PSQL, '-d', DB, '-c', sql], capture_output=True, text=True)
        if p.returncode != 0:
            print(f"SQL ERROR: {p.stderr}", file=sys.stderr)
            return False
        return True

def esc(s):
    if s is None: return 'NULL'
    return "'" + str(s).replace("'", "''") + "'"

def parse_guide(path):
    """Parse a guide markdown file, return (frontmatter_dict, body_text, raw_content)."""
    content = open(path).read()
    fm, body = {}, content
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            try: fm = yaml.safe_load(parts[1]) or {}
            except: pass
            body = parts[2]
    return fm, body, content

def detect_brands(text):
    """Detect brand mentions in text."""
    brands = []
    text_lower = text.lower()
    brand_list = [
        'apple', 'google', 'whatsapp', 'samsung', 'zoom', 'microsoft',
        'facebook', 'instagram', 'youtube', 'tiktok', 'snapchat', 'telegram',
        'signal', 'spotify', 'netflix', 'amazon', 'mozilla', 'firefox',
        'chrome', 'safari', 'siri', 'alexa', 'gmail', 'outlook', 'yahoo',
        'facetime', 'bluetooth', 'android', 'iphone', 'ipad', 'mac'
    ]
    for b in brand_list:
        if b in text_lower:
            brands.append(b)
    return brands

def compute_quality(fm, body):
    """Compute quality score and individual checks."""
    checks = {}
    checks['has_bold'] = '**' in body
    checks['has_faq'] = len(fm.get('faq', [])) >= 3
    checks['has_tips'] = any(x in body for x in ['## Helpful tips', '## Tips', '## Conseils', '## Consejos', '## Dicas', '## Consigli'])
    checks['has_external_links'] = 'http' in body
    checks['min_steps'] = fm.get('steps', 0) >= 4
    checks['max_steps'] = fm.get('steps', 0) <= 8
    checks['min_words'] = len(body.split()) >= 200
    checks['has_what_you_need'] = 'what you need' in body.lower() or 'ce dont vous' in body.lower() or 'lo que necesitas' in body.lower() or 'o que precisa' in body.lower() or 'cosa ti serve' in body.lower()
    checks['has_description'] = bool(fm.get('description', ''))
    checks['no_jargon'] = not any(w in body.lower() for w in ['api', 'dns', 'ssh', 'tcp', 'ip address', 'protocol'])
    
    score = int(sum(checks.values()) / len(checks) * 100)
    return score, checks

# ============================================================
# Commands
# ============================================================

def cmd_register(slug, lang, file_path, topic_title_en=None, category=None, platform=None):
    """Register a new guide in the DB. Creates topic if needed."""
    if not os.path.exists(file_path):
        print(f"ERROR: File not found: {file_path}", file=sys.stderr)
        return False
    
    fm, body, content = parse_guide(file_path)
    chash = hashlib.md5(content.encode()).hexdigest()
    title = fm.get('title', slug)
    desc = fm.get('description', '')
    cat = category or fm.get('category', 'general')
    plat = platform or fm.get('platform', 'web')
    diff_map = {'facile': 'beginner', 'moyen': 'intermediate', 'difficile': 'advanced'}
    diff = diff_map.get(fm.get('difficulty', 'facile'), 'beginner')
    steps = fm.get('steps', 0)
    faq_count = len(fm.get('faq', []))
    wc = len(body.split())
    date = fm.get('date', datetime.now().strftime('%Y-%m-%d'))
    brands = detect_brands(title + ' ' + body)
    quality_score, quality_checks = compute_quality(fm, body)
    
    # For EN guides, the topic slug is the guide slug
    # For translations, we need the source slug from meta or mapping
    en_slug = slug if lang == 'en' else None
    if lang != 'en':
        # Try to find from existing topic
        rows = run_sql(f"SELECT slug FROM facil_topics WHERE slug = {esc(slug)}")
        if rows:
            en_slug = rows[0][0]
        else:
            print(f"WARNING: No topic found for {slug}. Pass topic_title_en to create one.", file=sys.stderr)
            return False
    
    # Ensure topic exists (for EN guides)
    if lang == 'en':
        intent = 'what-is' if title.lower().startswith('what is') else 'how-to'
        run_sql(f"""
            INSERT INTO facil_topics (slug, title_en, category, platform, difficulty, intent, meta)
            VALUES ({esc(slug)}, {esc(topic_title_en or title)}, {esc(cat)}, {esc(plat)}, {esc(diff)}, {esc(intent)}, 
                    '{{"brands": {json.dumps(brands)}}}')
            ON CONFLICT (slug) DO UPDATE SET updated_at = now()
        """, fetch=False)
        en_slug = slug
    
    # Get topic_id
    rows = run_sql(f"SELECT id FROM facil_topics WHERE slug = {esc(en_slug)}")
    if not rows:
        print(f"ERROR: Topic {en_slug} not found", file=sys.stderr)
        return False
    topic_id = rows[0][0]
    
    # Insert guide
    rel_path = os.path.relpath(file_path, "/Users/kiddok/Desktop/labs/facil-guide/")
    url = f"https://facil.guide/{lang}/guide/{slug}/"
    
    run_sql(f"""
        INSERT INTO facil_guides (topic_id, lang, slug, title, description, word_count, step_count, faq_count,
            has_bold_ui_elements, has_faq, has_tips, has_external_links, quality_score, quality_checks,
            file_path, url, status, published_at, meta)
        VALUES ({topic_id}, {esc(lang)}, {esc(slug)}, {esc(title)}, {esc(desc)}, {wc}, {steps}, {faq_count},
            {('**' in body)}, {(faq_count >= 3)}, {quality_checks['has_tips']}, {('http' in body)},
            {quality_score}, {esc(json.dumps(quality_checks))},
            {esc(rel_path)}, {esc(url)}, 'live', {esc(date)}::timestamptz,
            '{{"content_hash": "{chash}", "source_slug": "{en_slug}"}}')
        ON CONFLICT (slug, lang) DO UPDATE SET
            title = EXCLUDED.title, description = EXCLUDED.description,
            word_count = EXCLUDED.word_count, step_count = EXCLUDED.step_count,
            faq_count = EXCLUDED.faq_count, quality_score = EXCLUDED.quality_score,
            quality_checks = EXCLUDED.quality_checks, status = 'live',
            updated_at = now(),
            meta = EXCLUDED.meta
    """, fetch=False)
    
    # Audit log
    run_sql(f"""
        INSERT INTO facil_audit_log (entity_type, entity_id, action, actor, details)
        SELECT 'guide', g.id, 'registered', 'monkey', '{{"slug": "{slug}", "lang": "{lang}", "quality": {quality_score}}}'
        FROM facil_guides g WHERE g.slug = {esc(slug)} AND g.lang = {esc(lang)}
    """, fetch=False)
    
    # Auto-register brands
    for brand in brands:
        run_sql(f"""
            INSERT INTO facil_topic_brands (topic_id, brand_name, relationship)
            VALUES ({topic_id}, {esc(brand)}, 'featured')
            ON CONFLICT (topic_id, brand_name) DO NOTHING
        """, fetch=False)
    
    print(f"OK: {slug} ({lang}) registered. Quality: {quality_score}/100. Words: {wc}. FAQs: {faq_count}.")
    return True

def cmd_deployed(slug, lang):
    """Mark a guide as deployed."""
    run_sql(f"""
        UPDATE facil_guides SET deployed = true, deployed_at = now(), status = 'live', updated_at = now()
        WHERE slug = {esc(slug)} AND lang = {esc(lang)}
    """, fetch=False)
    run_sql(f"""
        INSERT INTO facil_audit_log (entity_type, entity_id, action, actor, details)
        SELECT 'guide', g.id, 'deployed', 'monkey', '{{"slug": "{slug}", "lang": "{lang}"}}'
        FROM facil_guides g WHERE g.slug = {esc(slug)} AND g.lang = {esc(lang)}
    """, fetch=False)
    print(f"OK: {slug} ({lang}) marked as deployed.")

def cmd_sync():
    """Sync all guide files to DB."""
    count = 0
    for lang in ['en', 'fr', 'es', 'pt', 'it']:
        lang_dir = os.path.join(GUIDE_DIR, lang)
        if not os.path.isdir(lang_dir): continue
        for f in sorted(os.listdir(lang_dir)):
            if not f.endswith('.md'): continue
            slug = f.replace('.md', '')
            path = os.path.join(lang_dir, f)
            
            if lang == 'en':
                cmd_register(slug, lang, path)
                count += 1
            else:
                # For translations, try to find topic by checking if topic exists
                # We need the source mapping -- check meta in existing guide or guess
                fm, body, content = parse_guide(path)
                # Try to find existing guide record
                rows = run_sql(f"SELECT meta->>'source_slug' FROM facil_guides WHERE slug={esc(slug)} AND lang={esc(lang)}")
                if rows and rows[0][0]:
                    en_slug = rows[0][0]
                    topic_rows = run_sql(f"SELECT id FROM facil_topics WHERE slug={esc(en_slug)}")
                    if topic_rows:
                        cmd_register(slug, lang, path)
                        count += 1
                else:
                    # Skip unmapped translations for now
                    pass
    
    print(f"\nSynced {count} guides to DB.")

def cmd_gaps():
    """Show translation gaps."""
    print("\n=== TRANSLATION GAPS ===\n")
    rows = run_sql("""
        SELECT t.slug, t.category,
            CASE WHEN en.id IS NOT NULL THEN 'ok' ELSE '--' END,
            CASE WHEN fr.id IS NOT NULL THEN 'ok' ELSE 'MISS' END,
            CASE WHEN es.id IS NOT NULL THEN 'ok' ELSE 'MISS' END,
            CASE WHEN pt.id IS NOT NULL THEN 'ok' ELSE 'MISS' END,
            CASE WHEN it.id IS NOT NULL THEN 'ok' ELSE 'MISS' END
        FROM facil_topics t
        LEFT JOIN facil_guides en ON en.topic_id=t.id AND en.lang='en'
        LEFT JOIN facil_guides fr ON fr.topic_id=t.id AND fr.lang='fr'
        LEFT JOIN facil_guides es ON es.topic_id=t.id AND es.lang='es'
        LEFT JOIN facil_guides pt ON pt.topic_id=t.id AND pt.lang='pt'
        LEFT JOIN facil_guides it ON it.topic_id=t.id AND it.lang='it'
        WHERE fr.id IS NULL OR es.id IS NULL OR pt.id IS NULL OR it.id IS NULL
        ORDER BY t.category, t.slug
    """)
    
    missing = 0
    print(f"{'SLUG':<35} {'CAT':<15} {'EN':<5} {'FR':<5} {'ES':<5} {'PT':<5} {'IT':<5}")
    print("-" * 80)
    for r in rows:
        print(f"{r[0]:<35} {r[1]:<15} {r[2]:<5} {r[3]:<5} {r[4]:<5} {r[5]:<5} {r[6]:<5}")
        missing += sum(1 for x in r[3:] if x == 'MISS')
    print(f"\nTotal missing translations: {missing}")

def cmd_stats():
    """Full stats dashboard."""
    print("\n=== FACIL.GUIDE DASHBOARD ===\n")
    
    # Totals
    rows = run_sql("SELECT COUNT(*) FROM facil_topics")
    print(f"Topics: {rows[0][0]}")
    rows = run_sql("SELECT lang, COUNT(*) FROM facil_guides GROUP BY lang ORDER BY lang")
    total_guides = 0
    for r in rows:
        print(f"  {r[0].upper()}: {r[1]} guides")
        total_guides += int(r[1])
    print(f"  Total: {total_guides} guides")
    
    # Coverage
    rows = run_sql("SELECT COUNT(*) FROM facil_topics")
    total_topics = int(rows[0][0])
    target = total_topics * 5
    pct = round(total_guides / target * 100) if target > 0 else 0
    print(f"\nCoverage: {total_guides}/{target} ({pct}%)")
    print(f"Missing: {target - total_guides} translations")
    
    # Quality
    rows = run_sql("SELECT ROUND(AVG(quality_score)), MIN(quality_score), MAX(quality_score) FROM facil_guides WHERE quality_score IS NOT NULL")
    if rows and rows[0][0]:
        print(f"\nQuality: avg {rows[0][0]}, min {rows[0][1]}, max {rows[0][2]}")
    
    # By category
    print(f"\n{'CATEGORY':<15} {'TOPICS':<8} {'GUIDES':<8} {'COVERAGE':<10}")
    print("-" * 45)
    rows = run_sql("""
        SELECT t.category, COUNT(DISTINCT t.id), COUNT(g.id),
            ROUND(COUNT(g.id)::numeric / (COUNT(DISTINCT t.id) * 5) * 100)
        FROM facil_topics t
        LEFT JOIN facil_guides g ON g.topic_id = t.id
        GROUP BY t.category ORDER BY COUNT(DISTINCT t.id) DESC
    """)
    for r in rows:
        print(f"{r[0]:<15} {r[1]:<8} {r[2]:<8} {r[3]}%")
    
    # Brands
    rows = run_sql("SELECT brand_name, COUNT(*) FROM facil_topic_brands GROUP BY brand_name ORDER BY COUNT(*) DESC LIMIT 10")
    if rows:
        print(f"\nTop brands: {', '.join(f'{r[0]}({r[1]})' for r in rows)}")
    
    # Glossary
    rows = run_sql("SELECT COUNT(*) FROM facil_glossary")
    print(f"Glossary terms: {rows[0][0]}")

def cmd_next(n=5):
    """Show next guides to write by priority."""
    print(f"\n=== NEXT {n} GUIDES TO WRITE ===\n")
    rows = run_sql(f"""
        SELECT t.slug, t.title_en, t.category, t.priority_score,
            COUNT(g.id) as existing_langs,
            5 - COUNT(g.id) as missing_langs
        FROM facil_topics t
        LEFT JOIN facil_guides g ON g.topic_id = t.id
        GROUP BY t.id, t.slug, t.title_en, t.category, t.priority_score
        HAVING COUNT(g.id) < 5
        ORDER BY t.priority_score DESC, missing_langs DESC
        LIMIT {n}
    """)
    for r in rows:
        print(f"  [{r[3]}] {r[1]} ({r[2]}) -- {r[5]} langs missing")

def cmd_quality():
    """Run quality checks on all guides."""
    print("\n=== QUALITY AUDIT ===\n")
    
    low_quality = []
    for lang in ['en', 'fr', 'es', 'pt', 'it']:
        lang_dir = os.path.join(GUIDE_DIR, lang)
        if not os.path.isdir(lang_dir): continue
        for f in sorted(os.listdir(lang_dir)):
            if not f.endswith('.md'): continue
            path = os.path.join(lang_dir, f)
            fm, body, content = parse_guide(path)
            score, checks = compute_quality(fm, body)
            slug = f.replace('.md', '')
            
            # Update DB
            run_sql(f"""
                UPDATE facil_guides SET quality_score = {score}, 
                    quality_checks = {esc(json.dumps(checks))}, updated_at = now()
                WHERE slug = {esc(slug)} AND lang = {esc(lang)}
            """, fetch=False)
            
            if score < 70:
                failed = [k for k, v in checks.items() if not v]
                low_quality.append((slug, lang, score, failed))
    
    if low_quality:
        print(f"{'SLUG':<35} {'LANG':<5} {'SCORE':<7} ISSUES")
        print("-" * 80)
        for slug, lang, score, failed in sorted(low_quality, key=lambda x: x[2]):
            print(f"{slug:<35} {lang:<5} {score:<7} {', '.join(failed)}")
        print(f"\n{len(low_quality)} guides below 70 quality.")
    else:
        print("All guides pass quality threshold (70+).")

def cmd_stale():
    """Show guides that may be stale."""
    rows = run_sql("""
        SELECT t.slug, t.os_version_target, t.freshness_check_at, t.stale
        FROM facil_topics t
        WHERE t.stale = true 
           OR t.freshness_check_at IS NULL 
           OR t.freshness_check_at < now() - interval '60 days'
        ORDER BY t.freshness_check_at NULLS FIRST
    """)
    if rows:
        print(f"\n=== STALE/UNCHECKED GUIDES ===\n")
        for r in rows:
            print(f"  {r[0]} -- OS: {r[1] or 'unset'}, last check: {r[2] or 'never'}, stale: {r[3]}")
    else:
        print("No stale guides detected.")

# ============================================================
# Main
# ============================================================

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == 'sync':
        cmd_sync()
    elif cmd == 'gaps':
        cmd_gaps()
    elif cmd == 'stats':
        cmd_stats()
    elif cmd == 'register' and len(sys.argv) >= 5:
        cmd_register(sys.argv[2], sys.argv[3], sys.argv[4])
    elif cmd == 'deployed' and len(sys.argv) >= 4:
        cmd_deployed(sys.argv[2], sys.argv[3])
    elif cmd == 'next':
        cmd_next(int(sys.argv[2]) if len(sys.argv) > 2 else 5)
    elif cmd == 'quality':
        cmd_quality()
    elif cmd == 'stale':
        cmd_stale()
    else:
        print(__doc__)
