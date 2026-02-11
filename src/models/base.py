"""Abstract base classes for model providers"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, AsyncIterator
from pydantic import BaseModel


class Message(BaseModel):
    """Chat message model"""
    role: str
    content: str


class CompletionRequest(BaseModel):
    """Text completion request"""
    prompt: str
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 1.0
    stream: bool = False


class ChatRequest(BaseModel):
    """Chat completion request"""
    messages: List[Message]
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 1.0
    stream: bool = False


class EmbeddingRequest(BaseModel):
    """Embedding request"""
    texts: List[str]
    model: Optional[str] = None


class MultimodalRequest(BaseModel):
    """Multimodal inference request"""
    prompt: str
    image_url: Optional[str] = None
    image_base64: Optional[str] = None
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7


class ModelResponse(BaseModel):
    """Standard model response"""
    content: str
    model: str
    usage: Dict[str, int]
    finish_reason: Optional[str] = None
    metadata: Dict[str, Any] = {}


class EmbeddingResponse(BaseModel):
    """Embedding response"""
    embeddings: List[List[float]]
    model: str
    usage: Dict[str, int]


class BaseModelProvider(ABC):
    """Abstract base class for all model providers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.provider_name = self.__class__.__name__
    
    @abstractmethod
    async def complete(self, request: CompletionRequest) -> ModelResponse:
        """Generate text completion"""
        pass
    
    @abstractmethod
    async def chat(self, request: ChatRequest) -> ModelResponse:
        """Generate chat completion"""
        pass
    
    @abstractmethod
    async def stream_chat(self, request: ChatRequest) -> AsyncIterator[str]:
        """Stream chat completion"""
        pass
    
    @abstractmethod
    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """Generate embeddings"""
        pass
    
    @abstractmethod
    async def multimodal(self, request: MultimodalRequest) -> ModelResponse:
        """Generate multimodal inference"""
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the model"""
        pass
