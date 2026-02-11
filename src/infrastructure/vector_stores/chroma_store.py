"""Chroma vector store implementation"""
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from .base import BaseVectorStore, Document, SearchResult
import uuid


class ChromaVectorStore(BaseVectorStore):
    """Chroma vector store implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        host = config.get("host", "localhost")
        port = config.get("port", 8001)
        collection_name = config.get("collection_name", "genai-collection")
        
        self.client = chromadb.HttpClient(host=host, port=port)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
    
    async def add_documents(self, documents: List[Document]) -> List[str]:
        """Add documents to the vector store"""
        ids = []
        contents = []
        embeddings = []
        metadatas = []
        
        for doc in documents:
            doc_id = doc.id or str(uuid.uuid4())
            ids.append(doc_id)
            contents.append(doc.content)
            embeddings.append(doc.embedding)
            metadatas.append(doc.metadata)
        
        self.collection.add(
            ids=ids,
            documents=contents,
            embeddings=embeddings,
            metadatas=metadatas,
        )
        
        return ids
    
    async def search(
        self, 
        query_embedding: List[float], 
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Search for similar documents"""
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter_metadata,
        )
        
        search_results = []
        for i in range(len(results['ids'][0])):
            doc = Document(
                id=results['ids'][0][i],
                content=results['documents'][0][i],
                metadata=results['metadatas'][0][i] if results['metadatas'] else {},
            )
            search_results.append(SearchResult(
                document=doc,
                score=1 - results['distances'][0][i]  # Convert distance to similarity
            ))
        
        return search_results
    
    async def delete_documents(self, ids: List[str]) -> bool:
        """Delete documents by IDs"""
        try:
            self.collection.delete(ids=ids)
            return True
        except Exception:
            return False
    
    async def get_document(self, doc_id: str) -> Optional[Document]:
        """Get a document by ID"""
        try:
            results = self.collection.get(ids=[doc_id])
            if results['ids']:
                return Document(
                    id=results['ids'][0],
                    content=results['documents'][0],
                    metadata=results['metadatas'][0] if results['metadatas'] else {},
                )
        except Exception:
            pass
        return None
    
    async def update_document(self, doc_id: str, document: Document) -> bool:
        """Update a document"""
        try:
            self.collection.update(
                ids=[doc_id],
                documents=[document.content],
                embeddings=[document.embedding] if document.embedding else None,
                metadatas=[document.metadata],
            )
            return True
        except Exception:
            return False
    
    def get_store_info(self) -> Dict[str, Any]:
        """Get information about the vector store"""
        return {
            "type": "chroma",
            "collection": self.collection.name,
            "count": self.collection.count(),
        }
