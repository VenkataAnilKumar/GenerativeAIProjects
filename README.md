# GenAI Platform

> Production-ready, cloud-agnostic Generative AI platform deployable across AWS, Azure, and Google Cloud

[![CI/CD](https://github.com/VenkataAnilKumar/GenerativeAIProjects/workflows/CI%2FCD%20Pipeline/badge.svg)](https://github.com/VenkataAnilKumar/GenerativeAIProjects/actions)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Security](https://img.shields.io/badge/security-patched-green.svg)](SECURITY.md)

> **🔒 Security Update (v0.1.1)**: All critical vulnerabilities patched. See [CHANGELOG](CHANGELOG.md) for details.

## 🚀 Features

### Core AI Capabilities
- **LLM Text Generation** - Support for GPT-4, Claude, Gemini, and more
- **Multimodal Inference** - Vision + text with GPT-4V and Gemini Pro Vision
- **Code Completion** - Intelligent code generation, explanation, and fixing
- **RAG Pipeline** - Retrieval-augmented generation with pluggable vector stores

### Model Provider Abstraction
- **Multi-Provider Support** - OpenAI, Azure OpenAI, Google Vertex AI, AWS Bedrock
- **Unified API** - Single interface for all providers
- **Automatic Failover** - Provider redundancy and fallback
- **Cost Optimization** - Intelligent routing based on cost/performance

### Vector Stores
- **Pluggable Architecture** - Easy to swap vector databases
- **Supported Stores**:
  - Chroma (embedded, default)
  - Pinecone (managed)
  - Weaviate (open-source)
  - Qdrant (high-performance)

### Production Features
- **API Layer** - FastAPI with async support and OpenAPI documentation
- **Async Processing** - Celery workers for background tasks
- **Observability** - Prometheus metrics, OpenTelemetry tracing, structured logging
- **RBAC** - Role-based access control with JWT authentication
- **Containerization** - Docker and Docker Compose ready
- **Infrastructure as Code** - Terraform modules for AWS, Azure, and GCP

### LLMOps
- **Evaluation Framework** - BLEU, ROUGE, and custom metrics
- **Cost Tracking** - Real-time usage and cost monitoring
- **Model Versioning** - Version control for models and configurations
- **Performance Monitoring** - Dashboards and alerts

## 📋 Quick Start

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- API keys for LLM providers (OpenAI, Azure, Google, or AWS)

### Local Development

```bash
# Clone repository
git clone https://github.com/VenkataAnilKumar/GenerativeAIProjects.git
cd GenerativeAIProjects

# Setup environment
cp .env.example .env
# Edit .env with your API keys

# Start with Docker Compose
docker-compose up -d

# Access the API
open http://localhost:8000/docs
```

### Manual Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the API
uvicorn src.api.main:app --reload
```

## 📖 Documentation

- [Architecture Overview](docs/ARCHITECTURE.md)
- [API Documentation](docs/API.md)
- [Deployment Guide](docs/DEPLOYMENT.md)

## 🔧 Configuration

Key environment variables:

```bash
# Model Providers
OPENAI_API_KEY=sk-...
AZURE_OPENAI_API_KEY=...
GOOGLE_PROJECT_ID=...
AWS_ACCESS_KEY_ID=...

# Vector Store
DEFAULT_VECTOR_STORE=chroma
CHROMA_HOST=localhost
CHROMA_PORT=8001

# Database & Cache
DATABASE_URL=postgresql://user:pass@localhost:5432/genai
REDIS_URL=redis://localhost:6379/0
```

See [.env.example](.env.example) for full configuration options.

## 🌐 API Examples

### Chat Completion

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Explain quantum computing"}
    ],
    "temperature": 0.7,
    "provider": "openai"
  }'
```

### RAG Query

```bash
# Add documents
curl -X POST http://localhost:8000/api/v1/rag/documents \
  -H "Content-Type: application/json" \
  -d '{
    "texts": ["Paris is the capital of France."]
  }'

# Query
curl -X POST http://localhost:8000/api/v1/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the capital of France?"
  }'
```

### Code Completion

```bash
curl -X POST http://localhost:8000/api/v1/code/complete \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def fibonacci(n):",
    "language": "python"
  }'
```

## 🏗️ Architecture

```
┌─────────────┐
│   Clients   │
└──────┬──────┘
       │
┌──────▼──────────────────────────┐
│     FastAPI Application         │
│  ┌────────┬────────┬─────────┐  │
│  │  Chat  │  Code  │   RAG   │  │
│  └────────┴────────┴─────────┘  │
└──────┬──────────────────────────┘
       │
┌──────▼──────────┬───────────────┬──────────────┐
│ Model Providers │ Vector Stores │   Database   │
│  • OpenAI       │  • Chroma     │  • Postgres  │
│  • Azure        │  • Pinecone   │  • Redis     │
│  • Google       │  • Weaviate   │              │
│  • AWS          │  • Qdrant     │              │
└─────────────────┴───────────────┴──────────────┘
```

## 🚢 Deployment

### AWS

```bash
cd terraform/aws
terraform init
terraform apply
```

### Azure

```bash
cd terraform/azure
terraform init
terraform apply
```

### Google Cloud

```bash
cd terraform/gcp
terraform init
terraform apply
```

See [Deployment Guide](docs/DEPLOYMENT.md) for detailed instructions.

## 📊 Monitoring

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000
- **API Metrics**: http://localhost:8000/metrics

## 🧪 Testing

```bash
# Run tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

## 🛡️ Security

- JWT-based authentication
- API key management
- Encryption at rest and in transit
- RBAC for access control
- Security scanning in CI/CD
- Secrets management

## 📈 Performance

- Async API with FastAPI
- Connection pooling
- Response caching
- Horizontal scaling support
- Load balancing ready

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- LangChain for AI orchestration patterns
- All the AI model providers (OpenAI, Google, Anthropic, AWS)
- The open-source community

## 📞 Support

- GitHub Issues: [Report a bug](https://github.com/VenkataAnilKumar/GenerativeAIProjects/issues)
- Documentation: [docs/](docs/)

---

Built with ❤️ for enterprise AI applications
