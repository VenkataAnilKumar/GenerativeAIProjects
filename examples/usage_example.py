#!/usr/bin/env python3
"""
Example script demonstrating GenAI Platform usage
"""
import asyncio
import os
from src.models.factory import ProviderFactory
from src.models.base import ChatRequest, Message, EmbeddingRequest
from src.services.code_service import CodeCompletionService
from src.services.rag_service import RAGService
from src.infrastructure.vector_stores.chroma_store import ChromaVectorStore


async def chat_example():
    """Example: Chat completion"""
    print("\n=== Chat Completion Example ===")
    
    # Initialize provider
    config = {
        "api_key": os.getenv("OPENAI_API_KEY"),
        "model": "gpt-4",
    }
    provider = ProviderFactory.create_provider("openai", config)
    
    # Create chat request
    messages = [
        Message(role="system", content="You are a helpful assistant."),
        Message(role="user", content="What is the capital of France?"),
    ]
    request = ChatRequest(messages=messages, temperature=0.7)
    
    # Get response
    response = await provider.chat(request)
    print(f"Response: {response.content}")
    print(f"Model: {response.model}")
    print(f"Tokens: {response.usage}")


async def code_completion_example():
    """Example: Code completion"""
    print("\n=== Code Completion Example ===")
    
    # Initialize provider
    config = {
        "api_key": os.getenv("OPENAI_API_KEY"),
        "model": "gpt-4",
    }
    provider = ProviderFactory.create_provider("openai", config)
    service = CodeCompletionService(provider)
    
    # Complete code
    result = await service.complete_code(
        code="def factorial(n):",
        language="python",
        instruction="Complete this factorial function using recursion"
    )
    print(f"Completion:\n{result['completion']}")


async def rag_example():
    """Example: RAG query"""
    print("\n=== RAG Example ===")
    
    # Initialize provider
    config = {
        "api_key": os.getenv("OPENAI_API_KEY"),
        "model": "gpt-4",
        "embedding_model": "text-embedding-3-small",
    }
    provider = ProviderFactory.create_provider("openai", config)
    
    # Initialize vector store
    vector_config = {
        "host": "localhost",
        "port": 8001,
        "collection_name": "example-collection",
    }
    vector_store = ChromaVectorStore(vector_config)
    
    # Create RAG service
    rag_service = RAGService(provider, vector_store)
    
    # Add documents
    texts = [
        "Paris is the capital and largest city of France.",
        "London is the capital of the United Kingdom.",
        "Berlin is the capital of Germany.",
    ]
    doc_ids = await rag_service.add_documents(texts)
    print(f"Added {len(doc_ids)} documents")
    
    # Query
    result = await rag_service.query("What is the capital of France?")
    print(f"\nQuestion: What is the capital of France?")
    print(f"Answer: {result['answer']}")
    print(f"\nSources:")
    for i, source in enumerate(result['sources'], 1):
        print(f"  {i}. {source['content']} (score: {source['score']:.2f})")


async def multimodal_example():
    """Example: Multimodal inference"""
    print("\n=== Multimodal Example ===")
    
    # Initialize provider
    config = {
        "api_key": os.getenv("OPENAI_API_KEY"),
        "model": "gpt-4",
    }
    provider = ProviderFactory.create_provider("openai", config)
    
    # Note: This requires an actual image URL
    from src.models.base import MultimodalRequest
    request = MultimodalRequest(
        prompt="What is in this image?",
        image_url="https://example.com/image.jpg",
    )
    
    try:
        response = await provider.multimodal(request)
        print(f"Response: {response.content}")
    except Exception as e:
        print(f"Note: Multimodal example requires a valid image URL: {e}")


async def main():
    """Run all examples"""
    print("GenAI Platform - Usage Examples")
    print("=" * 50)
    
    try:
        await chat_example()
        await code_completion_example()
        # Uncomment if you have Chroma running
        # await rag_example()
        # await multimodal_example()
    except Exception as e:
        print(f"\nError: {e}")
        print("\nMake sure to set OPENAI_API_KEY environment variable")


if __name__ == "__main__":
    asyncio.run(main())
