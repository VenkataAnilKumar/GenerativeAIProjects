"""Abstract base class for vector stores"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class Document(BaseModel):
    """Document model for vector stores"""
    id: Optional[str] = None
    content: str
    metadata: Dict[str, Any] = {}
    embedding: Optional[List[float]] = None


class SearchResult(BaseModel):
    """Search result model"""
    document: Document
    score: float


class BaseVectorStore(ABC):
    """Abstract base class for vector stores"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.store_name = self.__class__.__name__
    
    @abstractmethod
    async def add_documents(self, documents: List[Document]) -> List[str]:
        """Add documents to the vector store"""
        pass
    
    @abstractmethod
    async def search(
        self, 
        query_embedding: List[float], 
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Search for similar documents"""
        pass
    
    @abstractmethod
    async def delete_documents(self, ids: List[str]) -> bool:
        """Delete documents by IDs"""
        pass
    
    @abstractmethod
    async def get_document(self, doc_id: str) -> Optional[Document]:
        """Get a document by ID"""
        pass
    
    @abstractmethod
    async def update_document(self, doc_id: str, document: Document) -> bool:
        """Update a document"""
        pass
    
    @abstractmethod
    def get_store_info(self) -> Dict[str, Any]:
        """Get information about the vector store"""
        pass
