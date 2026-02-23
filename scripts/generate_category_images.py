#!/usr/bin/env python3
"""
Generate category images for facil.guide using Together.ai FLUX.1-schnell.
Brand style: flat vector, coral (#F4845F) + teal (#2EC4B6) accents, white bg.
Each image depicts a warm scene related to the category.
"""

import os
import sys
import time
import base64
import requests

API_KEY = "tgp_v1_5WhRgQuzSKjMPO5maoJ2CfLytOygEbi2-Zu5IELS8oI"
API_URL = "https://api.together.xyz/v1/images/generations"
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "src", "assets", "categories")

STYLE = (
    "Flat vector illustration, minimal clean design, soft coral (#F4845F) and teal (#2EC4B6) color accents, "
    "clean white background, simple rounded shapes, warm and friendly mood, designed for seniors, "
    "no text, no words, no letters, no UI chrome. "
)

# Each category gets a scene description with people or objects
CATEGORIES = {
    "smartphone": {
        "prompt": STYLE + (
            "A grandmother with silver curly hair and lavender cardigan sitting in a cozy armchair, "
            "holding a large smartphone with both hands, looking at it with a warm smile. "
            "A small coral ghost mascot peeks from behind the phone screen. "
            "Soft light, peaceful living room setting."
        ),
        "alt_en": "A grandmother learning to use her smartphone",
        "alt_fr": "Une grand-mere apprenant a utiliser son smartphone",
    },
    "ordinateur": {
        "prompt": STYLE + (
            "A grandfather with white hair, reading glasses, and green sweater sitting at a clean desk, "
            "using a laptop computer. The laptop lid has a small coral ghost logo sticker. "
            "A cup of coffee nearby. Calm study environment, natural light from a window."
        ),
        "alt_en": "A grandfather using his laptop computer",
        "alt_fr": "Un grand-pere utilisant son ordinateur portable",
    },
    "internet": {
        "prompt": STYLE + (
            "A wifi router with signal waves radiating outward in coral and teal colors, "
            "surrounded by connected devices -- a phone, a tablet, a laptop -- floating gently. "
            "A small coral ghost mascot rides one of the wifi waves. "
            "Clean, minimal, centered composition on white background."
        ),
        "alt_en": "Devices connected to the internet via wifi",
        "alt_fr": "Appareils connectes a internet par wifi",
    },
    "applications": {
        "prompt": STYLE + (
            "A large smartphone screen showing a grid of colorful app icons in coral, teal, and soft purple. "
            "A hand with a finger tapping one of the app icons. The phone has a coral ghost sticker on the back. "
            "Clean white background, playful but organized layout."
        ),
        "alt_en": "A phone screen with app icons ready to use",
        "alt_fr": "Un ecran de telephone avec des icones d'applications",
    },
    "securite": {
        "prompt": STYLE + (
            "A large shield in teal color with a padlock in the center, surrounded by floating keys and password dots. "
            "A small coral ghost mascot stands on top of the shield looking protective. "
            "Subtle binary code pattern in the background, very faint. "
            "Clean composition, reassuring and safe feeling."
        ),
        "alt_en": "A protective shield symbolizing digital security",
        "alt_fr": "Un bouclier protecteur symbolisant la securite numerique",
    },
    "communication": {
        "prompt": STYLE + (
            "Two smartphones facing each other with colorful chat bubbles floating between them -- "
            "coral, teal, and white bubbles with simple shapes instead of text. "
            "A video call icon and phone icon float above. "
            "Warm, social, connected feeling. Clean white background."
        ),
        "alt_en": "Two phones exchanging messages and calls",
        "alt_fr": "Deux telephones echangeant messages et appels",
    },
    "ia": {
        "prompt": STYLE + (
            "A friendly robot assistant made of simple rounded shapes in teal, "
            "with a coral glow around its head suggesting intelligence. "
            "It holds out a helpful hand toward a person's hand reaching from the side. "
            "Warm interaction, not scary, collaborative feeling. White background."
        ),
        "alt_en": "A friendly AI assistant offering help",
        "alt_fr": "Un assistant IA amical offrant son aide",
    },
    "government": {
        "prompt": STYLE + (
            "A smartphone showing a government building icon on screen, "
            "with an ID card and official stamp floating beside it. "
            "Colors: institutional blue mixed with coral accents. "
            "A coral ghost mascot holds a small document. "
            "Professional but approachable feeling, white background."
        ),
        "alt_en": "Digital government services on your phone",
        "alt_fr": "Services publics numeriques sur votre telephone",
    },
    "money": {
        "prompt": STYLE + (
            "A smartphone with a payment screen showing a checkmark, "
            "surrounded by floating coins and a credit card in coral and teal colors. "
            "A small coral ghost mascot gives a thumbs up next to the phone. "
            "Safe, trustworthy feeling. Clean white background."
        ),
        "alt_en": "Mobile payments and digital money",
        "alt_fr": "Paiements mobiles et argent numerique",
    },
    "troubleshooting": {
        "prompt": STYLE + (
            "A smartphone with a small wrench and screwdriver crossed behind it, "
            "with a glowing light bulb above suggesting a solution. "
            "A coral ghost mascot wearing tiny round glasses peers at the phone with curiosity. "
            "Problem-solving mood, hopeful. Clean white background."
        ),
        "alt_en": "Fixing and troubleshooting phone problems",
        "alt_fr": "Resoudre les problemes de telephone",
    },
}


def generate_image(prompt, output_path, retries=3):
    """Generate image via Together.ai API."""
    for attempt in range(retries):
        try:
            resp = requests.post(
                API_URL,
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "black-forest-labs/FLUX.1-schnell",
                    "prompt": prompt,
                    "width": 512,
                    "height": 512,
                    "steps": 4,
                    "n": 1,
                    "response_format": "b64_json",
                },
                timeout=60,
            )
            resp.raise_for_status()
            data = resp.json()
            img_b64 = data["data"][0]["b64_json"]
            img_bytes = base64.b64decode(img_b64)

            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(img_bytes)
            return True
        except Exception as e:
            print(f"  Attempt {attempt+1} failed: {e}", flush=True)
            if attempt < retries - 1:
                time.sleep(2)
    return False


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    
    total = len(CATEGORIES)
    success = 0
    failed = []
    
    for i, (cat, info) in enumerate(sorted(CATEGORIES.items())):
        output = os.path.join(OUT_DIR, f"{cat}.png")
        if os.path.exists(output):
            print(f"[{i+1}/{total}] {cat} -- SKIP (exists)", flush=True)
            success += 1
            continue
            
        print(f"[{i+1}/{total}] {cat}...", flush=True)
        if generate_image(info["prompt"], output):
            size_kb = os.path.getsize(output) / 1024
            print(f"  OK ({size_kb:.0f}KB)", flush=True)
            success += 1
        else:
            print(f"  FAILED", flush=True)
            failed.append(cat)
        time.sleep(0.5)

    print(f"\nDone: {success}/{total} generated, {len(failed)} failed", flush=True)
    if failed:
        print(f"Failed: {', '.join(failed)}", flush=True)


if __name__ == "__main__":
    main()
