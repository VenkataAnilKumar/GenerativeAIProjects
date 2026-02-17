"""
Advanced RAG Module
Provides FAISS vector store with sentence-transformer embeddings,
hybrid search (keyword + semantic), and re-ranking.
Falls back to simple TF-IDF if dependencies are unavailable.
"""

import os
import json
import math
import re
from typing import List, Dict, Optional, Tuple
from collections import Counter


# ─── Embedding Backends ──────────────────────────────────────

class SimpleEmbedder:
    """
    TF-IDF–based embedder (zero dependencies).
    Used as fallback when sentence-transformers is not installed.
    """

    def __init__(self):
        self.vocab = {}
        self.idf = {}
        self.fitted = False

    def fit(self, documents: List[str]):
        """Build vocabulary and IDF from documents."""
        doc_freq = Counter()
        for doc in documents:
            tokens = set(self._tokenize(doc))
            for token in tokens:
                doc_freq[token] += 1
        n = len(documents)
        self.idf = {
            w: math.log((n + 1) / (df + 1)) + 1
            for w, df in doc_freq.items()
        }
        self.vocab = {w: i for i, w in enumerate(self.idf)}
        self.fitted = True

    def encode(self, texts: List[str]) -> List[List[float]]:
        """Encode texts into TF-IDF vectors."""
        if not self.fitted:
            self.fit(texts)
        vectors = []
        for text in texts:
            tokens = self._tokenize(text)
            tf = Counter(tokens)
            vec = [0.0] * len(self.vocab)
            for token, count in tf.items():
                if token in self.vocab:
                    idx = self.vocab[token]
                    vec[idx] = (count / len(tokens)) * self.idf.get(token, 1.0)
            # Normalize
            norm = math.sqrt(sum(v * v for v in vec)) or 1.0
            vec = [v / norm for v in vec]
            vectors.append(vec)
        return vectors

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r"\w+", text.lower())


class SentenceTransformerEmbedder:
    """
    Embedding backend using sentence-transformers.
    Requires: pip install sentence-transformers
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name)

    def fit(self, documents: List[str]):
        """No fitting needed for pre-trained models."""
        pass

    def encode(self, texts: List[str]) -> List[List[float]]:
        """Encode texts into dense embeddings."""
        embeddings = self.model.encode(texts, show_progress_bar=False)
        return [emb.tolist() for emb in embeddings]


def get_embedder(use_sentence_transformers: bool = True):
    """Factory: return best available embedder."""
    if use_sentence_transformers:
        try:
            return SentenceTransformerEmbedder()
        except ImportError:
            pass
    return SimpleEmbedder()


# ─── Vector Stores ───────────────────────────────────────────

class FAISSVectorStore:
    """
    FAISS-based vector store for fast similarity search.
    Requires: pip install faiss-cpu
    Falls back to brute-force numpy if FAISS unavailable.
    """

    def __init__(self, embedder=None):
        self.embedder = embedder or get_embedder(use_sentence_transformers=False)
        self.documents = []
        self.index = None
        self._use_faiss = False

        try:
            import faiss
            self._use_faiss = True
        except ImportError:
            pass

    def add_documents(self, documents: List[Dict]):
        """Add documents to the store and build the index."""
        self.documents = documents
        texts = [doc.get("content", "") for doc in documents]

        # Fit embedder
        self.embedder.fit(texts)
        vectors = self.embedder.encode(texts)

        if self._use_faiss:
            import faiss
            import numpy as np
            dim = len(vectors[0])
            self.index = faiss.IndexFlatIP(dim)  # Inner product
            matrix = np.array(vectors, dtype="float32")
            faiss.normalize_L2(matrix)
            self.index.add(matrix)
            self._vectors = matrix
        else:
            self._vectors = vectors

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search for documents similar to the query."""
        q_vec = self.embedder.encode([query])

        if self._use_faiss:
            import numpy as np
            q = np.array(q_vec, dtype="float32")
            import faiss
            faiss.normalize_L2(q)
            scores, indices = self.index.search(q, min(top_k, len(self.documents)))
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(self.documents):
                    results.append({
                        "document": self.documents[idx],
                        "relevance_score": float(score),
                    })
            return results
        else:
            return self._brute_force_search(q_vec[0], top_k)

    def _brute_force_search(self, query_vec, top_k):
        """Cosine similarity with brute force (fallback)."""
        scores = []
        for i, doc_vec in enumerate(self._vectors):
            dot = sum(a * b for a, b in zip(query_vec, doc_vec))
            scores.append((dot, i))

        scores.sort(key=lambda x: x[0], reverse=True)

        results = []
        for score, idx in scores[:top_k]:
            results.append({
                "document": self.documents[idx],
                "relevance_score": round(score, 4),
            })
        return results


