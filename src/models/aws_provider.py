"""AWS Bedrock model provider implementation"""
from typing import Dict, Any, AsyncIterator
import json
import boto3
from .base import (
    BaseModelProvider, CompletionRequest, ChatRequest, 
    EmbeddingRequest, MultimodalRequest, ModelResponse, EmbeddingResponse
)


class AWSBedrockProvider(BaseModelProvider):
    """AWS Bedrock model provider"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        self.client = boto3.client(
            'bedrock-runtime',
            region_name=config.get("region", "us-east-1"),
            aws_access_key_id=config.get("access_key_id"),
            aws_secret_access_key=config.get("secret_access_key"),
        )
        self.model_id = config.get("model", "anthropic.claude-v2")
    
    async def complete(self, request: CompletionRequest) -> ModelResponse:
        """Generate text completion"""
        body = json.dumps({
            "prompt": f"\n\nHuman: {request.prompt}\n\nAssistant:",
            "max_tokens_to_sample": request.max_tokens,
            "temperature": request.temperature,
            "top_p": request.top_p,
        })
        
        response = self.client.invoke_model(
            modelId=self.model_id,
            body=body,
        )
        
        response_body = json.loads(response['body'].read())
        
        return ModelResponse(
            content=response_body['completion'],
            model=self.model_id,
            usage={
                "prompt_tokens": 0,  # Bedrock doesn't provide token counts
                "completion_tokens": 0,
                "total_tokens": 0,
            },
            finish_reason=response_body.get('stop_reason'),
        )
    
    async def chat(self, request: ChatRequest) -> ModelResponse:
        """Generate chat completion"""
        # Convert messages to Anthropic format
        prompt = "\n\n"
        for msg in request.messages:
            role = "Human" if msg.role == "user" else "Assistant"
            prompt += f"{role}: {msg.content}\n\n"
        prompt += "Assistant:"
        
        body = json.dumps({
            "prompt": prompt,
            "max_tokens_to_sample": request.max_tokens,
            "temperature": request.temperature,
            "top_p": request.top_p,
        })
        
        response = self.client.invoke_model(
            modelId=self.model_id,
            body=body,
        )
        
        response_body = json.loads(response['body'].read())
        
        return ModelResponse(
            content=response_body['completion'],
            model=self.model_id,
            usage={
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
            },
            finish_reason=response_body.get('stop_reason'),
        )
    
    async def stream_chat(self, request: ChatRequest) -> AsyncIterator[str]:
        """Stream chat completion"""
        # Convert messages to Anthropic format
        prompt = "\n\n"
        for msg in request.messages:
            role = "Human" if msg.role == "user" else "Assistant"
            prompt += f"{role}: {msg.content}\n\n"
        prompt += "Assistant:"
        
        body = json.dumps({
            "prompt": prompt,
            "max_tokens_to_sample": request.max_tokens,
            "temperature": request.temperature,
            "top_p": request.top_p,
        })
        
        response = self.client.invoke_model_with_response_stream(
            modelId=self.model_id,
            body=body,
        )
        
        for event in response['body']:
            chunk = json.loads(event['chunk']['bytes'])
            if 'completion' in chunk:
                yield chunk['completion']
    
    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """Generate embeddings"""
        # Note: AWS Bedrock uses Amazon Titan for embeddings
        embeddings = []
        for text in request.texts:
            body = json.dumps({"inputText": text})
            response = self.client.invoke_model(
                modelId="amazon.titan-embed-text-v1",
                body=body,
            )
            response_body = json.loads(response['body'].read())
            embeddings.append(response_body['embedding'])
        
        return EmbeddingResponse(
            embeddings=embeddings,
            model="amazon.titan-embed-text-v1",
            usage={
                "prompt_tokens": 0,
                "total_tokens": 0,
            },
        )
    
    async def multimodal(self, request: MultimodalRequest) -> ModelResponse:
        """Generate multimodal inference"""
        # Note: Bedrock multimodal support varies by model
        prompt = f"\n\nHuman: {request.prompt}"
        if request.image_url:
            prompt += f" [Image: {request.image_url}]"
        prompt += "\n\nAssistant:"
        
        body = json.dumps({
            "prompt": prompt,
            "max_tokens_to_sample": request.max_tokens,
            "temperature": request.temperature,
        })
        
        response = self.client.invoke_model(
            modelId=self.model_id,
            body=body,
        )
        
        response_body = json.loads(response['body'].read())
        
        return ModelResponse(
            content=response_body['completion'],
            model=self.model_id,
            usage={
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
            },
            finish_reason=response_body.get('stop_reason'),
        )
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the model"""
        return {
            "provider": "aws",
            "model_id": self.model_id,
        }
