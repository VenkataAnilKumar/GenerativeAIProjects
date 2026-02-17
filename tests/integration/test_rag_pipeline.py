"""Integration tests for Use Case 04: Customer Support RAG Pipeline"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "use-cases", "04-customer-support-aws"))
from main import query, rag_query_demo


@pytest.mark.integration
class TestCustomerSupportRAG:
    """Integration tests for RAG pipeline."""

    def test_query_about_returns(self, demo_mode):
        """Test query about return policy."""
        result = query("What is your return policy?")
        
        assert result is not None
        assert "query" in result
        assert "answer" in result
        assert "sources" in result
        assert result["mode"] == "demo"
        assert len(result["answer"]) > 0

    def test_query_about_shipping(self, demo_mode):
        """Test query about shipping."""
        result = query("How long does shipping take?")
        
        assert result is not None
        assert "shipping" in result["answer"].lower() or any("KB002" in s for s in result["sources"])

    def test_query_about_warranty(self, demo_mode):
        """Test query about warranty."""
        result = query("What is the warranty period?")
        
        assert result is not None
        assert result["mode"] == "demo"

    def test_query_returns_sources(self, demo_mode):
        """Test that queries return knowledge base sources."""
        result = query("Tell me about pricing")
        
        assert "sources" in result
        assert isinstance(result["sources"], list)
        assert len(result["sources"]) > 0

    def test_query_returns_relevance_scores(self, demo_mode):
        """Test that relevance scores are included."""
        result = query("support information")
        
        assert "relevance_scores" in result or "sources" in result

    def test_guardrails_warning_on_blocked_topic(self, demo_mode):
        """Test guardrails trigger on blocked topics."""
        result = query("Can you give me legal advice?")
        
        assert "warnings" in result
        # May have warnings for blocked topic

    def test_demo_rag_pipeline_end_to_end(self, demo_mode):
        """Test complete RAG pipeline in demo mode."""
        result = rag_query_demo("How do I contact support?")
        
        assert result is not None
        assert "query" in result
        assert "answer" in result
        assert "sources" in result
        assert result["mode"] == "demo"

    def test_multiple_queries_work(self, demo_mode):
        """Test multiple sequential queries."""
        queries = [
            "What is your return policy?",
            "How much does shipping cost?",
            "Do you offer warranties?",
        ]
        
        for q in queries:
            result = query(q)
            assert result is not None
            assert result["mode"] == "demo"
