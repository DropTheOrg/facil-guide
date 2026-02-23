# Facil.guide Image System

## Status: SETUP COMPLETE, STRATEGY PENDING

Last updated: 2026-02-20

## Tooling

### Model
- **FLUX.1-schnell** by Black Forest Labs
- 12B params, Apache 2.0 license (fully commercial)
- Downloaded and cached at `~/.cache/huggingface/hub/models--black-forest-labs--FLUX.1-schnell/` (~25GB)
- HuggingFace auth: token `[REDACTED]`, FLUX license accepted

### Runtime
- **Python diffusers** library (not DrawThings, not ComfyUI)
- Venv: `/Users/kiddok/Desktop/labs/facil-guide/venv-flux/`
- Apple Silicon MPS backend with **CPU offload** (sequential_cpu_offload)
- Required because full model needs ~30GB VRAM, Mac Mini has 24GB unified
- Attention slicing enabled (slice_size=1) for memory efficiency

### Dependencies (venv-flux)
- torch 2.10.0
- diffusers 0.36.0
- transformers 5.2.0
- accelerate 1.12.0
- sentencepiece, protobuf

### Generation Script
- Location: `/Users/kiddok/Desktop/labs/facil-guide/scripts/generate_image.py`
- Usage: `python generate_image.py --slug "backup-phone" --prompt "description" [--seed N]`
- Test: `python generate_image.py --test`
- Default output: `src/assets/guides/{slug}/hero.png`
- Default size: 768x768
- Default steps: 4 (schnell is optimized for 1-4 steps)
- Guidance scale: 0.0 (schnell doesn't use guidance)

### Performance
- Model load: ~1 second (cached)
- Generation: ~6-7 minutes per image (CPU offload mode)
- Bottleneck: sequential CPU offload shuffles layers between CPU and MPS
- Pure MPS would be ~10 seconds but OOMs on 24GB

### Style Prompt (Current Default)
Appended automatically to every user prompt:
```
flat vector illustration, minimal clean design,
simplified device mockup, soft pastel colors,
coral and teal accent colors, white background,
no text in image, no watermark,
friendly and approachable style for seniors,
large clear icons, high contrast
```

## Current Image Inventory

| File | Guide | Prompt |
|------|-------|--------|
| `src/assets/guides/test/hero.png` | test | smartphone with cloud backup progress bar |
| `src/assets/guides/send-photo-email/hero.png` | send-photo-email | smartphone with envelope and photo attachment |

## Architecture Decisions (PENDING)

These need strategic planning before implementation:

### Image Storage & Hosting
- Option A: In-repo (`src/assets/guides/{slug}/`) -- Astro optimizes at build
- Option B: Cloudflare R2 + CDN -- scales better for thousands of images
- Option C: Hybrid -- heroes in repo, step images on R2
- Current: Option A (2 test images in repo)

### Image Types Per Guide
- Hero image (1 per guide) -- confirmed needed
- Step illustrations (1 per step?) -- TBD
- OG/social card -- TBD (could be auto-generated from hero)

### Naming Convention
- TBD: `hero.png` vs `{slug}-hero.png` vs semantic names
- SEO implications of filename

### Alt Text & SEO
- Alt text per language (5 languages)
- Storage: frontmatter? DB? JSON sidecar?
- ImageObject schema markup
- OG image meta tags

### Branding & Visual Identity
- Facil color palette: Coral (#E8735A) + Teal (#2A6B6B) + Warm white (#FAFAF7) -- proposed, not finalized
- Mascot: not decided
- Logo watermark on images: not decided
- Consistent style lock across all guides: need to define and test

### Rollout Plan
- Phase 1: 1 guide, full pipeline test
- Phase 2: 5 guides, verify consistency
- Phase 3: 10 guides, check at scale
- Phase 4: All existing + auto-generate for new
- Retroactive: generate for all 14 existing EN guides

## Environment Variables
None needed -- HuggingFace token is cached via `huggingface_hub.login()` in `~/.cache/huggingface/token`.

## Known Limitations
1. **6-7 min/image** -- CPU offload is slow. Options to speed up:
   - Quantized 8-bit model (~2x faster, slight quality loss)
   - 512x512 resolution (~2x faster)
   - Upgrade to 32GB+ Mac (pure MPS, ~10 sec)
2. **No text rendering** -- by design. Text labels added via CSS overlay per language.
3. **Style consistency** -- FLUX doesn't guarantee identical style across generations. May need seed locking or LoRA fine-tuning.
4. **Memory pressure** -- while generating, the Mac Mini has limited RAM for other tasks.
