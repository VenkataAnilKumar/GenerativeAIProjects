"""Integration tests for Use Case 01: Marketing Content Generation"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "use-cases", "01-marketing-content-azure"))
from main import generate, build_prompt


@pytest.mark.integration
class TestMarketingContentGeneration:
    """Integration tests for marketing content generation."""

    def test_generate_email_demo_mode(self, demo_mode):
        """Test email generation in demo mode."""
        result = generate(
            "email",
            product="Test Product",
            audience="Marketing Professionals",
            tone="professional",
            benefits="Save time, increase ROI",
        )
        
        assert result is not None
        assert "subject" in result
        assert "body" in result
        assert result["mode"] == "demo"
        assert "Test Product" in result["subject"] or "Test Product" in result["body"]

    def test_generate_social_post_demo_mode(self, demo_mode):
        """Test social post generation in demo mode."""
        result = generate(
            "social_post",
            product="AI Platform",
            platform="LinkedIn",
            tone="professional yet friendly",
        )
        
        assert result is not None
        assert "content" in result
        assert result["mode"] == "demo"
        assert len(result["content"]) > 0

    def test_generate_ad_copy_demo_mode(self, demo_mode):
        """Test ad copy generation in demo mode."""
        result = generate(
            "ad_copy",
            product="CloudSync",
            pain_point="manual data management",
            usp="automated cloud sync",
            cta="Try free",
        )
        
        assert result is not None
        assert "content" in result
        assert result["mode"] == "demo"

    def test_build_prompt_email(self):
        """Test prompt building for email."""
        prompt = build_prompt(
            "email",
            product="Test Product",
            audience="Developers",
            tone="technical",
            benefits="API access, SDKs",
        )
        
        assert isinstance(prompt, str)
        assert "Test Product" in prompt
        assert "Developers" in prompt
        assert "email" in prompt.lower()

    def test_build_prompt_invalid_type(self):
        """Test prompt building with invalid content type."""
        with pytest.raises(ValueError, match="Unknown content type"):
            build_prompt("invalid_type", product="Test")

    def test_all_content_types_work(self, demo_mode):
        """Test all content types can be generated."""
        content_types = ["email", "social_post", "ad_copy"]
        
        for content_type in content_types:
            result = generate(
                content_type,
                product="Test",
                audience="All",
                tone="casual",
                platform="Twitter",
                benefits="value",
                pain_point="problem",
                usp="solution",
                cta="action",
            )
            assert result is not None
            assert result["mode"] == "demo"
