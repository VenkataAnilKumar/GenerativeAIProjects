"""
Quality Evaluation Framework
LLM-as-judge scoring, benchmark test cases, and feedback collection.
"""

import json
import time
import sqlite3
from typing import Dict, Optional, List, Callable
from pathlib import Path
from datetime import datetime


class QualityScorer:
    """
    Evaluate AI output quality using rule-based and LLM-based scoring.
    
    Usage:
        scorer = QualityScorer()
        score = scorer.evaluate(
            prompt="Write an email about CloudSync",
            response="Dear Customer, ...",
            criteria=["relevance", "clarity", "engagement"]
        )
    """

    # Scoring rubrics
    CRITERIA = {
        "relevance": "How relevant is the response to the prompt?",
        "clarity": "How clear and well-structured is the response?",
        "engagement": "How engaging and compelling is the content?",
        "accuracy": "How factually accurate is the response?",
        "completeness": "Does the response fully address the prompt?",
        "safety": "Is the response free from harmful content?",
        "creativity": "How creative and original is the response?",
    }

    def __init__(self):
        self.evaluations: List[Dict] = []

    def evaluate(self, prompt: str, response: str,
                 criteria: List[str] = None) -> Dict:
        """
        Score a response using rule-based analysis.
        Returns scores per criterion (0-10) and overall score.
        """
        if criteria is None:
            criteria = ["relevance", "clarity", "completeness"]

        scores = {}
        for criterion in criteria:
            scores[criterion] = self._score_criterion(
                prompt, response, criterion
            )

        overall = sum(scores.values()) / len(scores) if scores else 0

        result = {
            "overall_score": round(overall, 2),
            "criteria_scores": scores,
            "response_length": len(response),
            "timestamp": datetime.utcnow().isoformat(),
        }

        self.evaluations.append(result)
        return result

    def _score_criterion(self, prompt: str, response: str,
                         criterion: str) -> float:
        """Score a single criterion using heuristics."""
        score = 5.0  # Baseline

        if criterion == "relevance":
            # Check keyword overlap
            prompt_words = set(prompt.lower().split())
            response_words = set(response.lower().split())
            overlap = len(prompt_words & response_words)
            score += min(overlap * 0.5, 3.0)
            if len(response) < 20:
                score -= 2.0

        elif criterion == "clarity":
            # Check structure (paragraphs, sentences)
            sentences = response.count(".") + response.count("!") + response.count("?")
            paragraphs = response.count("\n\n") + 1
            if sentences >= 3:
                score += 1.5
            if paragraphs >= 2:
                score += 1.0
            # Penalize very long sentences (avg > 30 words)
            words = len(response.split())
            if sentences > 0 and words / sentences > 30:
                score -= 1.0

        elif criterion == "completeness":
            # Check response length relative to prompt
            if len(response) > len(prompt) * 2:
                score += 2.0
            elif len(response) > len(prompt):
                score += 1.0
            else:
                score -= 1.0

        elif criterion == "engagement":
            # Check for engaging elements
            engaging_markers = ["!", "?", "you", "your", "imagine",
                                "discover", "exciting", "amazing"]
            for marker in engaging_markers:
                if marker.lower() in response.lower():
                    score += 0.3

        elif criterion == "safety":
            # Check for harmful content
            score = 9.0  # High baseline
            unsafe_words = ["hack", "exploit", "steal", "illegal",
                            "weapon", "dangerous", "kill"]
            for word in unsafe_words:
                if word in response.lower():
                    score -= 2.0

        elif criterion == "accuracy":
            # Can't truly judge without ground truth; moderate score
            score = 6.0
            if "I'm not sure" in response or "I don't know" in response:
                score += 1.0  # Honesty bonus

        elif criterion == "creativity":
            # Check vocabulary diversity
            words = response.lower().split()
            unique = len(set(words))
            if len(words) > 0:
                diversity = unique / len(words)
                score += diversity * 4

        return round(max(0, min(10, score)), 2)


class BenchmarkSuite:
    """
    Run benchmark test cases against use case implementations.
    
    Usage:
        bench = BenchmarkSuite()
        bench.add_case("marketing", "email",
                        input={"product": "Test"},
                        expected_keys=["subject", "body"])
        results = bench.run_all(generate_fn)
    """

    def __init__(self):
        self.test_cases: List[Dict] = []
        self.results: List[Dict] = []

    def add_case(self, use_case: str, name: str,
                 input_data: Dict, expected_keys: List[str] = None,
                 validation_fn: Callable = None):
        """Add a benchmark test case."""
        self.test_cases.append({
            "use_case": use_case,
            "name": name,
            "input": input_data,
            "expected_keys": expected_keys or [],
            "validation_fn": validation_fn,
        })

    def run_all(self, execute_fn: Callable) -> Dict:
        """Run all test cases and return results."""
        self.results = []
        passed = 0
        failed = 0

        for case in self.test_cases:
            start = time.time()
            try:
                output = execute_fn(case["use_case"], **case["input"])
                latency = (time.time() - start) * 1000

                # Check expected keys
                key_check = all(
                    k in output for k in case["expected_keys"]
                ) if case["expected_keys"] else True

                # Run custom validation
                custom_check = True
                if case["validation_fn"]:
                    custom_check = case["validation_fn"](output)

                success = key_check and custom_check
                if success:
                    passed += 1
                else:
                    failed += 1

                self.results.append({
                    "case": case["name"],
                    "status": "PASS" if success else "FAIL",
                    "latency_ms": round(latency, 2),
                    "key_check": key_check,
                    "custom_check": custom_check,
                })

            except Exception as e:
                failed += 1
                self.results.append({
                    "case": case["name"],
                    "status": "ERROR",
                    "error": str(e),
                })

        return {
            "total": len(self.test_cases),
            "passed": passed,
            "failed": failed,
            "pass_rate": f"{(passed / len(self.test_cases) * 100):.1f}%"
                if self.test_cases else "0%",
            "results": self.results,
        }


class FeedbackCollector:
    """
    Collect and store user feedback on AI outputs.
    
    Usage:
        feedback = FeedbackCollector()
        feedback.record("req_123", rating=4, comment="Good but too verbose")
        summary = feedback.get_summary()
    """

    def __init__(self, db_path: str = "feedback.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id TEXT NOT NULL,
                use_case TEXT,
                rating INTEGER CHECK(rating BETWEEN 1 AND 5),
                thumbs TEXT CHECK(thumbs IN ('up', 'down')),
                comment TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    def record(self, request_id: str, use_case: str = "",
               rating: int = None, thumbs: str = None,
               comment: str = ""):
        """Record user feedback."""
        self.conn.execute("""
            INSERT INTO feedback (request_id, use_case, rating, thumbs, comment)
            VALUES (?, ?, ?, ?, ?)
        """, (request_id, use_case, rating, thumbs, comment))
        self.conn.commit()

    def get_summary(self, use_case: Optional[str] = None) -> Dict:
        """Get feedback summary."""
        where = "WHERE use_case = ?" if use_case else ""
        params = (use_case,) if use_case else ()

        cursor = self.conn.execute(f"""
            SELECT
                COUNT(*) as total,
                AVG(rating) as avg_rating,
                SUM(CASE WHEN thumbs = 'up' THEN 1 ELSE 0 END) as thumbs_up,
                SUM(CASE WHEN thumbs = 'down' THEN 1 ELSE 0 END) as thumbs_down
            FROM feedback {where}
        """, params)

        row = cursor.fetchone()
        return dict(row) if row else {}

    def close(self):
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
