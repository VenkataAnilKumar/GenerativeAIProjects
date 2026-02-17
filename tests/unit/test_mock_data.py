"""Unit tests for scripts/mock_data.py"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from scripts.mock_data import (
    MARKETING_RESPONSES,
    IMAGE_GENERATION_RESPONSE,
    CODE_COMPLETIONS,
    KNOWLEDGE_BASE,
    MEDICAL_REPORTS,
    LEARNING_CONTENT,
    CODE_REVIEW_RULES,
    LEGAL_CLAUSES,
    MANUFACTURING_DATA,
    simulate_latency,
)


@pytest.mark.unit
class TestMarketingResponses:
    """Test marketing content mock data."""

    def test_marketing_responses_structure(self):
        """Test marketing responses have expected keys."""
        assert "email" in MARKETING_RESPONSES
        assert "social_post" in MARKETING_RESPONSES
        assert "ad_copy" in MARKETING_RESPONSES

    def test_email_template_has_subject_and_body(self):
        """Test email template structure."""
        email = MARKETING_RESPONSES["email"]
        assert "subject" in email
        assert "body" in email
        assert "{product}" in email["subject"]
        assert "{product}" in email["body"]

    def test_social_post_has_placeholders(self):
        """Test social post has product placeholder."""
        social = MARKETING_RESPONSES["social_post"]
        assert "{product}" in social


@pytest.mark.unit
class TestImageGeneration:
    """Test image generation mock data."""

    def test_image_response_structure(self):
        """Test image response has required fields."""
        assert "status" in IMAGE_GENERATION_RESPONSE
        assert "image_id" in IMAGE_GENERATION_RESPONSE
        assert "model" in IMAGE_GENERATION_RESPONSE
        assert IMAGE_GENERATION_RESPONSE["status"] == "success"


@pytest.mark.unit
class TestCodeCompletions:
    """Test code completion mock data."""

    def test_code_completions_has_python(self):
        """Test Python completions exist."""
        assert "python" in CODE_COMPLETIONS
        assert "def " in CODE_COMPLETIONS["python"]
        assert "class " in CODE_COMPLETIONS["python"]


@pytest.mark.unit
class TestKnowledgeBase:
    """Test knowledge base mock data."""

    def test_knowledge_base_is_list(self):
        """Test knowledge base structure."""
        assert isinstance(KNOWLEDGE_BASE, list)
        assert len(KNOWLEDGE_BASE) > 0

    def test_knowledge_base_entries_have_required_fields(self):
        """Test each KB entry has id, topic, content."""
        for entry in KNOWLEDGE_BASE:
            assert "id" in entry
            assert "topic" in entry
            assert "content" in entry
            assert len(entry["content"]) > 0

    def test_knowledge_base_topics_are_unique(self):
        """Test knowledge base has unique topics."""
        topics = [entry["topic"] for entry in KNOWLEDGE_BASE]
        assert len(topics) == len(set(topics))


@pytest.mark.unit
class TestMedicalReports:
    """Test medical reports mock data."""

    def test_medical_reports_structure(self):
        """Test medical reports have required fields."""
        assert len(MEDICAL_REPORTS) > 0
        for report in MEDICAL_REPORTS:
            assert "id" in report
            assert "type" in report
            assert "report" in report
            assert "summary" in report

    def test_medical_report_types(self):
        """Test medical report types are valid."""
        valid_types = ["radiology", "pathology", "clinical"]
        for report in MEDICAL_REPORTS:
            assert report["type"] in valid_types


@pytest.mark.unit
class TestLearningContent:
    """Test learning content mock data."""

    def test_learning_content_has_algebra(self):
        """Test algebra content exists."""
        assert "algebra" in LEARNING_CONTENT

    def test_algebra_has_difficulty_levels(self):
        """Test algebra has beginner and advanced."""
        algebra = LEARNING_CONTENT["algebra"]
        assert "beginner" in algebra
        assert "advanced" in algebra

    def test_learning_content_structure(self):
        """Test learning content has required fields."""
        beginner = LEARNING_CONTENT["algebra"]["beginner"]
        assert "title" in beginner
        assert "objectives" in beginner
        assert "content" in beginner
        assert "exercises" in beginner
        assert isinstance(beginner["objectives"], list)
        assert isinstance(beginner["exercises"], list)


@pytest.mark.unit
class TestCodeReviewRules:
    """Test code review rules."""

    def test_code_review_rules_structure(self):
        """Test review rules have required fields."""
        assert len(CODE_REVIEW_RULES) > 0
        for rule in CODE_REVIEW_RULES:
            assert "rule" in rule
            assert "severity" in rule
            assert "message" in rule

    def test_severity_levels_are_valid(self):
        """Test severity levels are standard."""
        valid_severities = ["error", "warning", "info"]
        for rule in CODE_REVIEW_RULES:
            assert rule["severity"] in valid_severities


@pytest.mark.unit
class TestLegalClauses:
    """Test legal clauses mock data."""

    def test_legal_clauses_structure(self):
        """Test clauses have required fields."""
        assert len(LEGAL_CLAUSES) > 0
        for clause in LEGAL_CLAUSES:
            assert "id" in clause
            assert "type" in clause
            assert "text" in clause
            assert len(clause["text"]) > 50  # Substantial text


@pytest.mark.unit
class TestManufacturingData:
    """Test manufacturing simulation data."""

    def test_manufacturing_data_structure(self):
        """Test manufacturing data has required fields."""
        assert "production_lines" in MANUFACTURING_DATA
        assert "suppliers" in MANUFACTURING_DATA
        assert "cost_per_unit" in MANUFACTURING_DATA
        assert "daily_output" in MANUFACTURING_DATA

    def test_production_lines_structure(self):
        """Test production line entries."""
        lines = MANUFACTURING_DATA["production_lines"]
        assert len(lines) > 0
        for line in lines:
            assert "line" in line
            assert "capacity" in line
            assert "utilization" in line
            assert "defect_rate" in line
            assert 0 <= line["utilization"] <= 1
            assert 0 <= line["defect_rate"] <= 1


@pytest.mark.unit
def test_simulate_latency_runs():
    """Test simulate_latency function doesn't crash."""
    import time
    start = time.time()
    simulate_latency(0.01, 0.02)
    elapsed = time.time() - start
    assert 0.01 <= elapsed <= 0.05  # Some tolerance
