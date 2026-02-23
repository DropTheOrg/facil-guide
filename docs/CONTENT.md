# facil.guide -- Content Guide

## Adding a New Guide

### 1. Create the markdown file

File: `src/content/guides/{lang}/{slug}.md`

```markdown
---
title: "How to Do Something"
description: "A clear description for SEO."
category: "smartphone"
steps: 5
difficulty: "facile"
platform: "iphone"
lang: "en"
date: "2026-02-18"
faq:
  - question: "Common question?"
    answer: "Clear answer."
  - question: "Another question?"
    answer: "Another answer."
---

## What you will learn

Brief intro paragraph explaining what the reader will learn and why it matters.

## What you need

- Device requirement 1
- Device requirement 2

## Step-by-step instructions

### Step 1: First action

Explanation. Bold the **key UI elements** the user needs to find.

### Step 2: Second action

Continue with clear, simple language.

### Step 3: Third action

...

## Tips

- Practical tip 1
- Practical tip 2
```

### 2. Create translations

Copy the same file to each language folder with translated content and a localized slug:
- `src/content/guides/fr/{slug-fr}.md` (lang: "fr")
- `src/content/guides/es/{slug-es}.md` (lang: "es")
- `src/content/guides/pt/{slug-pt}.md` (lang: "pt")
- `src/content/guides/it/{slug-it}.md` (lang: "it")

### 3. Build and deploy

```bash
npm run build && CLOUDFLARE_ACCOUNT_ID="166e52169c00e38f7054c88ba803c9f7" npx wrangler pages deploy dist --project-name facil-guide --branch main --commit-dirty=true
```

## Adding a Review

File: `src/content/reviews/{lang}/{slug}.md`

```markdown
---
title: "Product Name: Full Review"
description: "SEO description."
productName: "Product Name"
brand: "Brand"
category: "smartphone"
rating: 4.5
price: "$149"
pros:
  - "Pro 1"
  - "Pro 2"
cons:
  - "Con 1"
  - "Con 2"
verdict: "Summary verdict in one sentence."
platform: "iphone"
lang: "en"
date: "2026-02-18"
faq:
  - question: "Question?"
    answer: "Answer."
---

## Overview

Product introduction...

## Design and Build

...

## Verdict

Summary.
```

## Adding a Comparison

File: `src/content/comparisons/{lang}/{slug}.md`

```markdown
---
title: "Product A vs Product B: Which to Choose?"
description: "SEO description."
productA:
  name: "Product A"
  brand: "Brand A"
  price: "$149"
productB:
  name: "Product B"
  brand: "Brand B"
  price: "$429"
category: "smartphone"
winner: "Product A"
recommendation: "Choose A if... Choose B if..."
lang: "en"
date: "2026-02-18"
faq:
  - question: "Question?"
    answer: "Answer."
---

## Overview

Why compare these two...

## Design

...

## Our Recommendation

Summary.
```

## Categories

| Key | EN Name | Glyph |
|-----|---------|-------|
| `smartphone` | Smartphone | ✆ |
| `ordinateur` | Computer | ⌘ |
| `internet` | Internet | ☉ |
| `applications` | Applications | ▦ |
| `securite` | Security | ☖ |
| `communication` | Communication | ✉ |
| `ia` | Artificial Intelligence | ⚙ |

## Platforms

`iphone` | `android` | `web` | `windows` | `mac`

## Difficulty Levels

| Key | EN | Badge Color |
|-----|-----|------------|
| `facile` | Easy | Green |
| `moyen` | Medium | Orange |
| `avance` | Advanced | Blue |

## Content Rules

1. **No emojis.** Glyphs only.
2. **AI disclosure.** Every page has "AI-assisted content" in legal notice.
3. **No affiliate links** until programs are signed.
4. **External links** to official product pages/help docs are encouraged (SEO signal).
5. **FAQ section** strongly recommended -- generates FAQPage schema for rich results.
6. **2-4 external links** per guide to official sources.
7. **Bold key UI elements** ("Tap **Settings**", "Click **Send**").
8. **Simple language.** No jargon. Explain every term.
9. **Numbered steps** in H3 format: `### Step 1: Action`.
10. **Disclaimer** auto-added to bottom of every guide/review/comparison.

## Current Content Inventory

| Lang | Guides | Reviews | Comparisons | Total |
|------|--------|---------|-------------|-------|
| EN | 4 | 1 | 1 | 6 |
| FR | 4 | 1 | 1 | 6 |
| ES | 4 | 1 | 1 | 6 |
| PT | 4 | 1 | 1 | 6 |
| IT | 4 | 1 | 1 | 6 |
| **Total** | **20** | **5** | **5** | **30** |

### Existing Guides (EN titles)
1. How to send a photo on WhatsApp (applications/iphone)
2. How to video call on iPhone (communication/iphone)
3. What Is ChatGPT and How to Use It (ia/web)
4. How to Recognize a Scam Email (securite/web)

### Existing Reviews
1. Jitterbug Smart4: Full Review (smartphone)

### Existing Comparisons
1. Jitterbug Smart4 vs iPhone SE (smartphone)
