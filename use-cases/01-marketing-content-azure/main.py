"""
Use Case 01: AI-Powered Content Creation for Marketing
Cloud: Azure | Category: Text Generation | Model: GPT-4

Core Logic:
  - Prompt template engine with brand voice
  - Multi-channel content generation (email, social, ad copy)
  - Supports demo mode (mock) and dev mode (real Azure OpenAI API)
"""

import sys
import os
import json
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from scripts.config import (
    MODE, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_KEY,
    AZURE_OPENAI_DEPLOYMENT, OPENAI_API_KEY, is_demo,
)
from scripts.mock_data import MARKETING_RESPONSES, simulate_latency

# ─── Prompt Templates ─────────────────────────────────────

TEMPLATES = {
    "email": (
        "You are an expert marketing copywriter. Write a professional marketing email.\n\n"
        "Product: {product}\n"
        "Target Audience: {audience}\n"
        "Tone: {tone}\n"
        "Key Benefits: {benefits}\n\n"
        "Generate a complete email with subject line and body. "
        "Make it compelling with a clear call-to-action."
    ),
    "social_post": (
        "Create an engaging social media post for {platform}.\n\n"
        "Product: {product}\n"
        "Tone: {tone}\n"
        "Max Length: {max_length} characters\n"
        "Include relevant emojis and hashtags."
    ),
    "ad_copy": (
        "Write a short, punchy advertisement copy.\n\n"
        "Product: {product}\n"
        "Pain Point: {pain_point}\n"
        "Unique Selling Point: {usp}\n"
        "Call to Action: {cta}\n\n"
        "Keep it under 100 words."
    ),
}


# ─── Core Logic ────────────────────────────────────────────

def build_prompt(content_type, **kwargs):
    """Build a structured prompt from template and parameters."""
    template = TEMPLATES.get(content_type)
    if not template:
        raise ValueError(f"Unknown content type: {content_type}. Options: {list(TEMPLATES.keys())}")
    return template.format(**kwargs)


def generate_content_demo(content_type, **kwargs):
    """Generate content using mock data (no API calls)."""
    simulate_latency(0.5, 1.5)
    product = kwargs.get("product", "Our Product")

    if content_type == "email":
        mock = MARKETING_RESPONSES["email"]
        return {
            "subject": mock["subject"].format(product=product),
            "body": mock["body"].format(product=product, name=kwargs.get("audience", "Valued Customer")),
            "mode": "demo",
        }
    elif content_type == "social_post":
        return {
            "content": MARKETING_RESPONSES["social_post"].format(product=product),
            "mode": "demo",
        }
    elif content_type == "ad_copy":
        return {
            "content": MARKETING_RESPONSES["ad_copy"].format(
                product=product,
                pain_point=kwargs.get("pain_point", "inefficiency"),
            ),
            "mode": "demo",
        }


def generate_content_azure(content_type, **kwargs):
    """Generate content using Azure OpenAI Service."""
    try:
        from openai import AzureOpenAI

        client = AzureOpenAI(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_key=AZURE_OPENAI_KEY,
            api_version="2024-02-01",
        )
        prompt = build_prompt(content_type, **kwargs)

        response = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            messages=[
                {"role": "system", "content": "You are an expert marketing copywriter."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=500,
            temperature=0.7,
        )
        return {
            "content": response.choices[0].message.content,
            "tokens_used": response.usage.total_tokens,
            "model": AZURE_OPENAI_DEPLOYMENT,
            "mode": "azure",
        }
    except ImportError:
        print("Error: Install openai package → pip install openai")
        return None
    except Exception as e:
        print(f"Azure API Error: {e}")
        return None


def generate_content_openai(content_type, **kwargs):
    """Fallback: Generate content using OpenAI API directly."""
    try:
        from openai import OpenAI

        client = OpenAI(api_key=OPENAI_API_KEY)
        prompt = build_prompt(content_type, **kwargs)

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert marketing copywriter."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=500,
            temperature=0.7,
        )
        return {
            "content": response.choices[0].message.content,
            "tokens_used": response.usage.total_tokens,
            "model": "gpt-3.5-turbo",
            "mode": "openai_fallback",
        }
    except Exception as e:
        print(f"OpenAI API Error: {e}")
        return None


def generate(content_type, **kwargs):
    """Main entry point — routes to correct backend based on mode."""
    print(f"[Mode: {MODE}] Generating {content_type}...")

    if is_demo():
        return generate_content_demo(content_type, **kwargs)
    elif AZURE_OPENAI_KEY:
        return generate_content_azure(content_type, **kwargs)
    elif OPENAI_API_KEY:
        return generate_content_openai(content_type, **kwargs)
    else:
        print("No API keys configured. Running in demo mode.")
        return generate_content_demo(content_type, **kwargs)


# ─── CLI ───────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="AI Marketing Content Generator")
    parser.add_argument("--type", choices=["email", "social_post", "ad_copy"], default="email")
    parser.add_argument("--product", default="AI-Powered Analytics Platform")
    parser.add_argument("--audience", default="Marketing Managers")
    parser.add_argument("--tone", default="professional yet friendly")
    parser.add_argument("--platform", default="LinkedIn")
    args = parser.parse_args()

    params = {
        "product": args.product,
        "audience": args.audience,
        "tone": args.tone,
        "platform": args.platform,
        "benefits": "Real-time insights, automated reporting, 40% time savings",
        "max_length": "280",
        "pain_point": "manual data analysis",
        "usp": "AI-powered insights in seconds",
        "cta": "Start free trial",
    }

    result = generate(args.type, **params)
    if result:
        print("\n" + "=" * 60)
        print(f"  Content Type: {args.type.upper()}")
        print(f"  Mode: {result.get('mode', 'unknown')}")
        print("=" * 60)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
