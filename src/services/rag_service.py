"""RAG (Retrieval Augmented Generation) service"""
from typing import List, Dict, Any, Optional
from ..models.base import BaseModelProvider, ChatRequest, Message, EmbeddingRequest
from ..infrastructure.vector_stores.base import BaseVectorStore, Document


class RAGService:
    """RAG service for retrieval-augmented generation"""
    
    def __init__(
        self, 
        model_provider: BaseModelProvider,
        vector_store: BaseVectorStore,
        top_k: int = 5,
    ):
        self.model_provider = model_provider
        self.vector_store = vector_store
        self.top_k = top_k
    
    async def add_documents(self, texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None) -> List[str]:
        """Add documents to the knowledge base"""
        # Generate embeddings
        embedding_request = EmbeddingRequest(texts=texts)
        embedding_response = await self.model_provider.embed(embedding_request)
        
        # Create documents
        documents = []
        for i, text in enumerate(texts):
            doc = Document(
                content=text,
                embedding=embedding_response.embeddings[i],
                metadata=metadatas[i] if metadatas else {},
            )
            documents.append(doc)
        
        # Add to vector store
        return await self.vector_store.add_documents(documents)
    
    async def query(
        self, 
        question: str, 
        system_prompt: Optional[str] = None,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Query the RAG system"""
        # Generate query embedding
        embedding_request = EmbeddingRequest(texts=[question])
        embedding_response = await self.model_provider.embed(embedding_request)
        query_embedding = embedding_response.embeddings[0]
        
        # Search for relevant documents
        search_results = await self.vector_store.search(
            query_embedding=query_embedding,
            top_k=self.top_k,
            filter_metadata=filter_metadata,
        )
        
        # Build context from retrieved documents
        context = "\n\n".join([
            f"Document {i+1}:\n{result.document.content}"
            for i, result in enumerate(search_results)
        ])
        
        # Build prompt
        messages = []
        if system_prompt:
            messages.append(Message(role="system", content=system_prompt))
        else:
            messages.append(Message(
                role="system",
                content="You are a helpful assistant. Answer the question based on the provided context."
            ))
        
        user_message = f"Context:\n{context}\n\nQuestion: {question}"
        messages.append(Message(role="user", content=user_message))
        
        # Generate response
        chat_request = ChatRequest(messages=messages)
        response = await self.model_provider.chat(chat_request)
        
        return {
            "answer": response.content,
            "sources": [
                {
                    "content": result.document.content,
                    "metadata": result.document.metadata,
                    "score": result.score,
                }
                for result in search_results
            ],
            "model": response.model,
            "usage": response.usage,
        }
