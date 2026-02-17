"""
Use Case 09: Legal Document Analysis
Cloud: Azure | Category: RAG Pipeline | Model: Azure AI Search + OpenAI

Core Logic:
  - Local vector store for contract clauses
  - Semantic search with TF-IDF
  - Clause extraction and risk scoring
  - Compliance checking
"""

import sys
import os
import json
import re
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from scripts.config import (
    MODE, AZURE_SEARCH_ENDPOINT, AZURE_SEARCH_KEY,
    OPENAI_API_KEY, is_demo,
)
from scripts.mock_data import LEGAL_CLAUSES, simulate_latency

# ─── Local Vector Store ────────────────────────────────────

class LegalVectorStore:
    """Lightweight vector store for legal clause search."""

    def __init__(self):
        self.clauses = []

    def index_clauses(self, clauses):
        """Index legal clauses for search."""
        self.clauses = clauses

    def _tokenize(self, text):
        return set(re.findall(r'\b[a-z]{3,}\b', text.lower()))

    def search(self, query, top_k=3):
        """Search clauses by keyword overlap (TF-IDF approximation)."""
        query_tokens = self._tokenize(query)
        scored = []
        for clause in self.clauses:
            clause_tokens = self._tokenize(clause["text"])
            overlap = len(query_tokens & clause_tokens)
            total = len(query_tokens | clause_tokens)
            score = overlap / total if total > 0 else 0
            scored.append((score, clause))
        scored.sort(reverse=True, key=lambda x: x[0])
        return [{"clause": c, "score": round(s, 4)} for s, c in scored[:top_k]]


# ─── Risk Assessment ──────────────────────────────────────

RISK_KEYWORDS = {
    "high": ["unlimited liability", "indemnify", "sole discretion", "irrevocable",
             "waive all rights", "no liability"],
    "medium": ["termination", "penalty", "breach", "non-compete",
               "exclusive rights", "automatic renewal"],
    "low": ["notice period", "amendment", "governing law", "force majeure"],
}


def assess_risk(clause_text):
    """Score the risk level of a contract clause."""
    text_lower = clause_text.lower()
    risks_found = []

    for level, keywords in RISK_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                risks_found.append({"level": level, "trigger": kw})

    if any(r["level"] == "high" for r in risks_found):
        overall = "HIGH"
    elif any(r["level"] == "medium" for r in risks_found):
        overall = "MEDIUM"
    else:
        overall = "LOW"

    return {"overall_risk": overall, "risk_factors": risks_found}


# ─── Core Logic ────────────────────────────────────────────

def analyze_demo(query, contract_text=None):
    """Demo legal analysis with local vector store."""
    simulate_latency(0.5, 2.0)

    store = LegalVectorStore()
    store.index_clauses(LEGAL_CLAUSES)
    search_results = store.search(query, top_k=2)

    analyses = []
    for result in search_results:
        clause = result["clause"]
        risk = assess_risk(clause["text"])
        analyses.append({
            "clause_id": clause["id"],
            "clause_type": clause["type"],
            "text": clause["text"],
            "relevance": result["score"],
            "risk_assessment": risk,
        })

    return {
        "query": query,
        "results": analyses,
        "total_clauses_searched": len(LEGAL_CLAUSES),
        "mode": "demo",
    }


def analyze_llm(query, contract_text=None):
    """Legal analysis with LLM augmentation."""
    # Step 1: Retrieve relevant clauses
    store = LegalVectorStore()
    store.index_clauses(LEGAL_CLAUSES)
    search_results = store.search(query, top_k=3)
    context = "\n\n".join([r["clause"]["text"] for r in search_results])

    # Step 2: LLM analysis
    try:
        from openai import OpenAI

        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a legal document analyst. Analyze contract clauses "
                        "with focus on risks, obligations, and recommendations. "
                        "Be precise and cite specific language from the clauses."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Question: {query}\n\n"
                        f"Relevant clauses:\n{context}\n\n"
                        f"Provide: 1) Direct answer 2) Risk assessment 3) Recommendations"
                    ),
                },
            ],
            max_tokens=500,
            temperature=0.2,
        )

        analyses = []
        for result in search_results:
            clause = result["clause"]
            risk = assess_risk(clause["text"])
            analyses.append({
                "clause_id": clause["id"],
                "clause_type": clause["type"],
                "risk_assessment": risk,
            })

        return {
            "query": query,
            "ai_analysis": response.choices[0].message.content,
            "clause_details": analyses,
            "tokens_used": response.usage.total_tokens,
            "mode": "openai_rag",
        }
    except Exception as e:
        print(f"LLM Error: {e}")
        return None


def analyze(query, contract_text=None):
    """Main entry point."""
    print(f"[Mode: {MODE}] Analyzing: '{query}'...")

    if is_demo():
        return analyze_demo(query, contract_text)
    elif OPENAI_API_KEY:
        return analyze_llm(query, contract_text)
    else:
        return analyze_demo(query, contract_text)


# ─── CLI ───────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Legal Document Analyzer")
    parser.add_argument("--query", default="What are the termination conditions?")
    parser.add_argument("--contract", default=None, help="Path to contract file")
    args = parser.parse_args()

    result = analyze(args.query)
    if result:
        print("\n" + "=" * 60)
        print("  ⚖️ Legal Document Analysis")
        print("=" * 60)
        print(f"\nQuery: {result['query']}")

        if result.get("ai_analysis"):
            print(f"\nAI Analysis:\n{result['ai_analysis']}")

        if result.get("results"):
            print(f"\nRelevant Clauses:")
            for r in result["results"]:
                risk = r["risk_assessment"]["overall_risk"]
                icon = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(risk, "⚪")
                print(f"\n  {icon} [{r['clause_type'].upper()}] Risk: {risk}")
                print(f"     {r['text'][:120]}...")

        print(f"\n[Mode: {result['mode']}]")


if __name__ == "__main__":
    main()
