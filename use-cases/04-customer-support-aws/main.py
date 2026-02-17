"""
Use Case 04: Customer Support Knowledge Base Q&A
Cloud: AWS | Category: RAG Pipeline | Model: Claude

Core Logic:
  - Local RAG with FAISS vector search (MVP)
  - Embedding-based document retrieval
  - Context-augmented LLM generation
  - Guardrails for content filtering
"""

import sys
import os
import json
import argparse
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from scripts.config import MODE, OPENAI_API_KEY, is_demo
from scripts.mock_data import KNOWLEDGE_BASE, simulate_latency

# ─── Simple Vector Store (Local MVP) ──────────────────────

class SimpleVectorStore:
    """
    Lightweight vector store using TF-IDF for similarity search.
    No external dependencies — works anywhere.
    """

    def __init__(self):
        self.documents = []
        self.doc_vectors = []

    def _tokenize(self, text):
        """Simple tokenization and normalization."""
        return re.findall(r'\b[a-z]+\b', text.lower())

    def _compute_tfidf(self, tokens, vocab):
        """Compute a simple term-frequency vector."""
        vector = {}
        for token in tokens:
            vector[token] = vector.get(token, 0) + 1
        return {k: v / len(tokens) for k, v in vector.items()}

    def add_documents(self, documents):
        """Index a list of documents."""
        self.documents = documents
        for doc in documents:
            tokens = self._tokenize(doc["content"])
            self.doc_vectors.append(self._compute_tfidf(tokens, set(tokens)))

    def search(self, query, top_k=3):
        """Find most relevant documents using cosine-like similarity."""
        query_tokens = self._tokenize(query)
        query_vec = self._compute_tfidf(query_tokens, set(query_tokens))

        scores = []
        for i, doc_vec in enumerate(self.doc_vectors):
            # Dot product similarity
            score = sum(query_vec.get(k, 0) * doc_vec.get(k, 0) for k in set(query_vec) | set(doc_vec))
            scores.append((score, i))

        scores.sort(reverse=True)
        results = []
        for score, idx in scores[:top_k]:
            results.append({
                "document": self.documents[idx],
                "relevance_score": round(score, 4),
            })
        return results


# ─── Guardrails ────────────────────────────────────────────

BLOCKED_TOPICS = ["legal advice", "medical advice", "financial advice", "personal data"]


def apply_guardrails(query, response):
    """Simple guardrails for content filtering."""
    warnings = []
    for topic in BLOCKED_TOPICS:
        if topic in query.lower() or topic in response.lower():
            warnings.append(f"⚠️ Response may touch on '{topic}' — verify independently.")
    return warnings


# ─── Core Logic ────────────────────────────────────────────

def rag_query_demo(query):
    """RAG pipeline using local vector store (demo mode)."""
    simulate_latency(0.5, 2.0)

    # Step 1: Retrieve
    store = SimpleVectorStore()
    store.add_documents(KNOWLEDGE_BASE)
    search_results = store.search(query, top_k=2)

    # Step 2: Build context
    context_docs = [r["document"]["content"] for r in search_results]
    context = "\n---\n".join(context_docs)

    # Step 3: Generate (mock)
    answer = (
        f"Based on our knowledge base:\n\n"
        f"{context}\n\n"
        f"Summary: The above information should address your question about '{query}'."
    )

    # Step 4: Guardrails
    warnings = apply_guardrails(query, answer)

    return {
        "query": query,
        "answer": answer,
        "sources": [r["document"]["id"] for r in search_results],
        "relevance_scores": [r["relevance_score"] for r in search_results],
        "warnings": warnings,
        "mode": "demo",
    }


def rag_query_openai(query):
    """RAG pipeline with OpenAI for generation."""
    try:
        from openai import OpenAI

        # Step 1: Retrieve (still local)
        store = SimpleVectorStore()
        store.add_documents(KNOWLEDGE_BASE)
        search_results = store.search(query, top_k=2)
        context = "\n---\n".join([r["document"]["content"] for r in search_results])

        # Step 2: Generate with LLM
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful customer support assistant. "
                        "Answer questions ONLY using the provided context. "
                        "If the answer is not in the context, say so.\n\n"
                        f"Context:\n{context}"
                    ),
                },
                {"role": "user", "content": query},
            ],
            max_tokens=300,
            temperature=0.3,
        )

        answer = response.choices[0].message.content
        warnings = apply_guardrails(query, answer)

        return {
            "query": query,
            "answer": answer,
            "sources": [r["document"]["id"] for r in search_results],
            "tokens_used": response.usage.total_tokens,
            "warnings": warnings,
            "mode": "openai_rag",
        }
    except Exception as e:
        print(f"OpenAI Error: {e}")
        return None


def query(user_query):
    """Main entry point."""
    print(f"[Mode: {MODE}] Processing query: '{user_query}'")

    if is_demo():
        return rag_query_demo(user_query)
    elif OPENAI_API_KEY:
        return rag_query_openai(user_query)
    else:
        print("No API keys configured. Running in demo mode.")
        return rag_query_demo(user_query)


# ─── CLI ───────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Customer Support Knowledge Base Q&A")
    parser.add_argument("--query", default="What is your return policy?")
    args = parser.parse_args()

    result = query(args.query)
    if result:
        print("\n" + "=" * 60)
        print("  Knowledge Base Q&A Result")
        print("=" * 60)
        print(f"\nQ: {result['query']}")
        print(f"\nA: {result['answer']}")
        print(f"\nSources: {result['sources']}")
        if result.get("warnings"):
            print(f"\nWarnings: {result['warnings']}")
        print(f"\n[Mode: {result['mode']}]")


if __name__ == "__main__":
    main()
