#!/usr/bin/env python3
"""
Batch generate hero images for all facil.guide guides using Together.ai FLUX.1-schnell.
Cost: ~$0.003/image. Style: flat vector, minimal, coral+teal accents, white bg, no text.
"""

import os
import sys
import json
import time
import base64
import requests
import yaml

API_KEY = "tgp_v1_5WhRgQuzSKjMPO5maoJ2CfLytOygEbi2-Zu5IELS8oI"
API_URL = "https://api.together.xyz/v1/images/generations"
GUIDES_DIR = os.path.join(os.path.dirname(__file__), "..", "src", "content", "guides", "en")
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "src", "assets", "guides")

STYLE_PREFIX = (
    "Flat vector illustration, minimal design, soft coral (#F4845F) and teal (#2EC4B6) accents, "
    "clean white background, simple shapes, no text, no words, no letters, no UI elements, "
    "friendly and warm, designed for seniors, 1200x632 aspect ratio, centered composition. "
)

def get_guide_meta(md_path):
    """Extract frontmatter from markdown file."""
    with open(md_path, "r") as f:
        content = f.read()
    if not content.startswith("---"):
        return None
    end = content.index("---", 3)
    return yaml.safe_load(content[3:end])

def slug_to_prompt(slug, meta):
    """Generate a descriptive prompt from the guide slug and metadata."""
    title = meta.get("title", slug.replace("-", " "))
    # Map common topics to visual descriptions
    prompts = {
        "scan-qr-code": "a smartphone scanning a QR code, phone held in hand pointing at square pattern",
        "send-photo-whatsapp": "a smartphone showing a photo being sent, chat bubble with image",
        "send-photo-email": "a laptop and phone with photo attachment flying between them",
        "video-call-whatsapp": "two smartphones facing each other with video call faces on screens",
        "video-call-iphone": "a smartphone showing a video call with a friendly face on screen",
        "make-phone-call-iphone": "a smartphone with phone dial pad and call button",
        "make-phone-call-android": "a smartphone with phone dial pad and green call button",
        "send-text-message-iphone": "a smartphone with chat bubbles, one being typed",
        "send-voice-message-whatsapp": "a smartphone with microphone icon and sound wave",
        "take-screenshot-iphone": "an iPhone with screen capture animation, sparkle effect",
        "take-screenshot-android": "an Android phone with screen capture animation",
        "set-alarm-iphone": "a smartphone next to an alarm clock showing morning time",
        "connect-wifi-iphone": "a smartphone with wifi signal waves emanating from a router",
        "connect-wifi-android": "a smartphone connecting to a wifi router with signal waves",
        "connect-bluetooth-speaker": "a smartphone and wireless speaker with bluetooth waves",
        "connect-hotel-wifi": "a smartphone in a hotel room connecting to wifi, hotel key card nearby",
        "change-wifi-password": "a router with a lock icon and password field",
        "update-iphone": "a smartphone with download arrow and progress circle",
        "update-android": "a smartphone with system update progress bar",
        "update-phone-software": "a smartphone with circular update arrows",
        "install-app-android": "a smartphone with app store and download button",
        "delete-apps-iphone": "a smartphone with app icons, one being removed with X",
        "create-google-account": "a laptop screen showing account creation form with Google logo shape",
        "create-strong-password": "a shield with a lock and password dots",
        "forgot-password-recovery": "a key next to a lock with question mark",
        "forgot-password-what-to-do": "a padlock with a question mark and reset arrow",
        "increase-text-size-iphone": "a smartphone with small letter A becoming large letter A",
        "increase-text-size-android": "a smartphone with text size slider getting bigger",
        "enable-dark-mode-iphone": "a smartphone half light half dark, sun and moon",
        "use-google-maps": "a smartphone showing a colorful map with location pin",
        "use-google-maps-navigate": "a smartphone with navigation arrow on a road map",
        "use-voice-assistant-siri": "a smartphone with sound waves and microphone icon",
        "use-whatsapp-web": "a laptop and smartphone connected with QR code between them",
        "use-computer-keyboard": "a keyboard with highlighted keys and finger pointing",
        "use-computer-mouse": "a computer mouse with click indicators and cursor arrow",
        "use-orange-money": "a smartphone with mobile payment screen and coins",
        "organize-files-computer": "a laptop with file folders being sorted neatly",
        "send-email-gmail": "a laptop with email compose window and send arrow",
        "share-location-whatsapp": "a smartphone with map pin and chat bubble showing location",
        "share-location-family": "two smartphones sharing a map location pin between them",
        "setup-face-id": "a smartphone scanning a friendly face outline",
        "setup-emergency-contacts": "a smartphone with emergency SOS button and contact list",
        "set-up-email-iphone": "a smartphone with email envelope being configured",
        "save-photo-from-whatsapp": "a smartphone with photo being saved with download arrow",
        "copy-paste-text-phone": "a smartphone with text selection highlight and clipboard",
        "add-contact-iphone": "a smartphone with contact card and plus button",
        "block-number-iphone": "a smartphone with blocked call icon, red circle with line",
        "block-unknown-callers": "a smartphone blocking incoming call with shield",
        "turn-off-notifications-iphone": "a smartphone with notification bell being silenced",
        "phone-battery-dies-fast": "a smartphone with low battery icon and lightning bolt",
        "phone-frozen-fix": "a smartphone with frozen screen and restart arrow",
        "phone-screen-frozen": "a smartphone with frozen cracked ice effect on screen",
        "phone-running-slow": "a smartphone with slow loading spinner and turtle",
        "phone-storage-full": "a smartphone with full storage bar and warning",
        "phone-storage-full-fix": "a smartphone with storage being cleaned, broom sweeping",
        "phone-wont-connect-wifi": "a smartphone with broken wifi signal and warning triangle",
        "cant-hear-phone-call": "a smartphone with ear and muted speaker icon",
        "whatsapp-messages-not-sending": "a smartphone with stuck message and single check mark",
        "accidentally-deleted-photo": "a photo being recovered from a trash bin with undo arrow",
        "check-storage-space-android": "a smartphone showing storage usage pie chart",
        "clear-storage-iphone": "a smartphone with broom cleaning storage space",
        "is-this-message-scam": "a smartphone with suspicious message and warning magnifying glass",
        "recognize-email-scam": "a laptop with phishing email and red warning flag",
        "what-is-chatgpt": "a laptop with chat interface and friendly robot assistant",
        "zoom-video-call": "a laptop showing video call grid with multiple participants",
        "backup-phone": "a smartphone with cloud upload arrow and shield",
    }

    scene = prompts.get(slug, f"illustration about: {title}")
    return STYLE_PREFIX + scene


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
                    "width": 1200,
                    "height": 640,
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
            print(f"  Attempt {attempt+1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(2)
    return False


def main():
    # Get all EN guide slugs
    if not os.path.isdir(GUIDES_DIR):
        print(f"Guides dir not found: {GUIDES_DIR}")
        sys.exit(1)

    slugs = []
    for f in sorted(os.listdir(GUIDES_DIR)):
        if f.endswith(".md"):
            slug = f.replace(".md", "")
            hero_path = os.path.join(ASSETS_DIR, slug, "hero.png")
            if not os.path.exists(hero_path):
                slugs.append(slug)

    print(f"Need to generate {len(slugs)} hero images (~${len(slugs) * 0.003:.2f})")
    print()

    success = 0
    failed = []
    for i, slug in enumerate(slugs):
        md_path = os.path.join(GUIDES_DIR, f"{slug}.md")
        meta = get_guide_meta(md_path)
        if not meta:
            print(f"[{i+1}/{len(slugs)}] SKIP {slug} (no frontmatter)")
            continue

        prompt = slug_to_prompt(slug, meta)
        output = os.path.join(ASSETS_DIR, slug, "hero.png")
        print(f"[{i+1}/{len(slugs)}] {slug}...")

        if generate_image(prompt, output):
            size_kb = os.path.getsize(output) / 1024
            print(f"  OK ({size_kb:.0f}KB)")
            success += 1
        else:
            print(f"  FAILED")
            failed.append(slug)

        # Small delay to avoid rate limiting
        time.sleep(0.5)

    print(f"\nDone: {success} generated, {len(failed)} failed")
    if failed:
        print(f"Failed: {', '.join(failed)}")


if __name__ == "__main__":
    main()
