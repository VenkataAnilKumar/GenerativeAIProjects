"""Tests for model providers"""
import pytest
from src.models.factory import ProviderFactory


def test_provider_factory_list():
    """Test listing available providers"""
    providers = ProviderFactory.list_providers()
    assert "openai" in providers
    assert "azure" in providers
    assert "google" in providers
    assert "aws" in providers


def test_provider_factory_invalid():
    """Test creating invalid provider"""
    with pytest.raises(ValueError):
        ProviderFactory.create_provider("invalid", {})
