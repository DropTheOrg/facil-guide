#!/usr/bin/env python3
"""
Facil.guide image generator using FLUX.1-schnell on Apple Silicon (MPS).
Generates flat vector-style illustrations for guide steps.

Usage:
    python generate_image.py --slug "backup-phone" --prompt "A simple flat illustration of a smartphone showing a cloud backup icon"
    python generate_image.py --slug "backup-phone" --prompt "..." --output /path/to/output.png
    python generate_image.py --test  # Quick test to verify model works
"""

import argparse
import os
import sys
import time
from pathlib import Path

# Facil brand colors for reference in prompts
FACIL_STYLE = (
    "flat vector illustration, minimal clean design, "
    "simplified device mockup, soft pastel colors, "
    "coral and teal accent colors, white background, "
    "no text in image, no watermark, "
    "friendly and approachable style for seniors, "
    "large clear icons, high contrast"
)

def load_pipeline():
    """Load FLUX.1-schnell pipeline with CPU offload for 24GB Mac Mini."""
    import torch
    from diffusers import FluxPipeline

    print("Loading FLUX.1-schnell model with CPU offload...")
    t0 = time.time()

    pipe = FluxPipeline.from_pretrained(
        "black-forest-labs/FLUX.1-schnell",
        torch_dtype=torch.bfloat16,
    )

    # CPU offload: keeps model on CPU, moves each layer to MPS only during forward pass
    # This fits in 24GB unified memory (full model needs ~30GB on MPS)
    pipe.enable_sequential_cpu_offload(device="mps")
    pipe.enable_attention_slicing(slice_size=1)

    print(f"Model loaded in {time.time() - t0:.1f}s")
    return pipe


def generate(pipe, prompt: str, output_path: str, width: int = 768, height: int = 768, steps: int = 4, seed: int = None):
    """Generate a single image."""
    import torch

    full_prompt = f"{prompt}, {FACIL_STYLE}"

    generator = None
    if seed is not None:
        generator = torch.Generator("cpu").manual_seed(seed)

    print(f"Generating image ({width}x{height}, {steps} steps)...")
    t0 = time.time()

    result = pipe(
        prompt=full_prompt,
        width=width,
        height=height,
        num_inference_steps=steps,
        generator=generator,
        guidance_scale=0.0,  # schnell doesn't use guidance
    )

    image = result.images[0]
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    image.save(output_path)

    elapsed = time.time() - t0
    print(f"Saved to {output_path} ({elapsed:.1f}s)")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Generate Facil.guide illustrations")
    parser.add_argument("--slug", help="Guide slug (used for output path)")
    parser.add_argument("--prompt", help="Image prompt (style is auto-appended)")
    parser.add_argument("--output", help="Output file path (overrides slug-based path)")
    parser.add_argument("--width", type=int, default=768)
    parser.add_argument("--height", type=int, default=768)
    parser.add_argument("--steps", type=int, default=4)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--test", action="store_true", help="Quick test generation")

    args = parser.parse_args()

    if args.test:
        args.prompt = "A smartphone screen showing a simple backup progress bar with a cloud icon"
        args.slug = "test"

    if not args.prompt:
        print("Error: --prompt required (or use --test)")
        sys.exit(1)

    # Determine output path
    if args.output:
        output_path = args.output
    elif args.slug:
        base = Path(__file__).parent.parent / "src" / "assets" / "guides" / args.slug
        base.mkdir(parents=True, exist_ok=True)
        output_path = str(base / "hero.png")
    else:
        output_path = "output.png"

    pipe = load_pipeline()
    generate(pipe, args.prompt, output_path, args.width, args.height, args.steps, args.seed)


if __name__ == "__main__":
    main()
