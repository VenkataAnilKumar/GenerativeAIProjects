"""
Mock Data & Demo Responses
Used in demo mode to simulate AI outputs without API calls.
"""

import random
import time

# ─── 01: Marketing Content ─────────────────────────────
MARKETING_RESPONSES = {
    "email": {
        "subject": "🚀 Introducing {product} — Transform Your Workflow Today!",
        "body": (
            "Hi {name},\n\n"
            "We're thrilled to introduce {product}, designed to help you achieve more with less effort.\n\n"
            "✅ Boost productivity by 40%%\n"
            "✅ Save 10+ hours per week\n"
            "✅ Seamlessly integrates with your tools\n\n"
            "For a limited time, get 20%% off with code LAUNCH20.\n\n"
            "Best regards,\nThe Marketing Team"
        ),
    },
    "social_post": (
        "🔥 Big news! {product} is here to revolutionize the way you work.\n\n"
        "💡 Smarter. Faster. Better.\n\n"
        "Try it free for 14 days → [link]\n\n"
        "#Innovation #ProductLaunch #AI"
    ),
    "ad_copy": (
        "Tired of {pain_point}? {product} solves it in seconds.\n"
        "Join 10,000+ professionals who switched. Start free today."
    ),
}

# ─── 02: Product Images ────────────────────────────────
IMAGE_GENERATION_RESPONSE = {
    "status": "success",
    "image_id": "img_{id}",
    "format": "png",
    "resolution": "1024x1024",
    "model": "stable-diffusion-xl",
    "seed": 42,
    "message": "Demo mode: Image would be generated from prompt: '{prompt}'",
}

# ─── 03: Code Completion ───────────────────────────────
CODE_COMPLETIONS = {
    "python": {
        "def ": (
            "    \"\"\"\n"
            "    Auto-generated function implementation.\n"
            "    \"\"\"\n"
            "    # TODO: Implement logic here\n"
            "    pass\n"
        ),
        "class ": (
            "    \"\"\"\n"
            "    Auto-generated class with common patterns.\n"
            "    \"\"\"\n\n"
            "    def __init__(self):\n"
            "        pass\n\n"
            "    def __repr__(self):\n"
            "        return f\"{self.__class__.__name__}()\"\n"
        ),
    },
}

# ─── 04: Knowledge Base Q&A ────────────────────────────
KNOWLEDGE_BASE = [
    {
        "id": "KB001",
        "topic": "returns",
        "content": "Our return policy allows returns within 30 days of purchase. Items must be in original condition. Refunds are processed within 5-7 business days.",
    },
    {
        "id": "KB002",
        "topic": "shipping",
        "content": "Standard shipping takes 5-7 business days. Express shipping is 2-3 business days. International orders may take 10-15 business days.",
    },
    {
        "id": "KB003",
        "topic": "warranty",
        "content": "All products come with a 1-year limited warranty. Extended warranty for 2 additional years is available for $29.99.",
    },
    {
        "id": "KB004",
        "topic": "pricing",
        "content": "We offer tiered pricing: Basic ($9.99/mo), Pro ($29.99/mo), Enterprise (custom). Annual billing saves 20%.",
    },
    {
        "id": "KB005",
        "topic": "technical_support",
        "content": "Technical support available 24/7 via chat and email. Phone support available Mon-Fri 9 AM - 6 PM EST.",
    },
]

# ─── 05: Healthcare Summarization ──────────────────────
MEDICAL_REPORTS = [
    {
        "id": "RPT001",
        "type": "radiology",
        "report": (
            "Chest X-ray PA and lateral views obtained. The heart size is normal. "
            "The lungs are clear bilaterally. No pleural effusion or pneumothorax. "
            "The mediastinum is unremarkable. Bony structures are intact."
        ),
        "summary": (
            "IMPRESSION: Normal chest radiograph. No acute cardiopulmonary findings. "
            "Heart size within normal limits. Lungs clear."
        ),
    },
    {
        "id": "RPT002",
        "type": "pathology",
        "report": (
            "Specimen: Right breast, needle core biopsy. Microscopic examination reveals "
            "fibrocystic changes with apocrine metaplasia. No evidence of malignancy. "
            "Stromal fibrosis is present."
        ),
        "summary": (
            "IMPRESSION: Benign fibrocystic changes with apocrine metaplasia. "
            "No malignancy identified. Recommend routine follow-up."
        ),
    },
]

