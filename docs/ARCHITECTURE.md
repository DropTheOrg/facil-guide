# facil.guide -- Architecture

## Stack

- **Framework:** Astro 5.x (static site generator)
- **Output:** Static HTML (`dist/` folder, ~87 pages)
- **Hosting:** Cloudflare Pages (free tier, global CDN)
- **Dependencies:** Only `astro` + `@astrojs/sitemap`. Zero JS frameworks. Zero CSS frameworks.
- **Build time:** ~600ms

## File Structure

```
facil-guide/
├── astro.config.mjs          # Astro config: site URL, i18n, sitemap
├── package.json               # Node deps (astro + sitemap only)
├── tsconfig.json              # TypeScript config
├── public/                    # Static assets (copied as-is to dist/)
│   ├── favicon.svg            # SVG favicon (navy bg, green "f.")
│   ├── favicon.ico            # 32px PNG favicon
│   ├── apple-touch-icon.png   # 180px icon for iOS/social
│   ├── apple-touch-icon.svg   # SVG source
│   ├── og-image.png           # 1200x630 sharing card
│   ├── og-image.svg           # SVG source for og-image
│   └── robots.txt             # SEO robots (AI scrapers blocked)
├── docs/                      # This documentation
├── src/
│   ├── content/               # Markdown content (guides, reviews, comparisons)
│   │   ├── guides/            # Step-by-step how-to guides
│   │   │   ├── en/            # English guides
│   │   │   ├── fr/            # French guides
│   │   │   ├── es/            # Spanish guides
│   │   │   ├── pt/            # Portuguese guides
│   │   │   └── it/            # Italian guides
│   │   ├── reviews/           # Product reviews (same lang structure)
│   │   └── comparisons/       # A vs B comparisons (same lang structure)
│   ├── content.config.ts      # Content collection schemas (Zod)
│   ├── components/            # Astro components
│   │   ├── Header.astro       # Sticky header: logo, nav, lang switcher, theme toggle
│   │   ├── Footer.astro       # Footer: logo, nav, legal link, disclaimer, DropThe attribution
│   │   ├── SearchBar.astro    # Live search: filters cards by title/description
│   │   ├── GuideCard.astro    # Card component for guide listings
│   │   ├── GuideDisclaimer.astro  # Per-guide liability disclaimer
│   │   ├── CategoryNav.astro  # Category grid with glyph icons
│   │   ├── Breadcrumb.astro   # Breadcrumb navigation
│   │   ├── FaqSection.astro   # FAQ accordion (generates FAQPage schema)
│   │   ├── SchemaMarkup.astro # JSON-LD structured data
│   │   ├── LanguageSwitcher.astro # 5-language switcher (FR/EN/ES/PT/IT)
│   │   ├── BackToTop.astro    # Scroll-to-top button
│   │   └── StepBlock.astro    # (unused, steps render from markdown)
│   ├── layouts/
│   │   └── BaseLayout.astro   # Master layout: head (meta, OG, hreflang), header, main, footer
│   ├── i18n/
│   │   ├── translations.ts    # All UI strings in 5 languages (~60 keys per lang)
│   │   ├── legal.ts           # Legal page content in 5 languages
│   │   └── utils.ts           # Lang detection, path helpers, category icons
│   ├── pages/                 # Page routes (file-based routing)
│   │   ├── index.astro        # Root redirect (auto-detects lang)
│   │   ├── 404.astro          # 404 page
│   │   ├── [lang]/            # Dynamic lang routes (generates for all 5 langs)
│   │   │   ├── index.astro    # Homepage per language
│   │   │   ├── [category]/index.astro  # Category page (7 categories)
│   │   │   ├── guide/[slug].astro      # Individual guide page
│   │   │   ├── review/[slug].astro     # Individual review page
│   │   │   ├── compare/[slug].astro    # Individual comparison page
│   │   │   └── all/index.astro         # Hub page: all content, grouped by category
│   │   ├── fr/                # FR-specific pages (localized slugs)
│   │   │   ├── a-propos/      # About (FR)
│   │   │   └── mentions-legales/  # Legal (FR)
│   │   ├── en/                # EN-specific pages
│   │   │   ├── about/         # About (EN)
│   │   │   └── legal/         # Legal (EN)
│   │   ├── es/                # ES-specific pages
│   │   │   ├── acerca-de/     # About (ES)
│   │   │   └── aviso-legal/   # Legal (ES)
│   │   ├── pt/                # PT-specific pages
│   │   │   ├── sobre/         # About (PT)
│   │   │   └── aviso-legal/   # Legal (PT)
│   │   └── it/                # IT-specific pages
│   │       ├── chi-siamo/     # About (IT)
│   │       └── avviso-legale/ # Legal (IT)
│   └── styles/
│       └── global.css         # All CSS: themes, typography, utilities, components
└── dist/                      # Build output (deployed to CF Pages)
```

