"""RAG endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from ...core.config import get_settings, Settings
from ...models.factory import ProviderFactory
from ...infrastructure.vector_stores.chroma_store import ChromaVectorStore
from ...services.rag_service import RAGService

router = APIRouter()


class AddDocumentsRequest(BaseModel):
    """Add documents request"""
    texts: List[str]
    metadatas: Optional[List[Dict[str, Any]]] = None


class QueryRequest(BaseModel):
    """RAG query request"""
    question: str
    system_prompt: Optional[str] = None
    filter_metadata: Optional[Dict[str, Any]] = None
    provider: Optional[str] = None


@router.post("/rag/documents")
async def add_documents(
    request: AddDocumentsRequest,
    settings: Settings = Depends(get_settings),
):
    """Add documents to RAG knowledge base"""
    try:
        # Setup provider
        config = {
            "api_key": settings.openai_api_key,
            "model": settings.openai_model,
            "embedding_model": settings.openai_embedding_model,
        }
        provider = ProviderFactory.create_provider("openai", config)
        
        # Setup vector store
        vector_config = {
            "host": settings.chroma_host,
            "port": settings.chroma_port,
            "collection_name": settings.chroma_collection_name,
        }
        vector_store = ChromaVectorStore(vector_config)
        
        # Create RAG service
        rag_service = RAGService(provider, vector_store)
        
        # Add documents
        doc_ids = await rag_service.add_documents(
            texts=request.texts,
            metadatas=request.metadatas,
        )
        
        return {"document_ids": doc_ids, "count": len(doc_ids)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rag/query")
async def query_rag(
    request: QueryRequest,
    settings: Settings = Depends(get_settings),
):
    """Query RAG system"""
    try:
        # Setup provider
        provider_type = request.provider or settings.default_provider
        config = {
            "api_key": settings.openai_api_key,
            "model": settings.openai_model,
            "embedding_model": settings.openai_embedding_model,
        }
        provider = ProviderFactory.create_provider(provider_type, config)
        
        # Setup vector store
        vector_config = {
            "host": settings.chroma_host,
            "port": settings.chroma_port,
            "collection_name": settings.chroma_collection_name,
        }
        vector_store = ChromaVectorStore(vector_config)
        
        # Create RAG service
        rag_service = RAGService(provider, vector_store)
        
        # Query
        result = await rag_service.query(
            question=request.question,
            system_prompt=request.system_prompt,
            filter_metadata=request.filter_metadata,
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
