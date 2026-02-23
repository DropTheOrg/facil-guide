# facil.guide -- Design System

## Themes

Two themes matching DropThe's design system. User toggles via sun/moon button in header. System preference auto-detected.

### Sand Theme (Light, Default)

| Token | Value | Usage |
|-------|-------|-------|
| `--fg-bg` | `#ebe5d9` | Page background |
| `--fg-bg-card` | `#e0dace` | Card/surface background |
| `--fg-bg-warm` | `#d4cec2` | Hover/active states |
| `--fg-text` | `#1a1815` | Primary text (14.12:1 contrast) |
| `--fg-text-light` | `#4a4640` | Body text (7.47:1) |
| `--fg-text-muted` | `#685f54` | Secondary text (4.99:1) |
| `--fg-border` | `#c8c2b6` | Borders |
| `--fg-primary` | `#1E3A5F` | Links, brand color (navy) |
| `--fg-accent` | `#2E7D32` | Success, accent (green) |

### Midnight Theme (Dark)

| Token | Value | Usage |
|-------|-------|-------|
| `--fg-bg` | `#0a0a0a` | Page background |
| `--fg-bg-card` | `#161616` | Card/surface background |
| `--fg-text` | `#ffffff` | Primary text (19.80:1) |
| `--fg-text-light` | `#aaaaaa` | Body text (8.52:1) |
| `--fg-text-muted` | `#888888` | Secondary text (5.58:1) |
| `--fg-primary` | `#93b8fd` | Links (light blue) |
| `--fg-accent` | `#86efac` | Success, accent (light green) |

## Accessibility

- **WCAG AA** minimum on all text (4.5:1 contrast ratio)
- `--fg-text-muted` was fixed from failing (2.96) to passing (4.99) on 2026-02-18
- **48px minimum touch targets** on all interactive elements
- **18px minimum text size** for body content
- **System fonts** -- no custom font loading, respects user preferences
- **Skip to content** link
- **Semantic HTML** -- proper heading hierarchy, landmarks, ARIA labels
- **Print stylesheet** included
- **Focus indicators** on all interactive elements
- **prefers-color-scheme** respected for auto dark mode

## Typography

```css
font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
```

No web fonts. System fonts only. Fast, accessible, familiar to seniors.

| Element | Size | Weight |
|---------|------|--------|
| H1 | 2.25rem | 700 |
| H2 | 1.6rem | 700 |
| H3 | 1.25rem | 600 |
| Body | 1.1rem (18px) | 400 |
| Card desc | 0.95rem | 400 |
| Badge/meta | 0.85rem | 600 |

## Category Glyphs

No emojis. Unicode glyphs only.

| Category | Glyph | Unicode |
|----------|-------|---------|
| Smartphone | ✆ | U+2706 |
| Computer | ⌘ | U+2318 |
| Internet | ☉ | U+2609 |
| Applications | ▦ | U+25A6 |
| Security | ☖ | U+2616 |
| Communication | ✉ | U+2709 |
| AI | ⚙ | U+2699 |

## Favicon

- SVG: Navy rounded square (`#1E3A5F`) with green "f." text (`#4ADE80`)
- ICO: 32x32 PNG version
- Apple touch icon: 180x180 PNG version
- Generated from SVG via `sharp` library

## OG Image (Sharing Card)

- 1200x630 PNG
- Sand background (`#ebe5d9`)
- Centered "facil.guide" logo (navy + green dot + dark)
- "Tech, simplified." tagline
- "Step-by-step guides in 5 languages" subtitle
- Navy footer bar with "A DropThe project"
- Source SVG at `public/og-image.svg`, PNG regenerated via `sharp`

## Component Styles

All styles are scoped within Astro components (CSS `<style>` blocks). Global styles in `src/styles/global.css` define:
- CSS reset
- Theme variables
- Typography defaults
- Utility classes (`.fg-container`, `.fg-card`, `.fg-btn`, `.fg-badge`, `.fg-section`)
- Responsive breakpoints (768px, 640px)

## Design Rules

1. No emojis anywhere -- glyphs only
2. Use CSS custom properties, never hardcode colors
3. All interactive elements: min 48px height
4. All body text: min 18px
5. Cards have subtle shadow + border, not heavy drop shadows
6. Consistent spacing: 1.25rem gaps in grids, 2.5rem section padding
7. Clean, calm aesthetic -- seniors should feel comfortable, not overwhelmed
