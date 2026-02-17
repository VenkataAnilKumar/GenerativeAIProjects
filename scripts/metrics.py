"""
Metrics Collection and Cost Tracking
Tracks token usage, costs, and performance across all use cases.
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path


class MetricsCollector:
    """
    SQLite-based metrics collector for tracking AI usage and costs.
    
    Usage:
        metrics = MetricsCollector()
        metrics.track_request(
            use_case="marketing",
            model="gpt-4",
            tokens=150,
            cost=0.003,
            latency_ms=1200
        )
        
        report = metrics.get_daily_summary()
    """

    def __init__(self, db_path: str = "metrics.db"):
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self):
        """Initialize database schema."""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                use_case TEXT NOT NULL,
                model TEXT,
                mode TEXT DEFAULT 'demo',
                tokens INTEGER DEFAULT 0,
                cost REAL DEFAULT 0.0,
                latency_ms REAL DEFAULT 0.0,
                success BOOLEAN DEFAULT 1,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON requests(timestamp)
        """)
        
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_use_case 
            ON requests(use_case)
        """)
        
        self.conn.commit()

    def track_request(
        self,
        use_case: str,
        model: str = "unknown",
        mode: str = "demo",
        tokens: int = 0,
        cost: float = 0.0,
        latency_ms: float = 0.0,
        success: bool = True,
    ):
        """Record a completed request."""
        self.conn.execute("""
            INSERT INTO requests (use_case, model, mode, tokens, cost, latency_ms, success)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (use_case, model, mode, tokens, cost, latency_ms, success))
        self.conn.commit()

    def get_daily_summary(self, date: Optional[str] = None) -> Dict:
        """Get summary for a specific date (defaults to today)."""
        if date is None:
            date = datetime.utcnow().date().isoformat()
        
        cursor = self.conn.execute("""
            SELECT 
                COUNT(*) as total_requests,
                SUM(tokens) as total_tokens,
                SUM(cost) as total_cost,
                AVG(latency_ms) as avg_latency_ms,
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful,
                SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failed
            FROM requests
            WHERE DATE(timestamp) = ?
        """, (date,))
        
        row = cursor.fetchone()
        return dict(row) if row else {}

    def get_summary_by_use_case(self, days: int = 7) -> List[Dict]:
        """Get usage breakdown by use case for the last N days."""
        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
        
        cursor = self.conn.execute("""
            SELECT 
                use_case,
                COUNT(*) as requests,
                SUM(tokens) as tokens,
                SUM(cost) as cost,
                AVG(latency_ms) as avg_latency_ms
            FROM requests
            WHERE timestamp >= ?
            GROUP BY use_case
            ORDER BY cost DESC
        """, (cutoff,))
        
        return [dict(row) for row in cursor.fetchall()]

    def get_cost_projection(self, days_ahead: int = 30) -> float:
        """Project monthly cost based on recent usage."""
        summary = self.get_daily_summary()
        daily_cost = summary.get("total_cost", 0.0) or 0.0
        return daily_cost * days_ahead

    def export_to_json(self, days: int = 7) -> str:
        """Export recent metrics as JSON."""
        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
        
        cursor = self.conn.execute("""
            SELECT * FROM requests
            WHERE timestamp >= ?
            ORDER BY timestamp DESC
        """, (cutoff,))
        
        records = [dict(row) for row in cursor.fetchall()]
        return json.dumps(records, indent=2)

    def close(self):
        """Close database connection."""
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# ─── Cost Estimation Helpers ───────────────────────────────

# Pricing as of 2024 (per 1K tokens)
MODEL_COSTS = {
    "gpt-4": {"input": 0.03, "output": 0.06},
    "gpt-4-turbo": {"input": 0.01, "output": 0.03},
    "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
    "claude-v2": {"input": 0.008, "output": 0.024},
    "claude-instant": {"input": 0.00163, "output": 0.00551},
    "gemini-pro": {"input": 0.00025, "output": 0.0005},
}


def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Estimate cost for a request."""
    if model not in MODEL_COSTS:
        return 0.0
    
    pricing = MODEL_COSTS[model]
    input_cost = (input_tokens / 1000) * pricing["input"]
    output_cost = (output_tokens / 1000) * pricing["output"]
    return input_cost + output_cost
