"""Multimodal endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from ...core.config import get_settings, Settings
from ...models.factory import ProviderFactory
from ...models.base import MultimodalRequest

router = APIRouter()


class MultimodalRequestModel(BaseModel):
    """Multimodal request model"""
    prompt: str
    image_url: Optional[str] = None
    image_base64: Optional[str] = None
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7
    provider: Optional[str] = None


class MultimodalResponseModel(BaseModel):
    """Multimodal response model"""
    content: str
    model: str
    usage: dict


@router.post("/multimodal", response_model=MultimodalResponseModel)
async def multimodal_inference(
    request: MultimodalRequestModel,
    settings: Settings = Depends(get_settings),
):
    """Multimodal inference endpoint"""
    try:
        provider_type = request.provider or settings.default_provider
        
        config = {}
        if provider_type == "openai":
            config = {
                "api_key": settings.openai_api_key,
                "model": settings.openai_model,
            }
        elif provider_type == "google":
            config = {
                "project_id": settings.google_project_id,
                "location": settings.google_location,
            }
        
        provider = ProviderFactory.create_provider(provider_type, config)
        
        multimodal_request = MultimodalRequest(
            prompt=request.prompt,
            image_url=request.image_url,
            image_base64=request.image_base64,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
        )
        
        response = await provider.multimodal(multimodal_request)
        
        return MultimodalResponseModel(
            content=response.content,
            model=response.model,
            usage=response.usage,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
