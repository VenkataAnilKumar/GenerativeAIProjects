"""
Shared pytest fixtures for all tests.
"""

import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scripts.config import MODE
from scripts.mock_data import (
    MARKETING_RESPONSES,
    KNOWLEDGE_BASE,
    MEDICAL_REPORTS,
    LEARNING_CONTENT,
)


@pytest.fixture
def demo_mode():
    """Ensure tests run in demo mode."""
    original = os.environ.get("RUN_MODE")
    os.environ["RUN_MODE"] = "demo"
    yield
    if original:
        os.environ["RUN_MODE"] = original
    else:
        os.environ.pop("RUN_MODE", None)


@pytest.fixture
def sample_prompt():
    """Sample prompt for testing."""
    return {
        "product": "Test Product",
        "audience": "Test Audience",
        "tone": "professional",
    }


@pytest.fixture
def sample_code():
    """Sample code for testing code-related use cases."""
    return '''
def calculate_sum(a, b):
    """Add two numbers."""
    return a + b

class Calculator:
    def multiply(self, x, y):
        return x * y
'''


@pytest.fixture
def sample_medical_report():
    """Sample medical report for testing."""
    return MEDICAL_REPORTS[0]["report"]


@pytest.fixture
def sample_knowledge_base():
    """Sample knowledge base for RAG testing."""
    return KNOWLEDGE_BASE


@pytest.fixture
def sample_query():
    """Sample user query for RAG testing."""
    return "What is your return policy?"
