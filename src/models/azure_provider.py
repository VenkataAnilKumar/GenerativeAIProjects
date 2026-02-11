"""Azure OpenAI model provider implementation"""
from typing import Dict, Any, AsyncIterator
from openai import AsyncAzureOpenAI
from .base import (
    BaseModelProvider, CompletionRequest, ChatRequest, 
    EmbeddingRequest, MultimodalRequest, ModelResponse, EmbeddingResponse
)


class AzureOpenAIProvider(BaseModelProvider):
    """Azure OpenAI model provider"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        api_key = config.get("api_key")
        endpoint = config.get("endpoint")
        
        if not api_key or not endpoint:
            raise ValueError("Azure OpenAI API key and endpoint are required")
        
        self.client = AsyncAzureOpenAI(
            api_key=api_key,
            api_version=config.get("api_version", "2024-02-15-preview"),
            azure_endpoint=endpoint,
        )
        self.deployment = config.get("deployment", "gpt-4")
    
    async def complete(self, request: CompletionRequest) -> ModelResponse:
        """Generate text completion"""
        response = await self.client.completions.create(
            model=self.deployment,
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
            model=self.deployment,
            messages=messages,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=request.top_p,
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
            model=self.deployment,
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
        response = await self.client.embeddings.create(
            model=self.deployment,
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
            model=self.deployment,
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
            "provider": "azure",
            "deployment": self.deployment,
        }