## Page Types & URLs

| Type | URL Pattern | Template | Count per lang |
|------|-------------|----------|----------------|
| Homepage | `/{lang}/` | `[lang]/index.astro` | 1 |
| Category | `/{lang}/{category}/` | `[lang]/[category]/index.astro` | 7 |
| Guide | `/{lang}/guide/{slug}/` | `[lang]/guide/[slug].astro` | 4* |
| Review | `/{lang}/review/{slug}/` | `[lang]/review/[slug].astro` | 1* |
| Comparison | `/{lang}/compare/{slug}/` | `[lang]/compare/[slug].astro` | 1* |
| Hub (all) | `/{lang}/all/` | `[lang]/all/index.astro` | 1 |
| About | `/{lang}/{localized-slug}/` | `{lang}/{slug}/index.astro` | 1 |
| Legal | `/{lang}/{localized-slug}/` | `{lang}/{slug}/index.astro` | 1 |

*Current content count, will grow.

## Content Schema (Zod)

### Guide frontmatter
```yaml
title: string          # "How to send a photo on WhatsApp"
description: string    # SEO description
category: enum         # smartphone|ordinateur|internet|applications|securite|communication|ia
steps: number          # Step count (displayed on cards)
difficulty: enum       # facile|moyen|avance
platform: enum         # iphone|android|web|windows|mac
lang: enum             # fr|en|es|pt|it
date: string           # "2026-02-18"
faq:                   # Optional FAQ array (generates FAQPage schema)
  - question: string
    answer: string
```

### Review frontmatter
```yaml
title, description, category, lang, date  # Same as guide
productName: string    # "Jitterbug Smart4"
brand: string          # "Lively"
rating: number         # 0-5
price: string          # "$149"
pros: string[]         # List of pros
cons: string[]         # List of cons
verdict: string        # Summary verdict
platform: enum?        # Optional
faq: FaqItem[]?        # Optional
```

### Comparison frontmatter
```yaml
title, description, category, lang, date  # Same as guide
productA: { name, brand, price }
productB: { name, brand, price }
winner: string?        # Optional winner name
recommendation: string # Summary recommendation
faq: FaqItem[]?        # Optional
```

## Components Detail

### SearchBar
- Live client-side filtering via `input` event
- Queries all `[data-guide-card]` elements on the page
- Matches against `data-guide-title` and `data-guide-desc` attributes
- Hides empty sections when all their cards are filtered
- Shows "no results" message when nothing matches
- Works on homepage, category pages, and hub page

### SchemaMarkup
Generates JSON-LD for:
- **HowTo** (guides): steps from markdown headings
- **Product + Review** (reviews): rating, price, brand
- **FAQPage** (any page with faq frontmatter)
- **BreadcrumbList** (all pages)
- **WebSite** (homepage)

### Footer
Three layers:
1. Navigation: Home, About, Legal
2. Disclaimer: "Guides provided for informational purposes only..."
3. Attribution: "A project by DropThe"

### GuideDisclaimer
Shown at bottom of every guide, review, and comparison:
"This guide is provided for informational purposes. Steps may vary depending on your device..."

## i18n System

- 5 languages: FR (default), EN, ES, PT, IT
- All URLs prefixed: `/fr/`, `/en/`, `/es/`, `/pt/`, `/it/`
- Translation keys in `src/i18n/translations.ts` (~60 keys per language)
- Legal page content in `src/i18n/legal.ts`
- About/Legal pages have localized slugs (e.g., `/fr/mentions-legales/`, `/en/legal/`)
- Language switcher in header, all pages
- Root `/` auto-detects browser language and redirects
