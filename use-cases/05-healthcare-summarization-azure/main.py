"""
Use Case 05: Healthcare Report Summarization
Cloud: Azure | Category: Text Generation | Model: MedLM / GPT-4

Core Logic:
  - PHI redaction (anonymization)
  - Medical report parsing
  - Domain-specific summarization prompts
  - Output validation
"""

import sys
import os
import json
import re
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from scripts.config import (
    MODE, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_KEY,
    AZURE_OPENAI_DEPLOYMENT, OPENAI_API_KEY, is_demo,
)
from scripts.mock_data import MEDICAL_REPORTS, simulate_latency

# ─── PHI Redaction ─────────────────────────────────────────

PHI_PATTERNS = {
    "SSN": r"\b\d{3}-\d{2}-\d{4}\b",
    "PHONE": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
    "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    "DATE_OF_BIRTH": r"\b\d{1,2}/\d{1,2}/\d{4}\b",
    "MRN": r"\bMRN[:\s]*\d{6,}\b",
    "NAME": r"\b(Dr\.\s+[A-Z][a-z]+\s+[A-Z][a-z]+|Patient:\s+[A-Z][a-z]+\s+[A-Z][a-z]+)\b",
}


def redact_phi(text):
    """Remove Protected Health Information from text."""
    redacted = text
    redactions = []
    for field, pattern in PHI_PATTERNS.items():
        matches = re.findall(pattern, redacted)
        if matches:
            redactions.append({"field": field, "count": len(matches)})
            redacted = re.sub(pattern, f"[REDACTED-{field}]", redacted)
    return redacted, redactions


# ─── Report Parsing ────────────────────────────────────────

def parse_report_sections(report_text):
    """Extract structured sections from a medical report."""
    sections = {
        "findings": "",
        "impression": "",
        "recommendations": "",
        "full_text": report_text,
    }

    text_lower = report_text.lower()
    if "impression:" in text_lower:
        idx = text_lower.index("impression:")
        sections["impression"] = report_text[idx:]
    if "findings:" in text_lower:
        idx = text_lower.index("findings:")
        end = text_lower.find("impression:", idx)
        sections["findings"] = report_text[idx: end if end > 0 else len(report_text)]

    return sections


# ─── Core Logic ────────────────────────────────────────────

SYSTEM_PROMPT = (
    "You are a medical AI assistant specialized in summarizing clinical reports. "
    "Follow these rules:\n"
    "1. Preserve key clinical findings, diagnoses, and recommendations.\n"
    "2. Use standard medical terminology.\n"
    "3. Structure output as: FINDINGS → IMPRESSION → RECOMMENDATIONS.\n"
    "4. Flag any critical or urgent findings first.\n"
    "5. Be concise but complete — no information loss."
)


def summarize_demo(report_text):
    """Demo summarization using mock data."""
    simulate_latency(1.0, 2.0)

    # Try to find a matching mock report
    for mock_report in MEDICAL_REPORTS:
        if mock_report["report"][:50] in report_text:
            return {
                "original_length": len(report_text),
                "summary": mock_report["summary"],
                "summary_length": len(mock_report["summary"]),
                "compression_ratio": f"{len(mock_report['summary']) / len(report_text):.1%}",
                "report_type": mock_report["type"],
                "mode": "demo",
            }

    # Fallback: Simple extractive summary
    sentences = report_text.split(". ")
    summary = ". ".join(sentences[:3]) + "."
    return {
        "original_length": len(report_text),
        "summary": f"SUMMARY: {summary}",
        "summary_length": len(summary),
        "compression_ratio": f"{len(summary) / len(report_text):.1%}",
        "report_type": "unknown",
        "mode": "demo",
    }


def summarize_llm(report_text):
    """Summarize using LLM (Azure OpenAI or OpenAI fallback)."""
    # Step 1: Redact PHI
    safe_text, redactions = redact_phi(report_text)

    # Step 2: Parse sections
    sections = parse_report_sections(safe_text)

    # Step 3: Build prompt
    user_prompt = (
        f"Summarize the following medical report concisely:\n\n"
        f"{safe_text}\n\n"
        f"Provide a structured summary with key findings and impression."
    )

    try:
        from openai import OpenAI, AzureOpenAI

        if AZURE_OPENAI_KEY:
            client = AzureOpenAI(
                azure_endpoint=AZURE_OPENAI_ENDPOINT,
                api_key=AZURE_OPENAI_KEY,
                api_version="2024-02-01",
            )
            model = AZURE_OPENAI_DEPLOYMENT
            mode = "azure"
        else:
            client = OpenAI(api_key=OPENAI_API_KEY)
            model = "gpt-3.5-turbo"
            mode = "openai_fallback"

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=300,
            temperature=0.2,
        )

        summary = response.choices[0].message.content
        return {
            "original_length": len(report_text),
            "summary": summary,
            "summary_length": len(summary),
            "compression_ratio": f"{len(summary) / len(report_text):.1%}",
            "phi_redactions": redactions,
            "tokens_used": response.usage.total_tokens,
            "mode": mode,
        }
    except Exception as e:
        print(f"LLM Error: {e}")
        return None


def summarize(report_text):
    """Main entry point."""
    print(f"[Mode: {MODE}] Summarizing medical report ({len(report_text)} chars)...")

    if is_demo():
        return summarize_demo(report_text)
    elif AZURE_OPENAI_KEY or OPENAI_API_KEY:
        return summarize_llm(report_text)
    else:
        return summarize_demo(report_text)


# ─── CLI ───────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Healthcare Report Summarizer")
    parser.add_argument("--report", default=None, help="Report text or path to file")
    parser.add_argument("--type", choices=["radiology", "pathology", "clinical"], default="radiology")
    args = parser.parse_args()

    if args.report and os.path.isfile(args.report):
        with open(args.report) as f:
            report_text = f.read()
    elif args.report:
        report_text = args.report
    else:
        report_text = MEDICAL_REPORTS[0]["report"]

    result = summarize(report_text)
    if result:
        print("\n" + "=" * 60)
        print("  Healthcare Report Summary")
        print("=" * 60)
        print(f"\nOriginal: {result['original_length']} chars")
        print(f"Summary:  {result['summary_length']} chars")
        print(f"Compression: {result['compression_ratio']}")
        print(f"\n{result['summary']}")
        if result.get("phi_redactions"):
            print(f"\nPHI Redacted: {result['phi_redactions']}")
        print(f"\n[Mode: {result['mode']}]")


if __name__ == "__main__":
    main()
