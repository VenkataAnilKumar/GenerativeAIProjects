"""
Use Case 02: Product Image Generation for E-Commerce
Cloud: AWS | Category: Image Synthesis | Model: Stability AI (SDXL)

Core Logic:
  - Text-to-image via Amazon Bedrock
  - Prompt optimization for product photography
  - Image saving and format handling
"""

import sys
import os
import json
import base64
import argparse
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from scripts.config import (
    MODE, AWS_REGION, STABILITY_MODEL_ID, is_demo,
)
from scripts.mock_data import IMAGE_GENERATION_RESPONSE, simulate_latency

# ─── Prompt Engineering ────────────────────────────────────

STYLE_PRESETS = {
    "product": "professional product photography, white background, studio lighting, 8k, sharp focus",
    "lifestyle": "lifestyle photography, natural lighting, warm tones, bokeh background",
    "minimalist": "minimalist design, clean background, soft shadows, elegant composition",
    "luxury": "luxury product shot, dark background, dramatic lighting, premium feel",
}

NEGATIVE_PROMPT = (
    "blurry, low quality, distorted, deformed, ugly, bad anatomy, "
    "watermark, text, logo, signature, cropped"
)


def build_image_prompt(description, style="product", extras=None):
    """Enhance a basic description into an optimized image generation prompt."""
    style_suffix = STYLE_PRESETS.get(style, STYLE_PRESETS["product"])
    prompt = f"{description}, {style_suffix}"
    if extras:
        prompt += f", {extras}"
    return prompt


# ─── Core Logic ────────────────────────────────────────────

def generate_image_demo(description, style="product"):
    """Mock image generation for demo mode."""
    simulate_latency(1.0, 3.0)
    prompt = build_image_prompt(description, style)
    response = IMAGE_GENERATION_RESPONSE.copy()
    response["image_id"] = f"img_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    response["message"] = f"Demo mode: Image would be generated from → '{prompt}'"
    response["prompt_used"] = prompt
    response["negative_prompt"] = NEGATIVE_PROMPT
    return response


def generate_image_bedrock(description, style="product", output_path=None):
    """Generate image using Amazon Bedrock (Stability AI)."""
    try:
        import boto3

        bedrock = boto3.client(
            service_name="bedrock-runtime",
            region_name=AWS_REGION,
        )

        prompt = build_image_prompt(description, style)
        body = json.dumps({
            "text_prompts": [
                {"text": prompt, "weight": 1.0},
                {"text": NEGATIVE_PROMPT, "weight": -1.0},
            ],
            "cfg_scale": 10,
            "seed": 42,
            "steps": 50,
            "width": 1024,
            "height": 1024,
        })

        response = bedrock.invoke_model(
            body=body,
            modelId=STABILITY_MODEL_ID,
            accept="application/json",
            contentType="application/json",
        )

        result = json.loads(response["body"].read())
        image_data = result["artifacts"][0]["base64"]

        # Save image
        if output_path is None:
            output_path = f"output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

        with open(output_path, "wb") as f:
            f.write(base64.b64decode(image_data))

        return {
            "status": "success",
            "output_path": output_path,
            "prompt_used": prompt,
            "model": STABILITY_MODEL_ID,
            "mode": "bedrock",
        }
    except ImportError:
        print("Error: Install boto3 → pip install boto3")
        return None
    except Exception as e:
        print(f"Bedrock API Error: {e}")
        return None


def generate(description, style="product", output_path=None):
    """Main entry point."""
    print(f"[Mode: {MODE}] Generating image for: '{description}'")
    print(f"[Style: {style}]")

    if is_demo():
        return generate_image_demo(description, style)
    else:
        return generate_image_bedrock(description, style, output_path)


# ─── CLI ───────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="AI Product Image Generator")
    parser.add_argument("--description", default="A sleek wireless bluetooth headphone in matte black")
    parser.add_argument("--style", choices=list(STYLE_PRESETS.keys()), default="product")
    parser.add_argument("--output", default=None, help="Output file path")
    args = parser.parse_args()

    result = generate(args.description, args.style, args.output)
    if result:
        print("\n" + "=" * 60)
        print("  Product Image Generation Result")
        print("=" * 60)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
