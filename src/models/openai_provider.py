"""OpenAI model provider implementation"""
from typing import Dict, Any, AsyncIterator
import openai
from openai import AsyncOpenAI
from .base import (
    BaseModelProvider, CompletionRequest, ChatRequest, 
    EmbeddingRequest, MultimodalRequest, ModelResponse, EmbeddingResponse
)


class OpenAIProvider(BaseModelProvider):
    """OpenAI model provider"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        api_key = config.get("api_key")
        if not api_key:
            raise ValueError("OpenAI API key is required")
        
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = config.get("model", "gpt-4")
        self.embedding_model = config.get("embedding_model", "text-embedding-3-small")
    
    async def complete(self, request: CompletionRequest) -> ModelResponse:
        """Generate text completion"""
        response = await self.client.completions.create(
            model=self.model,
            prompt=request.prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=request.top_p,
        )
        
        return ModelResponse(
            content=response.choices[0].text,
            model=response.model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
            finish_reason=response.choices[0].finish_reason,
        )
    
    async def chat(self, request: ChatRequest) -> ModelResponse:
        """Generate chat completion"""
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=request.top_p,
            stream=False,
        )
        
        return ModelResponse(
            content=response.choices[0].message.content,
            model=response.model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
            finish_reason=response.choices[0].finish_reason,
        )
    
    async def stream_chat(self, request: ChatRequest) -> AsyncIterator[str]:
        """Stream chat completion"""
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=request.top_p,
            stream=True,
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """Generate embeddings"""
        model = request.model or self.embedding_model
        
        response = await self.client.embeddings.create(
            model=model,
            input=request.texts,
        )
        
        embeddings = [item.embedding for item in response.data]
        
        return EmbeddingResponse(
            embeddings=embeddings,
            model=response.model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "total_tokens": response.usage.total_tokens,
            },
        )
    
    async def multimodal(self, request: MultimodalRequest) -> ModelResponse:
        """Generate multimodal inference"""
        content = [{"type": "text", "text": request.prompt}]
        
        if request.image_url:
            content.append({
                "type": "image_url",
                "image_url": {"url": request.image_url}
            })
        elif request.image_base64:
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{request.image_base64}"}
            })
        
        response = await self.client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[{"role": "user", "content": content}],
            max_tokens=request.max_tokens,
            temperature=request.temperature,
        )
        
        return ModelResponse(
            content=response.choices[0].message.content,
            model=response.model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
            finish_reason=response.choices[0].finish_reason,
        )
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the model"""
        return {
            "provider": "openai",
            "model": self.model,
            "embedding_model": self.embedding_model,
        }
