# Task Log

## Task 1: Share hero images across all languages
**Status:** DONE
**Date:** 2026-02-20 23:48
**Commit:** 67cad8d

### Problem
Hero images stored under EN slug folders (e.g. `assets/guides/scan-qr-code/`). Translated guides have different slugs (e.g. FR `scanner-qr-code`) and couldn't find their hero images.

### Solution
- Completed `guideSlugMap` in `slugmap.ts` with all 66 EN<->FR/ES/PT/IT mappings
- Added `getBaseSlug(localizedSlug)` function that reverse-looks up the EN slug
- Updated `[slug].astro` + 3 listing pages to use `getBaseSlug` for hero image resolution

### What works now
- All 5 languages share the same hero images (stored under EN slug folder)
- og:image on translated guide pages points to the shared hero
- Card thumbnails on all listing pages (home, category, /all/) in all languages
- Alt text = guide title in the correct language
- Country-specific guides without EN equivalent gracefully show no hero

### Files changed
- `src/i18n/slugmap.ts` - complete 66-entry guideSlugMap + getBaseSlug()
- `src/pages/[lang]/guide/[slug].astro` - use getBaseSlug
- `src/pages/[lang]/index.astro` - use getBaseSlug for card images
- `src/pages/[lang]/[category]/index.astro` - same
- `src/pages/[lang]/all/index.astro` - same

### Notes
- `forgot-password-recovery` and `forgot-password-what-to-do` both map to FR `mot-de-passe-oublie` (content duplication in FR, not a mapping bug)
- `phone-storage-full` and `phone-storage-full-fix` share some translations (same issue)
- When adding new guides: add entry to `guideSlugMap` for cross-language image sharing

## Task 2: Category images with brand design
**Status:** DONE
**Date:** 2026-02-20 23:51
**Commit:** 0113926

- 10 category illustrations generated via Together.ai FLUX.1-schnell ($0.03)
- Brand style: coral/teal accents, ghost mascot appearances, warm scenes
- CategoryNav component updated with image support + localized alt text in 5 languages
- Responsive: 80px desktop, 60px tablet, 50px mobile

## Task 3: Add SVG ghost logo to header
**Status:** DONE
**Date:** 2026-02-21 00:32
**Commit:** 7bd20dd

- Inline coral ghost SVG mark (28px) in header, (24px) in footer
- Uses CSS variables for theme adaptation
- Preserved text logo for SEO/accessibility

## Task 4: Rethink categories and homepage
**Status:** DONE
**Date:** 2026-02-21 00:37
**Commits:** d39aa25, 0c3dbe6

### 4a: Popular guides section
- Curated 10 universally useful guides (6 displayed)
- Cross-language support via slugmap
- Section between categories and latest on homepage

### 4b: Device & difficulty filters on /all/ page
- Filter tabs: All / iPhone / Android / Computer
- Difficulty tabs: All levels / Easy / Medium
- Client-side JS filtering, hides empty categories
- Localized in all 5 languages

## Task 6: Discovery & navigation improvements
**Status:** DONE (merged with Task 4b)

- Device and difficulty filters on /all/ page
- TOC with jump links to categories already existed
- Filter + search combination enables full discovery
