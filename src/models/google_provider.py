"""Google Vertex AI model provider implementation"""
from typing import Dict, Any, AsyncIterator
from google.cloud import aiplatform
from vertexai.preview.generative_models import GenerativeModel
import vertexai
from .base import (
    BaseModelProvider, CompletionRequest, ChatRequest, 
    EmbeddingRequest, MultimodalRequest, ModelResponse, EmbeddingResponse
)


class GoogleVertexAIProvider(BaseModelProvider):
    """Google Vertex AI model provider"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        project_id = config.get("project_id")
        location = config.get("location", "us-central1")
        
        if not project_id:
            raise ValueError("Google Cloud project ID is required")
        
        vertexai.init(project=project_id, location=location)
        self.model_name = config.get("model", "gemini-pro")
        self.model = GenerativeModel(self.model_name)
    
    async def complete(self, request: CompletionRequest) -> ModelResponse:
        """Generate text completion"""
        response = self.model.generate_content(
            request.prompt,
            generation_config={
                "max_output_tokens": request.max_tokens,
                "temperature": request.temperature,
                "top_p": request.top_p,
            }
        )
        
        return ModelResponse(
            content=response.text,
            model=self.model_name,
            usage={
                "prompt_tokens": 0,  # Vertex AI doesn't always provide token counts
                "completion_tokens": 0,
                "total_tokens": 0,
            },
            metadata={"candidates": len(response.candidates)},
        )
    
    async def chat(self, request: ChatRequest) -> ModelResponse:
        """Generate chat completion"""
        chat = self.model.start_chat()
        
        # Send all messages except the last one as history
        for msg in request.messages[:-1]:
            chat.send_message(msg.content)
        
        # Send the last message and get response
        response = chat.send_message(
            request.messages[-1].content,
            generation_config={
                "max_output_tokens": request.max_tokens,
                "temperature": request.temperature,
                "top_p": request.top_p,
            }
        )
        
        return ModelResponse(
            content=response.text,
            model=self.model_name,
            usage={
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
            },
        )
    
    async def stream_chat(self, request: ChatRequest) -> AsyncIterator[str]:
        """Stream chat completion"""
        chat = self.model.start_chat()
        
        # Send all messages except the last one as history
        for msg in request.messages[:-1]:
            chat.send_message(msg.content)
        
        # Stream the last message
        responses = chat.send_message(
            request.messages[-1].content,
            generation_config={
                "max_output_tokens": request.max_tokens,
                "temperature": request.temperature,
                "top_p": request.top_p,
            },
            stream=True,
        )
        
        for response in responses:
            yield response.text
    
    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """Generate embeddings"""
        from vertexai.language_models import TextEmbeddingModel
        
        model = TextEmbeddingModel.from_pretrained("textembedding-gecko@003")
        embeddings = []
        
        for text in request.texts:
            embedding = model.get_embeddings([text])[0]
            embeddings.append(embedding.values)
        
        return EmbeddingResponse(
            embeddings=embeddings,
            model="textembedding-gecko@003",
            usage={
                "prompt_tokens": 0,
                "total_tokens": 0,
            },
        )
    
    async def multimodal(self, request: MultimodalRequest) -> ModelResponse:
        """Generate multimodal inference"""
        from vertexai.preview.generative_models import Image, Part
        
        multimodal_model = GenerativeModel("gemini-pro-vision")
        
        parts = [request.prompt]
        
        if request.image_url:
            # Download image from URL
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(request.image_url)
                image_bytes = response.content
            parts.append(Image.from_bytes(image_bytes))
        elif request.image_base64:
            import base64
            image_bytes = base64.b64decode(request.image_base64)
            parts.append(Image.from_bytes(image_bytes))
        
        response = multimodal_model.generate_content(
            parts,
            generation_config={
                "max_output_tokens": request.max_tokens,
                "temperature": request.temperature,
            }
        )
        
        return ModelResponse(
            content=response.text,
            model="gemini-pro-vision",
            usage={
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
            },
        )
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the model"""
        return {
            "provider": "google",
            "model": self.model_name,
        }
