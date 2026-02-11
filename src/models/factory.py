"""Model provider factory"""
from typing import Dict, Any
from .base import BaseModelProvider
from .openai_provider import OpenAIProvider
from .azure_provider import AzureOpenAIProvider
from .aws_provider import AWSBedrockProvider
from .google_provider import GoogleVertexAIProvider


class ProviderFactory:
    """Factory for creating model providers"""
    
    _providers = {
        "openai": OpenAIProvider,
        "azure": AzureOpenAIProvider,
        "aws": AWSBedrockProvider,
        "google": GoogleVertexAIProvider,
    }
    
    @classmethod
    def create_provider(cls, provider_type: str, config: Dict[str, Any]) -> BaseModelProvider:
        """Create a model provider instance"""
        provider_class = cls._providers.get(provider_type)
        
        if not provider_class:
            raise ValueError(f"Unknown provider type: {provider_type}")
        
        return provider_class(config)
    
    @classmethod
    def register_provider(cls, name: str, provider_class: type):
        """Register a custom provider"""
        cls._providers[name] = provider_class
    
    @classmethod
    def list_providers(cls) -> list:
        """List all available providers"""
        return list(cls._providers.keys())
