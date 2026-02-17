"""Unit tests for scripts/config.py"""

import pytest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from scripts.config import is_demo, is_dev, get_config_summary, MODE


class TestConfigModule:
    """Test suite for configuration module."""

    def test_demo_mode_default(self, demo_mode):
        """Test that demo mode is detected correctly."""
        assert is_demo() is True
        assert is_dev() is False

    def test_mode_environment_variable(self):
        """Test MODE reads from environment."""
        original = os.environ.get("RUN_MODE")
        os.environ["RUN_MODE"] = "dev"
        
        # Reimport to pick up new env var
        import importlib
        import scripts.config as config
        importlib.reload(config)
        
        assert config.MODE == "dev"
        
        # Restore
        if original:
            os.environ["RUN_MODE"] = original
        else:
            os.environ.pop("RUN_MODE", None)
        importlib.reload(config)

    def test_config_summary_structure(self):
        """Test get_config_summary returns expected keys."""
        summary = get_config_summary()
        
        assert isinstance(summary, dict)
        assert "mode" in summary
        assert "azure_configured" in summary
        assert "aws_configured" in summary
        assert "gcp_configured" in summary
        assert "openai_configured" in summary

    def test_config_summary_bool_values(self):
        """Test config summary has boolean values for configured flags."""
        summary = get_config_summary()
        
        assert isinstance(summary["azure_configured"], bool)
        assert isinstance(summary["aws_configured"], bool)
        assert isinstance(summary["gcp_configured"], bool)
        assert isinstance(summary["openai_configured"], bool)

    def test_azure_configuration_detection(self):
        """Test Azure configuration is detected when endpoint is set."""
        original = os.environ.get("AZURE_OPENAI_ENDPOINT")
        
        # Test with endpoint
        os.environ["AZURE_OPENAI_ENDPOINT"] = "https://test.openai.azure.com/"
        import importlib
        import scripts.config as config
        importlib.reload(config)
        summary = config.get_config_summary()
        assert summary["azure_configured"] is True
        
        # Test without endpoint
        os.environ["AZURE_OPENAI_ENDPOINT"] = ""
        importlib.reload(config)
        summary = config.get_config_summary()
        assert summary["azure_configured"] is False
        
        # Restore
        if original:
            os.environ["AZURE_OPENAI_ENDPOINT"] = original
        else:
            os.environ.pop("AZURE_OPENAI_ENDPOINT", None)
        importlib.reload(config)


@pytest.mark.unit
def test_is_demo_function():
    """Test is_demo helper function."""
    # Should work without fixture too
    result = is_demo()
    assert isinstance(result, bool)


@pytest.mark.unit
def test_is_dev_function():
    """Test is_dev helper function."""
    result = is_dev()
    assert isinstance(result, bool)
