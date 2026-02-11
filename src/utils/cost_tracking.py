"""Cost tracking for LLM usage"""
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class UsageRecord(Base):
    """Database model for usage records"""
    __tablename__ = "usage_records"
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    provider = Column(String(50))
    model = Column(String(100))
    endpoint = Column(String(100))
    user_id = Column(String(100))
    prompt_tokens = Column(Integer)
    completion_tokens = Column(Integer)
    total_tokens = Column(Integer)
    estimated_cost = Column(Float)
    metadata = Column(JSON)


class CostTracker:
    """Track and calculate costs for LLM usage"""
    
    # Cost per 1K tokens (USD)
    PRICING = {
        "gpt-4": {
            "prompt": 0.03,
            "completion": 0.06,
        },
        "gpt-4-turbo": {
            "prompt": 0.01,
            "completion": 0.03,
        },
        "gpt-3.5-turbo": {
            "prompt": 0.0015,
            "completion": 0.002,
        },
        "claude-v2": {
            "prompt": 0.008,
            "completion": 0.024,
        },
        "claude-instant": {
            "prompt": 0.0008,
            "completion": 0.0024,
        },
        "gemini-pro": {
            "prompt": 0.00025,
            "completion": 0.0005,
        },
    }
    
    @classmethod
    def calculate_cost(
        cls,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
    ) -> float:
        """Calculate estimated cost"""
        pricing = cls.PRICING.get(model, {"prompt": 0.001, "completion": 0.002})
        
        prompt_cost = (prompt_tokens / 1000) * pricing["prompt"]
        completion_cost = (completion_tokens / 1000) * pricing["completion"]
        
        return prompt_cost + completion_cost
    
    @classmethod
    def track_usage(
        cls,
        provider: str,
        model: str,
        endpoint: str,
        prompt_tokens: int,
        completion_tokens: int,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> UsageRecord:
        """Create usage record"""
        cost = cls.calculate_cost(model, prompt_tokens, completion_tokens)
        
        return UsageRecord(
            provider=provider,
            model=model,
            endpoint=endpoint,
            user_id=user_id,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            estimated_cost=cost,
            metadata=metadata or {},
        )
