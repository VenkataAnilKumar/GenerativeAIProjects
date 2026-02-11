"""Pinecone vector store implementation"""
from typing import List, Dict, Any, Optional
import pinecone
from .base import BaseVectorStore, Document, SearchResult
import uuid


class PineconeVectorStore(BaseVectorStore):
    """Pinecone vector store implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        api_key = config.get("api_key")
        environment = config.get("environment")
        index_name = config.get("index_name", "genai-index")
        
        if not api_key or not environment:
            raise ValueError("Pinecone API key and environment are required")
        
        pinecone.init(api_key=api_key, environment=environment)
        self.index = pinecone.Index(index_name)
        self.index_name = index_name
    
    async def add_documents(self, documents: List[Document]) -> List[str]:
        """Add documents to the vector store"""
        vectors = []
        doc_ids = []
        
        for doc in documents:
            doc_id = doc.id or str(uuid.uuid4())
            doc_ids.append(doc_id)
            
            vectors.append({
                "id": doc_id,
                "values": doc.embedding,
                "metadata": {
                    "content": doc.content,
                    **doc.metadata
                }
            })
        
        self.index.upsert(vectors=vectors)
        return doc_ids
    
    async def search(
        self, 
        query_embedding: List[float], 
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Search for similar documents"""
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            filter=filter_metadata,
            include_metadata=True,
        )
        
        search_results = []
        for match in results["matches"]:
            metadata = match["metadata"]
            content = metadata.pop("content", "")
            
            doc = Document(
                id=match["id"],
                content=content,
                metadata=metadata,
            )
            search_results.append(SearchResult(
                document=doc,
                score=match["score"]
            ))
        
        return search_results
    
    async def delete_documents(self, ids: List[str]) -> bool:
        """Delete documents by IDs"""
        try:
            self.index.delete(ids=ids)
            return True
        except Exception:
            return False
    
    async def get_document(self, doc_id: str) -> Optional[Document]:
        """Get a document by ID"""
        try:
            results = self.index.fetch(ids=[doc_id])
            if doc_id in results["vectors"]:
                vector_data = results["vectors"][doc_id]
                metadata = vector_data["metadata"]
                content = metadata.pop("content", "")
                
                return Document(
                    id=doc_id,
                    content=content,
                    metadata=metadata,
                    embedding=vector_data["values"],
                )
        except Exception:
            pass
        return None
    
    async def update_document(self, doc_id: str, document: Document) -> bool:
        """Update a document"""
        try:
            self.index.upsert(vectors=[{
                "id": doc_id,
                "values": document.embedding,
                "metadata": {
                    "content": document.content,
                    **document.metadata
                }
            }])
            return True
        except Exception:
            return False
    
    def get_store_info(self) -> Dict[str, Any]:
        """Get information about the vector store"""
        stats = self.index.describe_index_stats()
        return {
            "type": "pinecone",
            "index_name": self.index_name,
            "dimension": stats.get("dimension"),
            "total_vectors": stats.get("total_vector_count"),
        }
