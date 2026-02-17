# Generative AI Cloud Projects - Docker Quick Start

## 🚀 Running with Docker

### Prerequisites
- Docker Desktop installed
- `.env` file configured (copy from `.env.example`)

### Quick Commands

```bash
# Build all services
docker-compose build

# Run single use case (demo mode, no API keys needed)
docker-compose up marketing-content

# Run all services
docker-compose up -d

# Check logs
docker-compose logs -f marketing-content

# Stop all
docker-compose down

# Rebuild after code changes
docker-compose up --build marketing-content
```

### Available Services

| Service | Port | Command Example |
|---------|------|-----------------|
| marketing-content | 8001 | `docker-compose run marketing-content python main.py --type email` |
| product-image | 8002 | `docker-compose run product-image python main.py --description "red shoes"` |
| code-completion | 8003 | `docker-compose run code-completion python main.py --code "def add():"` |
| customer-support | 8004 | `docker-compose run customer-support python main.py --query "returns"` |
| code-review | 8008 | `docker-compose run code-review python main.py` |

### Production Builds

```bash
# Build optimized image
docker build -f docker/base.Dockerfile -t genai-base:latest .

# Run with custom environment
docker run -e RUN_MODE=dev -e OPENAI_API_KEY=sk-xxx genai-base
```

### Troubleshooting

```bash
# View container logs
docker-compose logs marketing-content

# Access container shell
docker-compose exec marketing-content /bin/bash

# Rebuild without cache
docker-compose build --no-cache

# Remove all containers and volumes
docker-compose down -v
```
