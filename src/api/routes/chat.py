"""Chat endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from ...core.config import get_settings, Settings
from ...models.factory import ProviderFactory
from ...models.base import ChatRequest, Message

router = APIRouter()


class ChatRequestModel(BaseModel):
    """Chat request model"""
    messages: List[dict]
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7
    provider: Optional[str] = None


class ChatResponseModel(BaseModel):
    """Chat response model"""
    content: str
    model: str
    usage: dict
    provider: str


def get_provider(settings: Settings = Depends(get_settings), provider_name: Optional[str] = None):
    """Get model provider"""
    provider_type = provider_name or settings.default_provider
    
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
    elif provider_type == "google":
        config = {
            "project_id": settings.google_project_id,
            "location": settings.google_location,
        }
    elif provider_type == "aws":
        config = {
            "region": settings.aws_region,
            "access_key_id": settings.aws_access_key_id,
            "secret_access_key": settings.aws_secret_access_key,
            "model": settings.aws_bedrock_model,
        }
    
    return ProviderFactory.create_provider(provider_type, config)


@router.post("/chat", response_model=ChatResponseModel)
async def chat_completion(
    request: ChatRequestModel,
    settings: Settings = Depends(get_settings),
):
    """Chat completion endpoint"""
    try:
        provider = get_provider(settings, request.provider)
        
        messages = [Message(role=msg["role"], content=msg["content"]) for msg in request.messages]
        
        chat_request = ChatRequest(
            messages=messages,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
        )
        
        response = await provider.chat(chat_request)
        
        return ChatResponseModel(
            content=response.content,
            model=response.model,
            usage=response.usage,
            provider=provider.provider_name,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
