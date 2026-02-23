# facil.guide -- Changelog

All changes in reverse chronological order.

## 2026-02-18

### Phase 1: Initial Build
- **Astro scaffold** -- 5 languages, 3 content types, 7 categories
- **Content:** 12 sample guides, 5 reviews, 5 comparisons (30 markdown files)
- **Components:** Header, Footer, SearchBar, GuideCard, CategoryNav, Breadcrumb, FaqSection, SchemaMarkup, LanguageSwitcher, BackToTop, GuideDisclaimer
- **JSON-LD schema:** HowTo, Product+Review, FAQPage, BreadcrumbList, WebSite
- **Print stylesheet**
- **Search bar** with live client-side filtering

### Phase 2: Theme & Design
- **Sand/Midnight dual theme** -- matching DropThe design system
- **Theme toggle** in header (sun/moon glyph)
- **System dark mode** detection via `prefers-color-scheme`
- **Mobile responsive** -- fluid grids, sticky header, touch-optimized
- **Category glyphs** -- Unicode characters, no emojis

### Phase 3: Deployment
- **Cloudflare Pages** deployment via wrangler
- **Custom domains:** facil.guide + www.facil.guide
- **SSL** auto-provisioned
- **Live at:** https://facil.guide

### Phase 4: SEO Foundation
- **Canonical URLs** on every page
- **OG image** (1200x630) + Twitter cards
- **DropThe attribution** in footer
- **Sitemap** auto-generated (87 URLs)
- **robots.txt** -- AI scrapers blocked, search allowed

### Phase 5: Legal & Liability
- **Footer disclaimer** on every page (5 languages)
- **GuideDisclaimer component** on every guide/review/comparison
- **Legal pages** -- 5 languages, 5 sections each:
  - No liability
  - Not professional advice
  - Third-party products
  - Software changes
  - AI-assisted content disclosure
- Legal page URLs: `/fr/mentions-legales/`, `/en/legal/`, `/es/aviso-legal/`, `/pt/aviso-legal/`, `/it/avviso-legale/`

### Phase 6: Internal Linking & SEO Fixes
- **Hub page** (`/all/`) -- master index of all content grouped by category
  - Table of contents with anchor links and counts
  - Category headings link to category pages
  - Search bar filters all content types
- **Header nav:** added "Browse all" link
- **Fixed duplicate pages** -- `/en/a-propos/`, `/es/a-propos/` etc. removed (was FR slug generated for all langs)
- **Fixed section headings** -- Reviews/Comparisons now use proper translations (was showing raw "verdict" and "vs")

### Phase 7: Visual Fixes
- **OG image regenerated** from SVG via sharp (was cropped/off-center)
- **Favicon regenerated** -- 32px and 180px PNGs from SVG
- **Search bar fixed** -- `readyState` check, no-results message, section hiding
- **WCAG contrast fix** -- `text-muted` updated:
  - Sand: `#8a8478` (2.96:1) -> `#685f54` (4.99:1)
  - Midnight: `#666666` (3.45:1) -> `#888888` (5.58:1)

## Stats

| Metric | Value |
|--------|-------|
| Total pages | 87 |
| Content files | 30 |
| Languages | 5 |
| Components | 12 |
| Build time | ~600ms |
| Bundle size | ~8KB CSS, ~2KB JS |
| Hosting cost | $0 |
| Git commits | 12 |
