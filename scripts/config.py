"""
Shared Configuration Module
Handles environment variables, API keys, and mode selection (demo/dev/prod).
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ─── Run Mode ──────────────────────────────────────────
# demo  = Mock responses, no API calls (free)
# dev   = Real API calls, local execution
# prod  = Full cloud deployment
MODE = os.getenv("RUN_MODE", "demo")

# ─── Azure Configuration ───────────────────────────────
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY", "")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4")
AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT", "")
AZURE_SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY", "")

# ─── AWS Configuration ────────────────────────────────
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-v2")
STABILITY_MODEL_ID = os.getenv("STABILITY_MODEL_ID", "stability.stable-diffusion-xl-v1")

# ─── GCP Configuration ────────────────────────────────
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "")
GCP_LOCATION = os.getenv("GCP_LOCATION", "us-central1")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")

# ─── General ───────────────────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


def is_demo():
    return MODE == "demo"


def is_dev():
    return MODE == "dev"


def get_config_summary():
    """Print a summary of current config (safe, no secrets)."""
    return {
        "mode": MODE,
        "azure_configured": bool(AZURE_OPENAI_ENDPOINT),
        "aws_configured": bool(AWS_ACCESS_KEY),
        "gcp_configured": bool(GCP_PROJECT_ID),
        "openai_configured": bool(OPENAI_API_KEY),
    }
