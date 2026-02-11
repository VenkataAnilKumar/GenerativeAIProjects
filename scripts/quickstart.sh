#!/bin/bash
# Quick start script for GenAI Platform

set -e

echo "🚀 GenAI Platform - Quick Start"
echo "================================"
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker found"
echo "✅ Docker Compose found"
echo ""

# Check for .env file
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your API keys before starting"
    echo ""
    read -p "Press enter to continue or Ctrl+C to exit and configure .env..."
fi

# Build and start services
echo "🔨 Building Docker images..."
docker-compose build

echo ""
echo "🚀 Starting services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if API is responding
if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
    echo "✅ API is up and running!"
else
    echo "⚠️  API might still be starting. Check logs with: docker-compose logs -f api"
fi

echo ""
echo "🎉 GenAI Platform is ready!"
echo ""
echo "📚 Access points:"
echo "  - API: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo "  - Prometheus: http://localhost:9090"
echo "  - Grafana: http://localhost:3000 (admin/admin)"
echo ""
echo "📖 Next steps:"
echo "  1. Configure your API keys in .env"
echo "  2. Visit http://localhost:8000/docs to explore the API"
echo "  3. Run example script: python examples/usage_example.py"
echo ""
echo "🛠️  Useful commands:"
echo "  - View logs: docker-compose logs -f"
echo "  - Stop services: docker-compose down"
echo "  - Restart: docker-compose restart"
echo ""
