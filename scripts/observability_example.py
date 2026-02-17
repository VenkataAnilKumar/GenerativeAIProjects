"""
Example integration of logging and metrics into a use case.
This shows how to instrument use cases with observability.
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from scripts.logger import get_logger
from scripts.metrics import MetricsCollector, estimate_cost

# Example: Use Case 01 - Marketing Content
def generate_with_observability(content_type, **kwargs):
    """
    Instrumented version of generate() function.
    Adds logging and metrics tracking.
    """
    # Initialize observability
    logger = get_logger("marketing_content")
    metrics = MetricsCollector()
    
    # Start request
    request_id = logger.log_request(
        prompt=kwargs.get("product", ""),
        mode="demo",
        metadata={"content_type": content_type}
    )
    
    start_time = time.time()
    success = True
    tokens_used = 0
    error_msg = None
    
    try:
        # Your existing generation logic here
        # result = generate_content_demo(content_type, **kwargs)
        result = {
            "content": "Sample generated content",
            "tokens_used": 150,
            "model": "gpt-3.5-turbo",
        }
        
        tokens_used = result.get("tokens_used", 0)
        
    except Exception as e:
        success = False
        error_msg = str(e)
        logger.log_error(request_id, error_msg)
        raise
    
    finally:
        # Calculate metrics
        latency_ms = (time.time() - start_time) * 1000
        cost = estimate_cost("gpt-3.5-turbo", tokens_used // 2, tokens_used // 2)
        
        # Log response
        logger.log_response(
            request_id=request_id,
            tokens=tokens_used,
            cost=cost,
            latency_ms=latency_ms,
            success=success,
            error=error_msg,
        )
        
        # Track metrics
        metrics.track_request(
            use_case="marketing_content",
            model="gpt-3.5-turbo",
            mode="demo",
            tokens=tokens_used,
            cost=cost,
            latency_ms=latency_ms,
            success=success,
        )
        
        metrics.close()
    
    return result


if __name__ == "__main__":
    # Demo usage
    print("=== Testing Observability ===\n")
    
    result = generate_with_observability(
        "email",
        product="Test Product",
        audience="Developers",
    )
    
    print(f"\nGenerated: {result['content']}")
    
    # Show metrics
    metrics = MetricsCollector()
    summary = metrics.get_daily_summary()
    print(f"\n=== Today's Metrics ===")
    print(f"Total requests: {summary.get('total_requests', 0)}")
    print(f"Total cost: ${summary.get('total_cost', 0):.4f}")
    print(f"Avg latency: {summary.get('avg_latency_ms', 0):.0f}ms")
    metrics.close()
