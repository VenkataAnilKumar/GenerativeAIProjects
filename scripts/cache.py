"""
Caching Layer
Provides in-memory and Redis-compatible caching with TTL support.
Falls back to in-memory dict if Redis is unavailable.
"""

import json
import hashlib
import time
from typing import Optional, Any, Dict
from functools import wraps


class InMemoryCache:
    """
    Simple in-memory cache with TTL support.
    Used when Redis is not available.
    """

    def __init__(self):
        self._store: Dict[str, Dict] = {}

    def get(self, key: str) -> Optional[Any]:
        """Get a cached value by key."""
        entry = self._store.get(key)
        if entry is None:
            return None
        
        if entry["expires_at"] and time.time() > entry["expires_at"]:
            del self._store[key]
            return None
        
        entry["hits"] += 1
        return entry["value"]

    def set(self, key: str, value: Any, ttl: int = 3600):
        """Set a cached value with TTL (seconds)."""
        self._store[key] = {
            "value": value,
            "expires_at": time.time() + ttl if ttl > 0 else None,
            "created_at": time.time(),
            "hits": 0,
        }

    def delete(self, key: str) -> bool:
        """Delete a cached entry."""
        return self._store.pop(key, None) is not None

    def clear(self):
        """Clear all cached entries."""
        self._store.clear()

    def stats(self) -> Dict:
        """Get cache statistics."""
        now = time.time()
        active = {k: v for k, v in self._store.items()
                  if not v["expires_at"] or v["expires_at"] > now}
        total_hits = sum(v["hits"] for v in active.values())
        return {
            "total_entries": len(active),
            "total_hits": total_hits,
            "memory_keys": list(active.keys())[:10],
        }


class RedisCache:
    """
    Redis-backed cache.
    Requires: pip install redis
    """

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0,
                 prefix: str = "genai:"):
        import redis
        self.client = redis.Redis(host=host, port=port, db=db,
                                  decode_responses=True)
        self.prefix = prefix

    def get(self, key: str) -> Optional[Any]:
        """Get cached value from Redis."""
        raw = self.client.get(f"{self.prefix}{key}")
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return raw

    def set(self, key: str, value: Any, ttl: int = 3600):
        """Set cached value in Redis."""
        serialized = json.dumps(value) if not isinstance(value, str) else value
        if ttl > 0:
            self.client.setex(f"{self.prefix}{key}", ttl, serialized)
        else:
            self.client.set(f"{self.prefix}{key}", serialized)

    def delete(self, key: str) -> bool:
        """Delete cached entry from Redis."""
        return bool(self.client.delete(f"{self.prefix}{key}"))

    def clear(self):
        """Clear all entries with our prefix."""
        for key in self.client.scan_iter(f"{self.prefix}*"):
            self.client.delete(key)

    def stats(self) -> Dict:
        """Get Redis cache statistics."""
        info = self.client.info("memory")
        keys = list(self.client.scan_iter(f"{self.prefix}*", count=10))
        return {
            "total_entries": len(keys),
            "used_memory": info.get("used_memory_human", "unknown"),
            "sample_keys": [k.replace(self.prefix, "") for k in keys[:10]],
        }


def get_cache(use_redis: bool = True) -> Any:
    """Factory: return best available cache backend."""
    if use_redis:
        try:
            cache = RedisCache()
            cache.client.ping()
            return cache
        except Exception:
            pass
    return InMemoryCache()


# ─── Caching Utilities ───────────────────────────────────────

def make_cache_key(*args, **kwargs) -> str:
    """Generate a deterministic cache key from arguments."""
    raw = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def cached(ttl: int = 3600, prefix: str = "fn"):
    """
    Decorator to cache function results.
    
    Usage:
        @cached(ttl=600, prefix="marketing")
        def generate_email(product, tone):
            # Expensive LLM call
            return result
    """
    _cache = InMemoryCache()

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = f"{prefix}:{func.__name__}:{make_cache_key(*args, **kwargs)}"
            
            cached_result = _cache.get(key)
            if cached_result is not None:
                return cached_result
            
            result = func(*args, **kwargs)
            _cache.set(key, result, ttl=ttl)
            return result
        
        wrapper.cache = _cache
        wrapper.cache_clear = lambda: _cache.clear()
        return wrapper
    return decorator


class EmbeddingCache:
    """
    Specialized cache for embeddings to avoid re-computing.
    
    Usage:
        cache = EmbeddingCache()
        embedding = cache.get_or_compute("hello world", embed_fn)
    """

    def __init__(self, backend=None):
        self.cache = backend or InMemoryCache()
        self.hits = 0
        self.misses = 0

    def get_or_compute(self, text: str, embed_fn, ttl: int = 86400):
        """Get cached embedding or compute and cache it."""
        key = f"emb:{make_cache_key(text)}"
        
        cached = self.cache.get(key)
        if cached is not None:
            self.hits += 1
            return cached
        
        self.misses += 1
        embedding = embed_fn(text)
        self.cache.set(key, embedding, ttl=ttl)
        return embedding

    def stats(self) -> Dict:
        """Get embedding cache statistics."""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{hit_rate:.1f}%",
            **self.cache.stats(),
        }
