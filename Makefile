.PHONY: help install dev-install test lint format clean docker-build docker-up docker-down deploy-aws deploy-azure deploy-gcp

help:
	@echo "GenAI Platform - Makefile Commands"
	@echo ""
	@echo "Development:"
	@echo "  make install       - Install production dependencies"
	@echo "  make dev-install   - Install development dependencies"
	@echo "  make test          - Run tests"
	@echo "  make lint          - Run linters"
	@echo "  make format        - Format code"
	@echo "  make clean         - Clean build artifacts"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build  - Build Docker images"
	@echo "  make docker-up     - Start services with Docker Compose"
	@echo "  make docker-down   - Stop services"
	@echo ""
	@echo "Deployment:"
	@echo "  make deploy-aws    - Deploy to AWS"
	@echo "  make deploy-azure  - Deploy to Azure"
	@echo "  make deploy-gcp    - Deploy to Google Cloud"

install:
	pip install -r requirements.txt

dev-install:
	pip install -r requirements.txt
	pip install pytest pytest-asyncio pytest-cov black flake8 mypy

test:
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term

lint:
	flake8 src tests
	mypy src --ignore-missing-imports

format:
	black src tests
	isort src tests

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/ .coverage htmlcov/ .pytest_cache/

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f api

deploy-aws:
	cd terraform/aws && terraform init && terraform apply

deploy-azure:
	cd terraform/azure && terraform init && terraform apply

deploy-gcp:
	cd terraform/gcp && terraform init && terraform apply

run:
	uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
