"""Text completion endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from ...core.config import get_settings, Settings
from ...models.factory import ProviderFactory
from ...models.base import CompletionRequest

router = APIRouter()


class CompletionRequestModel(BaseModel):
    """Completion request model"""
    prompt: str
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7
    provider: Optional[str] = None


class CompletionResponseModel(BaseModel):
    """Completion response model"""
    content: str
    model: str
    usage: dict


@router.post("/completion", response_model=CompletionResponseModel)
async def text_completion(
    request: CompletionRequestModel,
    settings: Settings = Depends(get_settings),
):
    """Text completion endpoint"""
    try:
        provider_type = request.provider or settings.default_provider
        
        config = {}
        if provider_type == "openai":
            config = {
                "api_key": settings.openai_api_key,
                "model": settings.openai_model,
            }
        elif provider_type == "azure":
            config = {
                "api_key": settings.azure_openai_api_key,
                "endpoint": settings.azure_openai_endpoint,
                "deployment": settings.azure_openai_deployment,
            }
        
        provider = ProviderFactory.create_provider(provider_type, config)
        
        completion_request = CompletionRequest(
            prompt=request.prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
        )
        
        response = await provider.complete(completion_request)
        
        return CompletionResponseModel(
            content=response.content,
            model=response.model,
            usage=response.usage,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
