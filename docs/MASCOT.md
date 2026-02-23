# Facil.guide Mascot

## Status: APPROVED 2026-02-20

## Character: "Pix"
- Coral/peach colored friendly ghost
- Two thin antennae with round bobbles on top
- Round dark glasses (signature feature)
- Big expressive dark eyes behind glasses
- Rosy blush cheeks
- Small warm smile
- Small flipper arms
- Wavy ghost bottom edge
- Floating with subtle shadow

## Reference Image
`docs/images/mascot-reference.png` (ghost-antenna-2)

## Consistency Method
- **FLUX.1 Kontext dev** via Together.ai API
- Feed `mascot-reference.png` as image_url + scene prompt
- $0.025/image, keeps character identical across scenes
- Tested: 3 scenes (holding phone, showing screen, pointing at gear) -- all consistent

## Visual Identity
- **Color:** Coral/Peach (#FFB5A0 range)
- **Glasses:** Dark round frames
- **Antennae:** Two thin lines with coral bobbles
- **Background:** Always white (transparent for compositing)
- **Style:** Flat vector, thick clean outlines, minimal

## SVG-Ready Shapes
The silhouette is recognizable from:
1. Round dome head
2. Two antennae with bobbles (top)
3. Round glasses (middle)
4. Wavy ghost bottom
~8-10 SVG paths total for a clean vector version

## Usage
- Hero images: mascot in scene related to guide topic
- Step images: mascot pointing at/interacting with UI elements
- Favicon: silhouette version (head + antennae only)
- Watermark: NOT needed -- mascot presence IS the brand
- OG cards: mascot + guide title text overlay

## API Config
- Provider: Together.ai
- Model: black-forest-labs/FLUX.1-kontext-dev (for mascot scenes)
- Model: black-forest-labs/FLUX.1-schnell (for generic illustrations without mascot)
- Cost: $0.025/mascot image, $0.003/generic image

## Test Images
| File | Scene |
|------|-------|
| mascot-reference.png | Base character (front-facing, neutral) |
| mascot-scene-1.png | Holding smartphone |
| mascot-scene-2.png | Showing phone screen |
| mascot-scene-3.png | Pointing at settings gear |
