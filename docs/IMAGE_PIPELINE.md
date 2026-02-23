# Facil.guide Image Pipeline

## Status: V1 TESTED, PROCESS DEFINED
Last updated: 2026-02-20

## Lessons Learned From Test Runs

### What Failed
1. **Vague prompts** -- "holding a phone happily" produces random garbage. Need exact compositions.
2. **Random cast rotation** -- switching characters per step breaks the visual story.
3. **No fil rouge** -- images must flow like a comic strip, not random stock photos.
4. **AI text/logos** -- FLUX can't reliably render our SVG logo. Brand placement needs post-processing or CSS overlay.
5. **Over-describing emotions** -- "she looks pleasantly surprised" adds nothing. Describe OBJECTS and POSITIONS.

### What Worked
1. **Kontext character consistency** -- same character across all steps when using reference image.
2. **Close-up hands + phone** -- step-4 (tap the link) was the best image. Clear, instructional, no ambiguity.
3. **Reusable endings** -- generic thumbs-up images work for every guide's final step.
4. **Precise spatial descriptions** -- "right hand holds phone, left hand rests on desk, laptop is to the left showing QR code" works way better than "grandma scans QR code."

## The Process (Step-by-Step for Every Guide)

### Phase 1: Plan (Before generating anything)
1. Read the guide content (all steps)
2. Pick ONE primary character (match to guide audience)
3. Define the visual storyboard:
   - For each step: exact camera angle, exact objects, exact positions
   - Which steps need unique images vs reusable assets
4. Identify reusable assets (endings, generic phone-in-hand, etc.)

### Phase 2: Prompt Engineering
Every prompt MUST include these 5 elements:

```
WHO: [character name] from [angle: waist up / close-up hands / medium shot]
WEARING: [exact clothing from reference]
HANDS: [left hand does X, right hand does Y]
OBJECTS: [phone showing X on screen, laptop on desk showing Y, mug on table]
BACKGROUND: [clean white / at a desk / in kitchen]
```

**Example - BAD prompt:**
"Grandma looking at her phone with settings open"

**Example - GOOD prompt:**
"Medium shot of the same grandmother sitting at a wooden desk from three quarter angle. Her right hand holds a black smartphone vertically. The phone screen displays a blue settings page with a gear icon at the top. Her left hand rests flat on the desk next to a closed laptop. Lavender cardigan, white undershirt. Clean white background."

### Phase 3: Generate
1. Hero image (1200x632) using Kontext + character reference
2. Step images (768x768) using Kontext + same character reference
3. Final step = reusable ending image (already generated, just copy)

### Phase 4: Quality Check
- [ ] Same character in every image (clothing, hair, features consistent)
- [ ] Story flows logically (image N follows image N-1)
- [ ] No AI artifacts (extra hands, floating objects, wrong objects)
- [ ] Phone screens show relevant content (not gibberish)
- [ ] No text that needs to be readable (text = CSS overlay layer)
- [ ] Brand placement is organic (not forced, not distracting)

### Phase 5: Post-Process (TODO - not built yet)
- Add brand logo overlay via code (not AI generation)
- Optimize file size (WebP conversion)
- Generate alt text per language

## Cost Optimization Strategy

### Reusable Asset Library (Generate Once, Use Forever)
| Asset | Count | Cost | Reused on |
|---|---|---|---|
| Ending thumbs-up (per character) | 6 | $0.15 | Every guide's final step |
| Character holding phone (neutral) | 6 | $0.15 | Guides where step 1 = "open phone" |
| Character at desk with laptop | 3 | $0.075 | Any guide involving computer |
| Character looking confused | 3 | $0.075 | "If it doesn't work" troubleshooting steps |
| **Total reusable library** | **~20** | **$0.50** | **Saves ~$0.05-0.10 per guide** |

### Per-Guide Cost Breakdown
| Image Type | Model | Cost | Count |
|---|---|---|---|
| Hero | Kontext dev | $0.025 | 1 |
| Unique step images | Kontext dev | $0.025 | 3-4 per guide |
| Reusable steps | FREE (from library) | $0 | 1-2 per guide |
| **Total per guide** | | **$0.10-0.125** | 5-6 images |

### At Scale
| Guides | Unique images | Reused | Total cost |
|---|---|---|---|
| 100 | 400 | 200 | $10 |
| 1,000 | 4,000 | 2,000 | $100 |
| 10,000 | 40,000 | 20,000 | $1,000 |

### Sweet Spot: 60% unique + 40% reusable
- Every guide gets 3-4 truly unique step images (the ones that show the actual action)
- 1-2 images are from the reusable library (opening phone, ending, troubleshooting)
- Hero is always unique

## Character Assignment Rules

| Guide Category | Primary Character | Why |
|---|---|---|
| Smartphone basics | Grandma or Grandpa | Target audience |
| Social media | Mom or Dad | Younger audience |
| Gaming / apps | Boy or Girl | Kids teach grandparents |
| Email / work tools | Dad | Professional context |
| Photos / memories | Grandma | Emotional connection |
| Safety / security | Grandpa | Trust, authority |

## Image Specs

| Type | Dimensions | Format | Model |
|---|---|---|---|
| Hero / OG card | 1200x632 | PNG -> WebP | Kontext dev |
| Step image | 768x768 | PNG -> WebP | Kontext dev |
| Reusable ending | 768x768 | PNG -> WebP | Kontext dev |
| Category header | 1200x632 | PNG -> WebP | Kontext dev |

## File Structure
```
src/assets/guides/{slug}/
  hero.png
  step-1.png
  step-2.png
  step-3.png
  step-4.png      (may be reusable ending symlink)

docs/images/brand/
  cast-ref-{character}.png    # 6 character references
  ending-{character}.png      # 6 reusable endings
  mascot-reference.png        # Ghost mascot
  logo-coral.svg              # Brand logo (coral bg)
  logo-mark.svg               # Brand logo (transparent)
  favicon.svg                 # Favicon
```

## Brand Placement Strategy
**DO NOT rely on AI to render the logo.** FLUX can't do it reliably.

Instead:
1. Generate clean images with white/neutral surfaces where logo COULD go
2. Overlay logo via CSS/SVG compositing in post-processing
3. OR: accept that brand placement lives in the SITE DESIGN (header, favicon, footer) not in every image

**For now: skip in-image brand placement. Focus on quality step images. Brand is the site itself.**

## API Config
- Provider: Together.ai
- Key: in credentials.md
- Model for character scenes: `black-forest-labs/FLUX.1-kontext-dev` ($0.025/image)
- Model for generic scenes (no character): `black-forest-labs/FLUX.1-schnell` ($0.003/image)
- Response format: b64_json (URL download is unreliable)
- Dimensions must be multiples of 8

## TODO Before Automation
1. [ ] Build reusable asset library (20 images, ~$0.50)
2. [ ] Create prompt template system (slug -> step descriptions -> prompts)
3. [ ] Build post-processing pipeline (resize, WebP, alt text)
4. [ ] Wire into content cron (generate images after guide text is written)
5. [ ] Integrate into Astro build (frontmatter reference to image folder)
6. [ ] Set up R2 bucket for production (before 100+ guides)