# ─── 06: Learning Content ──────────────────────────────
LEARNING_CONTENT = {
    "algebra": {
        "beginner": {
            "title": "Introduction to Algebra",
            "objectives": [
                "Understand variables and expressions",
                "Solve simple one-step equations",
                "Identify algebraic patterns",
            ],
            "content": (
                "Algebra is a branch of math that uses letters (variables) to represent numbers.\n\n"
                "Example: If x + 3 = 7, then x = 4\n\n"
                "Practice: Solve for x → x + 5 = 12"
            ),
            "exercises": [
                {"question": "Solve: x + 3 = 10", "answer": "x = 7"},
                {"question": "Solve: 2x = 8", "answer": "x = 4"},
            ],
        },
        "advanced": {
            "title": "Quadratic Equations",
            "objectives": [
                "Factor quadratic expressions",
                "Use the quadratic formula",
                "Graph parabolas",
            ],
            "content": (
                "A quadratic equation has the form ax² + bx + c = 0.\n\n"
                "The quadratic formula: x = (-b ± √(b²-4ac)) / 2a\n\n"
                "Example: x² - 5x + 6 = 0 → x = 2 or x = 3"
            ),
            "exercises": [
                {"question": "Solve: x² - 4 = 0", "answer": "x = ±2"},
                {"question": "Factor: x² + 5x + 6", "answer": "(x+2)(x+3)"},
            ],
        },
    },
}

# ─── 08: Code Review ───────────────────────────────────
CODE_REVIEW_RULES = [
    {"rule": "missing_docstring", "severity": "warning", "message": "Function is missing a docstring."},
    {"rule": "no_error_handling", "severity": "error", "message": "No try/except block for potential exceptions."},
    {"rule": "magic_numbers", "severity": "info", "message": "Consider using named constants instead of magic numbers."},
    {"rule": "unused_imports", "severity": "warning", "message": "Imported modules may not be used."},
    {"rule": "long_function", "severity": "warning", "message": "Function exceeds 50 lines. Consider refactoring."},
]

# ─── 09: Legal Documents ───────────────────────────────
LEGAL_CLAUSES = [
    {
        "id": "CL001",
        "type": "termination",
        "text": "Either party may terminate this agreement with 30 days written notice. Upon termination, all confidential materials must be returned within 10 business days.",
    },
    {
        "id": "CL002",
        "type": "liability",
        "text": "The total liability under this Agreement shall not exceed the total fees paid in the 12 months preceding the claim. Neither party shall be liable for indirect or consequential damages.",
    },
    {
        "id": "CL003",
        "type": "confidentiality",
        "text": "All information shared between parties shall remain confidential for 3 years following termination. Exceptions include information that becomes public through no fault of the receiving party.",
    },
    {
        "id": "CL004",
        "type": "intellectual_property",
        "text": "All IP created during this engagement belongs to the Client. The Service Provider retains rights to pre-existing tools and methodologies.",
    },
]

# ─── 10: Manufacturing Data ────────────────────────────
MANUFACTURING_DATA = {
    "production_lines": [
        {"line": "A", "capacity": 1000, "utilization": 0.85, "defect_rate": 0.02},
        {"line": "B", "capacity": 800, "utilization": 0.72, "defect_rate": 0.03},
        {"line": "C", "capacity": 1200, "utilization": 0.90, "defect_rate": 0.015},
    ],
    "suppliers": [
        {"name": "Supplier X", "lead_time_days": 7, "reliability": 0.95},
        {"name": "Supplier Y", "lead_time_days": 14, "reliability": 0.88},
    ],
    "cost_per_unit": 12.50,
    "daily_output": 2800,
}


def simulate_latency(min_s=0.5, max_s=2.0):
    """Simulate API latency for demo realism."""
    time.sleep(random.uniform(min_s, max_s))
