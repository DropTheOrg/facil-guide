# facil.guide -- Decision Log

Every decision made and why. This only grows.

## 2026-02-18

### Astro + Cloudflare Pages, NOT WordPress
**Decision:** Static site generator, not WordPress.
**Why:** Instant page loads (no server), free hosting forever, no security patches, no plugins to maintain. WordPress would cost $5-20/mo for hosting and add complexity we don't need. Seniors need FAST pages.

### 5 Languages (FR, EN, ES, PT, IT)
**Decision:** Start with 5 European languages.
**Why:** Underserved markets. French seniors searching "comment envoyer photo WhatsApp" get worse results than English queries. Less competition, faster to rank.
**Added later:** Italian (IT) added during build, was originally 4 languages.

### Sand/Midnight Theme, NOT BRAND.md Colors
**Decision:** Use DropThe's color system, not the original facil brand colors.
**Why:** Middo explicitly requested it. Consistency with the parent brand. The original BRAND.md had different blues/greens that didn't match.

### No Emojis
**Decision:** Unicode glyphs only for category icons and UI.
**Why:** Middo's preference. Applies globally to all DropThe properties.

### No Affiliate Links (Yet)
**Decision:** No affiliate components until programs are signed up.
**Why:** Don't build UI for something that doesn't exist yet. Add when ready.

### File-Based Routing with Localized Slugs
**Decision:** Per-language static files for about/legal pages, dynamic `[lang]` routes for content.
**Why:** About and legal pages need localized URLs (`/fr/mentions-legales/` not `/fr/legal/`). Dynamic `[lang]` catch-all was creating duplicate pages for every language. Fixed by making FR/EN/ES/PT/IT-specific folders.

### Content-Signal in robots.txt (CF Managed)
**Decision:** Accept CF's prepended robots.txt for now, override with our own + manual CF toggle.
**Why:** CF Pages injects `Content-Signal` directive that Google flags as invalid. Can't disable via API. Need manual toggle in CF dashboard. Our own robots.txt has the same bot blocks using standard directives.

### Hub Page (/all/) for Crawl Depth
**Decision:** Create a master index page linking to all content.
**Why:** Google needs to discover every page within 2-3 clicks of homepage. With 5 languages x many guides, a hub page ensures no content is orphaned. Also helps users browse everything.

### Disclaimers on Every Page
**Decision:** Three layers: footer disclaimer, per-guide disclaimer, full legal page.
**Why:** Seniors following tech guides = liability risk. If someone deletes data following our steps, we need legal protection. All 5 languages covered.

### AI Content Disclosure
**Decision:** Explicit "AI-assisted content" section in legal page.
**Why:** Legal requirement in some jurisdictions. Also builds trust. We're transparent about it.

### WCAG AA Contrast Minimum
**Decision:** All text must pass 4.5:1 contrast ratio.
**Why:** Seniors often have reduced vision. Original `text-muted` color (#8a8478) failed at 2.96:1. Fixed to #685f54 (4.99:1).

### Deploy via Wrangler, Not GitHub Integration
**Decision:** Manual deploy with `wrangler pages deploy`.
**Why:** Cloudflare Pages GitHub integration returns error 8000011. Known CF bug. Direct upload works perfectly. Can be automated via cron later.

### System Fonts, No Web Fonts
**Decision:** Use `system-ui` font stack.
**Why:** Zero font loading time. Familiar to users (they see their system's default font). No CLS from font swap. Proven benefit for seniors (familiar = comfortable).

### External Links to Official Sources
**Decision:** Link to Apple, Google, WhatsApp official pages in guide content.
**Why:** SEO trust signal. Shows Google the content references authoritative sources. Especially important for YMYL-adjacent content (security guides for seniors).

### Search Bar Uses Client-Side Filtering
**Decision:** Vanilla JS filtering, no search service.
**Why:** Static site, no server. JS queries `data-guide-card` attributes on the page. Works offline after page load. Zero dependencies. Fast. Handles "no results" state.

### OG Image Generated from SVG via Sharp
**Decision:** Maintain SVG source, generate PNG with sharp.
**Why:** SVG is editable. PNG is required for social sharing (Twitter/Facebook don't render SVG). Sharp is already an Astro dependency. Original PNG was cropped/off-center.
