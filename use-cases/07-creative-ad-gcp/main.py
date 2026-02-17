"""
Use Case 07: Creative Ad Design Tool
Cloud: GCP | Category: Image Synthesis | Model: Imagen 2

Core Logic:
  - Ad-optimized prompt engineering
  - Multiple format support (social, display, print)
  - Brand consistency templates
"""

import sys
import os
import json
import argparse
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from scripts.config import (
    MODE, GCP_PROJECT_ID, GCP_LOCATION, is_demo,
)
from scripts.mock_data import IMAGE_GENERATION_RESPONSE, simulate_latency

# ─── Ad Format Specs ──────────────────────────────────────

AD_FORMATS = {
    "instagram_post": {"width": 1080, "height": 1080, "label": "Instagram Post (1:1)"},
    "instagram_story": {"width": 1080, "height": 1920, "label": "Instagram Story (9:16)"},
    "facebook_ad": {"width": 1200, "height": 628, "label": "Facebook Ad (1.91:1)"},
    "google_display": {"width": 300, "height": 250, "label": "Google Display (300x250)"},
    "billboard": {"width": 1920, "height": 1080, "label": "Billboard (16:9)"},
}

# ─── Prompt Templates ─────────────────────────────────────

AD_STYLES = {
    "modern": "clean modern design, geometric shapes, bold typography, gradient colors",
    "luxury": "premium luxury aesthetic, gold accents, dark background, elegant serif font",
    "playful": "vibrant fun design, bright colors, cartoon elements, rounded shapes",
    "corporate": "professional business style, blue tones, clean layout, sans-serif typography",
    "minimalist": "minimalist design, white space, single focal point, muted colors",
}


def build_ad_prompt(product, headline, style="modern", mood=None):
    """Build optimized prompt for ad creative generation."""
    style_desc = AD_STYLES.get(style, AD_STYLES["modern"])
    prompt = (
        f"Professional advertisement design for '{product}'. "
        f"Headline text: '{headline}'. "
        f"Style: {style_desc}. "
        f"High quality, commercial photography, advertising layout."
    )
    if mood:
        prompt += f" Mood: {mood}."
    return prompt


# ─── Core Logic ────────────────────────────────────────────

def generate_ad_demo(product, headline, style="modern", ad_format="instagram_post"):
    """Demo mode ad generation."""
    simulate_latency(1.0, 3.0)
    fmt = AD_FORMATS.get(ad_format, AD_FORMATS["instagram_post"])
    prompt = build_ad_prompt(product, headline, style)

    return {
        "status": "success",
        "ad_id": f"ad_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "format": fmt["label"],
        "dimensions": f"{fmt['width']}x{fmt['height']}",
        "prompt_used": prompt,
        "style": style,
        "message": f"Demo mode: Ad creative would be generated for '{product}'",
        "mode": "demo",
    }


def generate_ad_vertex(product, headline, style="modern", ad_format="instagram_post"):
    """Generate ad using Vertex AI Imagen."""
    try:
        import vertexai
        from vertexai.vision_models import ImageGenerationModel

        vertexai.init(project=GCP_PROJECT_ID, location=GCP_LOCATION)
        model = ImageGenerationModel.from_pretrained("imagen-2")

        prompt = build_ad_prompt(product, headline, style)
        fmt = AD_FORMATS.get(ad_format, AD_FORMATS["instagram_post"])

        images = model.generate_images(
            prompt=prompt,
            number_of_images=1,
        )

        output_path = f"ad_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        images[0].save(location=output_path)

        return {
            "status": "success",
            "output_path": output_path,
            "format": fmt["label"],
            "prompt_used": prompt,
            "mode": "vertex_ai",
        }
    except ImportError:
        print("Error: Install google-cloud-aiplatform")
        return None
    except Exception as e:
        print(f"Vertex AI Error: {e}")
        return None


def generate(product, headline, style="modern", ad_format="instagram_post"):
    """Main entry point."""
    print(f"[Mode: {MODE}] Creating ad for '{product}' ({ad_format})...")

    if is_demo():
        return generate_ad_demo(product, headline, style, ad_format)
    elif GCP_PROJECT_ID:
        return generate_ad_vertex(product, headline, style, ad_format)
    else:
        return generate_ad_demo(product, headline, style, ad_format)


# ─── CLI ───────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Creative Ad Design Tool")
    parser.add_argument("--product", default="Premium Coffee Blend")
    parser.add_argument("--headline", default="Awaken Your Senses")
    parser.add_argument("--style", choices=list(AD_STYLES.keys()), default="modern")
    parser.add_argument("--format", choices=list(AD_FORMATS.keys()), default="instagram_post")
    args = parser.parse_args()

    result = generate(args.product, args.headline, args.style, args.format)
    if result:
        print("\n" + "=" * 60)
        print("  🎨 Creative Ad Design Result")
        print("=" * 60)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
