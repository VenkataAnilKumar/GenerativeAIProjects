"""Code completion endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from ...core.config import get_settings, Settings
from ...models.factory import ProviderFactory
from ...services.code_service import CodeCompletionService

router = APIRouter()


class CodeCompletionRequest(BaseModel):
    """Code completion request"""
    code: str
    language: str = "python"
    instruction: Optional[str] = None
    provider: Optional[str] = None


class CodeExplanationRequest(BaseModel):
    """Code explanation request"""
    code: str
    language: str = "python"
    provider: Optional[str] = None


class CodeFixRequest(BaseModel):
    """Code fix request"""
    code: str
    error: str
    language: str = "python"
    provider: Optional[str] = None


class CodeGenerationRequest(BaseModel):
    """Code generation request"""
    description: str
    language: str = "python"
    provider: Optional[str] = None


@router.post("/code/complete")
async def complete_code(
    request: CodeCompletionRequest,
    settings: Settings = Depends(get_settings),
):
    """Code completion endpoint"""
    try:
        provider_type = request.provider or settings.default_provider
        config = {
            "api_key": settings.openai_api_key,
            "model": settings.openai_model,
        }
        provider = ProviderFactory.create_provider(provider_type, config)
        
        service = CodeCompletionService(provider)
        result = await service.complete_code(
            code=request.code,
            language=request.language,
            instruction=request.instruction,
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/code/explain")
async def explain_code(
    request: CodeExplanationRequest,
    settings: Settings = Depends(get_settings),
):
    """Code explanation endpoint"""
    try:
        provider_type = request.provider or settings.default_provider
        config = {
            "api_key": settings.openai_api_key,
            "model": settings.openai_model,
        }
        provider = ProviderFactory.create_provider(provider_type, config)
        
        service = CodeCompletionService(provider)
        result = await service.explain_code(
            code=request.code,
            language=request.language,
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/code/fix")
async def fix_code(
    request: CodeFixRequest,
    settings: Settings = Depends(get_settings),
):
    """Code fix endpoint"""
    try:
        provider_type = request.provider or settings.default_provider
        config = {
            "api_key": settings.openai_api_key,
            "model": settings.openai_model,
        }
        provider = ProviderFactory.create_provider(provider_type, config)
        
        service = CodeCompletionService(provider)
        result = await service.fix_code(
            code=request.code,
            error=request.error,
            language=request.language,
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/code/generate")
async def generate_code(
    request: CodeGenerationRequest,
    settings: Settings = Depends(get_settings),
):
    """Code generation endpoint"""
    try:
        provider_type = request.provider or settings.default_provider
        config = {
            "api_key": settings.openai_api_key,
            "model": settings.openai_model,
        }
        provider = ProviderFactory.create_provider(provider_type, config)
        
        service = CodeCompletionService(provider)
        result = await service.generate_code(
            description=request.description,
            language=request.language,
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
