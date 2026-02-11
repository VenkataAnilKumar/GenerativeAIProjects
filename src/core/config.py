from pydantic_settings import BaseSettings
from typing import Optional, Literal
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings with environment-based configuration"""
    
    # Application
    app_name: str = "GenAI Platform"
    app_version: str = "0.1.0"
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = False
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api/v1"
    cors_origins: list[str] = ["*"]
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Model Providers
    default_provider: Literal["openai", "azure", "google", "aws"] = "openai"
    
    # OpenAI
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4"
    openai_embedding_model: str = "text-embedding-3-small"
    
    # Azure OpenAI
    azure_openai_api_key: Optional[str] = None
    azure_openai_endpoint: Optional[str] = None
    azure_openai_api_version: str = "2024-02-15-preview"
    azure_openai_deployment: Optional[str] = None
    
    # Google Vertex AI
    google_project_id: Optional[str] = None
    google_location: str = "us-central1"
    google_credentials_path: Optional[str] = None
    
    # AWS Bedrock
    aws_region: str = "us-east-1"
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_bedrock_model: str = "anthropic.claude-v2"
    
    # Vector Stores
    default_vector_store: Literal["pinecone", "weaviate", "qdrant", "chroma"] = "chroma"
    
    # Pinecone
    pinecone_api_key: Optional[str] = None
    pinecone_environment: Optional[str] = None
    pinecone_index_name: str = "genai-index"
    
    # Weaviate
    weaviate_url: Optional[str] = None
    weaviate_api_key: Optional[str] = None
    
    # Qdrant
    qdrant_url: Optional[str] = None
    qdrant_api_key: Optional[str] = None
    qdrant_collection_name: str = "genai-collection"
    
    # Chroma
    chroma_host: str = "localhost"
    chroma_port: int = 8001
    chroma_collection_name: str = "genai-collection"
    
    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/genai"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Celery
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"
    
    # Observability
    enable_prometheus: bool = True
    enable_opentelemetry: bool = True
    jaeger_endpoint: Optional[str] = None
    
    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