# ─── Hybrid Search ───────────────────────────────────────────

class HybridSearchEngine:
    """
    Combines keyword (BM25-style) and semantic (vector) search.
    Merges results with weighted scoring.
    """

    def __init__(self, semantic_weight: float = 0.7):
        self.semantic_weight = semantic_weight
        self.keyword_weight = 1.0 - semantic_weight
        self.vector_store = FAISSVectorStore()
        self.documents = []

    def add_documents(self, documents: List[Dict]):
        """Index documents for both keyword and semantic search."""
        self.documents = documents
        self.vector_store.add_documents(documents)

        # Build inverted index for keyword search
        self._inverted_index = {}
        for i, doc in enumerate(documents):
            tokens = re.findall(r"\w+", doc.get("content", "").lower())
            for token in set(tokens):
                self._inverted_index.setdefault(token, []).append(i)

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Hybrid search combining keyword and semantic results."""
        # Semantic search
        semantic_results = self.vector_store.search(query, top_k=top_k * 2)

        # Keyword search (BM25-style)
        keyword_scores = self._keyword_search(query)

        # Merge with weights
        merged = {}

        for i, result in enumerate(semantic_results):
            doc_id = result["document"].get("id", i)
            merged[doc_id] = {
                "document": result["document"],
                "semantic_score": result["relevance_score"],
                "keyword_score": 0.0,
            }

        for doc_idx, score in keyword_scores.items():
            doc_id = self.documents[doc_idx].get("id", doc_idx)
            if doc_id in merged:
                merged[doc_id]["keyword_score"] = score
            else:
                merged[doc_id] = {
                    "document": self.documents[doc_idx],
                    "semantic_score": 0.0,
                    "keyword_score": score,
                }

        # Calculate combined score
        results = []
        for doc_id, data in merged.items():
            combined = (
                self.semantic_weight * data["semantic_score"]
                + self.keyword_weight * data["keyword_score"]
            )
            results.append({
                "document": data["document"],
                "relevance_score": round(combined, 4),
                "semantic_score": round(data["semantic_score"], 4),
                "keyword_score": round(data["keyword_score"], 4),
            })

        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results[:top_k]

    def _keyword_search(self, query: str) -> Dict[int, float]:
        """Simple BM25-style keyword scoring."""
        query_tokens = re.findall(r"\w+", query.lower())
        scores = Counter()

        for token in query_tokens:
            if token in self._inverted_index:
                matching_docs = self._inverted_index[token]
                idf = math.log(
                    (len(self.documents) + 1) / (len(matching_docs) + 1)
                ) + 1
                for doc_idx in matching_docs:
                    scores[doc_idx] += idf

        # Normalize to 0-1
        if scores:
            max_score = max(scores.values())
            return {k: v / max_score for k, v in scores.items()}
        return {}


# ─── Convenience ─────────────────────────────────────────────

def create_rag_engine(
    documents: List[Dict],
    hybrid: bool = True,
    semantic_weight: float = 0.7,
) -> HybridSearchEngine:
    """
    Factory to create a ready-to-use RAG search engine.
    
    Usage:
        engine = create_rag_engine(docs)
        results = engine.search("What is the return policy?")
    """
    if hybrid:
        engine = HybridSearchEngine(semantic_weight=semantic_weight)
    else:
        engine = FAISSVectorStore()
    engine.add_documents(documents)
    return engine
