# Testing Guide

## Overview

This guide covers how to run tests for the GenAI Platform.

## Prerequisites

```bash
# Install test dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## Running Tests

### All Tests

```bash
# Run all tests
pytest

# With coverage
pytest --cov=src --cov-report=html

# Using Makefile
make test
```

### Specific Test Suites

```bash
# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# Specific test file
pytest tests/unit/test_providers.py -v

# Specific test function
pytest tests/unit/test_api.py::test_health_check -v
```

## Test Markers

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

## Testing with Docker

```bash
# Run tests in Docker container
docker-compose run --rm api pytest tests/ -v

# With coverage
docker-compose run --rm api pytest tests/ --cov=src --cov-report=html
```

## Writing Tests

### Unit Tests

Place in `tests/unit/`:

```python
import pytest
from src.models.factory import ProviderFactory

def test_provider_creation():
    """Test creating a provider"""
    config = {"api_key": "test-key"}
    provider = ProviderFactory.create_provider("openai", config)
    assert provider is not None
```

### Integration Tests

Place in `tests/integration/`:

```python
import pytest
from fastapi.testclient import TestClient
from src.api.main import app

@pytest.mark.integration
def test_chat_endpoint():
    """Test chat endpoint integration"""
    client = TestClient(app)
    response = client.post("/api/v1/chat", json={
        "messages": [{"role": "user", "content": "Hello"}]
    })
    assert response.status_code == 200
```

### Async Tests

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    """Test async function"""
    result = await some_async_function()
    assert result is not None
```

## Mocking

### Mock External APIs

```python
from unittest.mock import patch, AsyncMock

@patch('src.models.openai_provider.AsyncOpenAI')
async def test_with_mock(mock_openai):
    """Test with mocked OpenAI"""
    mock_openai.return_value.chat.completions.create = AsyncMock(
        return_value=mock_response
    )
    # Test code here
```

## Coverage Reports

```bash
# Generate HTML coverage report
pytest --cov=src --cov-report=html

# View report
open htmlcov/index.html

# Terminal report with missing lines
pytest --cov=src --cov-report=term-missing
```

## Continuous Integration

Tests run automatically on:
- Pull requests
- Push to main/develop branches
- Manual workflow dispatch

See `.github/workflows/ci-cd.yml` for CI configuration.

## Troubleshooting

### Import Errors

```bash
# Ensure PYTHONPATH is set
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or install package in development mode
pip install -e .
```

### Missing Dependencies

```bash
# Install all dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Database Tests

```bash
# Start test database
docker-compose up -d postgres

# Run tests
pytest tests/integration/ -v

# Cleanup
docker-compose down
```

## Test Structure

```
tests/
├── unit/                 # Unit tests (fast, isolated)
│   ├── test_api.py
│   ├── test_providers.py
│   ├── test_services.py
│   └── test_utils.py
├── integration/          # Integration tests (slower, external deps)
│   ├── test_api_integration.py
│   ├── test_rag_pipeline.py
│   └── test_vector_stores.py
├── fixtures/             # Shared test fixtures
│   └── conftest.py
└── conftest.py          # Root conftest
```

## Best Practices

1. **Test Naming**: Use descriptive names (`test_should_return_error_when_invalid_input`)
2. **One Assertion**: Prefer one logical assertion per test
3. **Arrange-Act-Assert**: Structure tests clearly
4. **Mock External**: Mock external APIs and services
5. **Fast Tests**: Keep unit tests fast (< 1s each)
6. **Clean Up**: Use fixtures for setup/teardown
7. **Test Coverage**: Aim for >80% coverage

## Example Test File

```python
"""Tests for chat service"""
import pytest
from unittest.mock import AsyncMock, patch
from src.services.chat_service import ChatService

@pytest.fixture
def mock_provider():
    """Create mock provider"""
    provider = AsyncMock()
    provider.chat.return_value = {
        "content": "Test response",
        "usage": {"total_tokens": 10}
    }
    return provider

@pytest.mark.unit
async def test_chat_service_success(mock_provider):
    """Test successful chat"""
    service = ChatService(mock_provider)
    result = await service.chat("Hello")
    
    assert result["content"] == "Test response"
    assert result["usage"]["total_tokens"] == 10
    mock_provider.chat.assert_called_once()

@pytest.mark.unit
async def test_chat_service_error(mock_provider):
    """Test chat service error handling"""
    mock_provider.chat.side_effect = Exception("API Error")
    service = ChatService(mock_provider)
    
    with pytest.raises(Exception) as exc:
        await service.chat("Hello")
    assert "API Error" in str(exc.value)
```

## Quick Commands

```bash
# Quick test run
pytest -x  # Stop on first failure

# Verbose output
pytest -v  # Verbose
pytest -vv # Very verbose

# Show print statements
pytest -s

# Run last failed tests
pytest --lf

# Run with parallel execution
pytest -n auto  # Requires pytest-xdist
```
