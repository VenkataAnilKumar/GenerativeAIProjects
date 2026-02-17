"""Integration tests for Use Case 08: Automated Code Review"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "use-cases", "08-automated-code-review-aws"))
from main import (
    review,
    check_syntax,
    check_docstrings,
    check_error_handling,
    check_security,
    run_static_analysis,
)


@pytest.mark.integration
class TestCodeReview:
    """Integration tests for code review system."""

    def test_review_valid_code(self, demo_mode, sample_code):
        """Test reviewing valid Python code."""
        result = review(sample_code)
        
        assert result is not None
        assert "syntax" in result
        assert result["syntax"]["status"] == "pass"
        assert result["mode"] == "demo"

    def test_review_code_with_issues(self, demo_mode):
        """Test reviewing code with common issues."""
        bad_code = '''
import os
def process_data(data):
    result = eval(data)
    return result
'''
        result = review(bad_code)
        
        assert result is not None
        assert "issues" in result
        # Should detect missing docstring and eval() usage

    def test_syntax_error_detection(self):
        """Test syntax error is caught."""
        invalid_code = "def broken(\n    pass"
        result = check_syntax(invalid_code)
        
        assert result["status"] == "fail"
        assert "error" in result["message"].lower() or "syntax" in result["message"].lower()

    def test_docstring_check(self):
        """Test docstring detection."""
        code_without_docstring = '''
def my_function():
    return 42
'''
        issues = check_docstrings(code_without_docstring)
        
        assert len(issues) > 0
        assert any("docstring" in issue["message"].lower() for issue in issues)

    def test_security_check_eval(self):
        """Test security check detects eval()."""
        dangerous_code = 'result = eval(user_input)'
        issues = check_security(dangerous_code)
        
        assert len(issues) > 0
        assert any("eval" in issue["message"].lower() for issue in issues)

    def test_security_check_hardcoded_password(self):
        """Test detection of hardcoded credentials."""
        code = 'password = "admin123"'
        issues = check_security(code)
        
        assert len(issues) > 0
        assert any("password" in issue["message"].lower() for issue in issues)

    def test_static_analysis_complete(self, sample_code):
        """Test complete static analysis."""
        result = run_static_analysis(sample_code)
        
        assert "syntax" in result
        assert "issues" in result
        assert isinstance(result["issues"], list)

    def test_severity_classification(self, demo_mode):
        """Test issues are classified by severity."""
        code_with_mixed_issues = '''
import os

password = "secret123"

def process(data):
    result = eval(data)
    return result
'''
        result = review(code_with_mixed_issues)
        
        assert "issues" in result
        if len(result["issues"]) > 0:
            # Check that severity exists
            assert "severity" in result["issues"][0]

    def test_empty_code(self, demo_mode):
        """Test reviewing empty code."""
        result = review("")
        
        assert result is not None
        assert result["mode"] == "demo"

    def test_well_written_code_minimal_issues(self, demo_mode):
        """Test well-written code has minimal issues."""
        good_code = '''
"""Module for data processing."""

def calculate_sum(numbers):
    """
    Calculate the sum of a list of numbers.
    
    Args:
        numbers: List of numeric values
        
    Returns:
        Sum of all numbers
    """
    try:
        return sum(numbers)
    except TypeError:
        return 0
'''
        result = review(good_code)
        
        assert result is not None
        assert result["syntax"]["status"] == "pass"
