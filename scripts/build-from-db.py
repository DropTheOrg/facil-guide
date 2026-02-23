#!/usr/bin/env python3
"""
Build script: Pull guides from PostgreSQL and generate .md files + slugmap.
Run before `npm run build` to sync DB -> files.

Usage: python3 scripts/build-from-db.py [--only-translated] [--dry-run]
"""

import os
import sys
import json
import subprocess

PSQL = '/opt/homebrew/Cellar/postgresql@17/17.7_1/bin/psql'
DB = 'dropthe'
GUIDES_DIR = 'src/content/guides'
SLUGMAP_PATH = 'src/i18n/slugmap.ts'

ONLY_TRANSLATED = '--only-translated' in sys.argv
DRY_RUN = '--dry-run' in sys.argv


def query_json(sql):
    """Run SQL and return rows as JSON array"""
    wrapped = f"SELECT json_agg(t) FROM ({sql}) t"
    r = subprocess.run([PSQL, '-d', DB, '-t', '-A', '-c', wrapped],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(f"SQL ERROR: {r.stderr}", file=sys.stderr)
        sys.exit(1)
    result = r.stdout.strip()
    if not result or result == '':
        return []
    return json.loads(result)


def escape_yaml(s):
    return s.replace('\\', '\\\\').replace('"', '\\"')


def main():
    status_filter = "AND t.status = 'translated'" if ONLY_TRANSLATED else ""
    
    sql = f"""
    SELECT t.lang, t.slug, t.title, t.description, t.body, t.faq, t.status,
           tp.slug as topic_slug, tp.category, tp.platform, tp.difficulty,
           g.step_count
    FROM facil_translations t
    JOIN facil_guides g ON g.id = t.guide_id
    JOIN facil_topics tp ON tp.id = g.topic_id
    WHERE 1=1 {status_filter}
    ORDER BY tp.slug, t.lang
    """
    
    rows = query_json(sql)
    if not rows:
        print("No translations found!")
        return
    
    print(f"Found {len(rows)} translations")
    
    diff_map = {'beginner': 'facile', 'intermediate': 'moyen', 'advanced': 'avance'}
    slug_families = {}
    generated = 0
    
    for row in rows:
        lang = row['lang']
        slug = row['slug']
        title = row['title']
        desc = row['description']
        body = row['body']
        faq_list = row['faq'] if row['faq'] else []
        status = row['status']
        topic_slug = row['topic_slug']
        category = row['category']
        platform = row['platform'] or ''
        difficulty = diff_map.get(row['difficulty'], 'facile')
        step_count = row['step_count'] or 5
        
        # Build FAQ YAML
        if faq_list:
            faq_yaml = "faq:\n"
            for item in faq_list:
                q = escape_yaml(item.get('question', ''))
                a = escape_yaml(item.get('answer', ''))
                faq_yaml += f'  - question: "{q}"\n    answer: "{a}"\n'
        else:
            faq_yaml = "faq: []"
        
        md_content = f'''---
title: "{escape_yaml(title)}"
description: "{escape_yaml(desc)}"
lang: "{lang}"
category: "{category}"
difficulty: "{difficulty}"
steps: {step_count}
platform: "{platform}"
date: "2026-02-23"
{faq_yaml}
---

{body}
'''
        
        file_path = os.path.join(GUIDES_DIR, lang, f'{slug}.md')
        
        if DRY_RUN:
            marker = "DRAFT" if status == 'draft' else "OK"
            print(f"  [{marker}] {file_path}")
        else:
            os.makedirs(os.path.join(GUIDES_DIR, lang), exist_ok=True)
            with open(file_path, 'w') as f:
                f.write(md_content)
        
        generated += 1
        
        if topic_slug not in slug_families:
            slug_families[topic_slug] = {}
        slug_families[topic_slug][lang] = slug
    
    print(f"Generated: {generated} files")
    
    if not DRY_RUN:
        generate_slugmap(slug_families)
    
    print("Done.")


def generate_slugmap(families):
    with open(SLUGMAP_PATH) as f:
        content = f.read()
    
    review_idx = content.index('export const reviewSlugMap')
    after_guide = content[review_idx:]
    guide_idx = content.index('export const guideSlugMap')
    header = content[:guide_idx]
    
    lines = ["export const guideSlugMap: Record<string, Record<string, string>> = {"]
    
    for topic_slug in sorted(families.keys()):
        slugs = families[topic_slug]
        parts = []
        for lang in ['en', 'fr', 'es', 'pt', 'it']:
            if lang in slugs:
                parts.append(f"{lang}: '{slugs[lang]}'")
        lines.append(f"  '{topic_slug}': {{ {', '.join(parts)} }},")
    
    lines.append("};")
    lines.append("")
    
    new_content = header + '\n'.join(lines) + '\n\n' + after_guide
    
    with open(SLUGMAP_PATH, 'w') as f:
        f.write(new_content)
    
    print(f"Slugmap updated: {len(families)} entries")


if __name__ == '__main__':
    main()
