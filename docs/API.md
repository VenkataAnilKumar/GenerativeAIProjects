# API Documentation

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

Currently using API key authentication. Include in header:

```
Authorization: Bearer <your-api-key>
```

## Endpoints

### Health Check

#### GET /health

Check service health status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "0.1.0",
  "environment": "production"
}
```

### Chat Completion

#### POST /chat

Generate chat completions using various LLM providers.

**Request:**
```json
{
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is the capital of France?"}
  ],
  "max_tokens": 100,
  "temperature": 0.7,
  "provider": "openai"
}
```

**Response:**
```json
{
  "content": "The capital of France is Paris.",
  "model": "gpt-4",
  "usage": {
    "prompt_tokens": 25,
    "completion_tokens": 8,
    "total_tokens": 33
  },
  "provider": "OpenAIProvider"
}
```

**Parameters:**
- `messages` (required): Array of message objects
- `max_tokens` (optional): Maximum tokens in response (default: 1000)
- `temperature` (optional): Sampling temperature 0-1 (default: 0.7)
- `provider` (optional): Provider to use (openai, azure, google, aws)

### Text Completion

#### POST /completion

Generate text completions.

**Request:**
```json
{
  "prompt": "Once upon a time",
  "max_tokens": 100,
  "temperature": 0.8
}
```

**Response:**
```json
{
  "content": "Once upon a time, in a faraway land...",
  "model": "gpt-4",
  "usage": {
    "prompt_tokens": 4,
    "completion_tokens": 50,
    "total_tokens": 54
  }
}
```

### Code Operations

#### POST /code/complete

Complete code snippets.

**Request:**
```json
{
  "code": "def fibonacci(n):\n    ",
  "language": "python",
  "instruction": "Complete this fibonacci function"
}
```

**Response:**
```json
{
  "completion": "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)",
  "model": "gpt-4",
  "usage": {...}
}
```

#### POST /code/explain

Explain code snippets.

**Request:**
```json
{
  "code": "list(map(lambda x: x**2, range(10)))",
  "language": "python"
}
```

**Response:**
```json
{
  "explanation": "This code creates a list of squares from 0 to 9...",
  "model": "gpt-4",
  "usage": {...}
}
```

#### POST /code/fix

Fix code with errors.

**Request:**
```json
{
  "code": "def add(a b):\n    return a + b",
  "error": "SyntaxError: invalid syntax",
  "language": "python"
}
```

**Response:**
```json
{
  "fixed_code": "def add(a, b):\n    return a + b",
  "model": "gpt-4",
  "usage": {...}
}
```

#### POST /code/generate

Generate code from description.

**Request:**
```json
{
  "description": "Create a function to calculate factorial",
  "language": "python"
}
```

**Response:**
```json
{
  "code": "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n-1)",
  "model": "gpt-4",
  "usage": {...}
}
```

### RAG Operations

#### POST /rag/documents

Add documents to the knowledge base.

**Request:**
```json
{
  "texts": [
    "Paris is the capital of France.",
    "London is the capital of the UK."
  ],
  "metadatas": [
    {"source": "geography", "topic": "capitals"},
    {"source": "geography", "topic": "capitals"}
  ]
}
```

**Response:**
```json
{
  "document_ids": ["doc-123", "doc-124"],
  "count": 2
}
```

#### POST /rag/query

Query the RAG system.

**Request:**
```json
{
  "question": "What is the capital of France?",
  "system_prompt": "You are a geography expert.",
  "filter_metadata": {"topic": "capitals"}
}
```

**Response:**
```json
{
  "answer": "The capital of France is Paris.",
  "sources": [
    {
      "content": "Paris is the capital of France.",
      "metadata": {"source": "geography", "topic": "capitals"},
      "score": 0.95
    }
  ],
  "model": "gpt-4",
  "usage": {...}
}
```

### Multimodal Operations

#### POST /multimodal

Generate multimodal inference (text + image).

**Request:**
```json
{
  "prompt": "What is in this image?",
  "image_url": "https://example.com/image.jpg",
  "max_tokens": 200,
  "temperature": 0.7
}
```

**Response:**
```json
{
  "content": "The image shows a beautiful sunset...",
  "model": "gpt-4-vision-preview",
  "usage": {...}
}
```

## Error Responses

All endpoints return standard error responses:

```json
{
  "detail": "Error message description"
}
```

**Status Codes:**
- `200` - Success
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error

## Rate Limiting

Default rate limits:
- 100 requests per minute per API key
- 10,000 requests per day per API key

## Examples

### Python

```python
import requests

url = "http://localhost:8000/api/v1/chat"
headers = {"Authorization": "Bearer your-api-key"}
data = {
    "messages": [
        {"role": "user", "content": "Hello!"}
    ]
}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

### cURL

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Hello!"}
    ]
  }'
```

### JavaScript

```javascript
const response = await fetch('http://localhost:8000/api/v1/chat', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer your-api-key',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    messages: [
      {role: 'user', content: 'Hello!'}
    ]
  })
});

const data = await response.json();
console.log(data);
```

## Interactive Documentation

Visit http://localhost:8000/docs for interactive Swagger UI documentation.
