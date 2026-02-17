"""Unit tests for RAG vector store (Use Case 04)"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "use-cases", "04-customer-support-aws"))
from main import SimpleVectorStore, apply_guardrails


@pytest.mark.unit
class TestSimpleVectorStore:
    """Test the local TF-IDF vector store."""

    def test_initialization(self):
        """Test vector store initializes empty."""
        store = SimpleVectorStore()
        assert store.documents == []
        assert store.doc_vectors == []

    def test_tokenize(self):
        """Test simple tokenization."""
        store = SimpleVectorStore()
        tokens = store._tokenize("Hello World! This is a TEST.")
        assert "hello" in tokens
        assert "world" in tokens
        assert "test" in tokens
        assert "!" not in tokens  # Punctuation removed

    def test_add_documents(self):
        """Test adding documents to vector store."""
        store = SimpleVectorStore()
        docs = [
            {"id": "1", "content": "Python programming language"},
            {"id": "2", "content": "JavaScript web development"},
        ]
        store.add_documents(docs)
        assert len(store.documents) == 2
        assert len(store.doc_vectors) == 2

    def test_search_returns_results(self, sample_knowledge_base):
        """Test search returns ranked results."""
        store = SimpleVectorStore()
        store.add_documents(sample_knowledge_base)
        
        results = store.search("return policy", top_k=3)
        
        assert len(results) <= 3
        assert isinstance(results, list)
        if len(results) > 0:
            assert "document" in results[0]
            assert "relevance_score" in results[0]

    def test_search_relevance_ordering(self, sample_knowledge_base):
        """Test search results are ordered by relevance."""
        store = SimpleVectorStore()
        store.add_documents(sample_knowledge_base)
        
        results = store.search("shipping information", top_k=3)
        
        if len(results) >= 2:
            # Scores should be descending
            assert results[0]["relevance_score"] >= results[1]["relevance_score"]

    def test_search_with_no_matches(self):
        """Test search with query that matches nothing."""
        store = SimpleVectorStore()
        store.add_documents([{"id": "1", "content": "completely unrelated text"}])
        
        results = store.search("xyz123 nonexistent query")
        
        # Should still return results, just with low scores
        assert isinstance(results, list)


@pytest.mark.unit
class TestGuardrails:
    """Test content guardrails."""

    def test_no_warnings_for_safe_content(self):
        """Test safe content passes without warnings."""
        query = "How do I track my order?"
        response = "You can track your order using the tracking number."
        
        warnings = apply_guardrails(query, response)
        
        assert isinstance(warnings, list)
        assert len(warnings) == 0

    def test_warning_for_blocked_topic(self):
        """Test blocked topics trigger warnings."""
        query = "Can you give me legal advice?"
        response = "Here's some legal advice about contracts."
        
        warnings = apply_guardrails(query, response)
        
        assert len(warnings) > 0
        assert any("legal advice" in w for w in warnings)

    def test_warning_for_medical_advice(self):
        """Test medical advice triggers warning."""
        query = "What medicine should I take?"
        response = "You should take medical advice from a doctor."
        
        warnings = apply_guardrails(query, response)
        
        assert len(warnings) > 0

    def test_multiple_blocked_topics(self):
        """Test multiple blocked topics are detected."""
        query = "I need legal advice and medical advice"
        response = "Here's financial advice too"
        
        warnings = apply_guardrails(query, response)
        
        assert len(warnings) >= 2  # At least legal and medical
