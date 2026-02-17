#!/bin/bash
# ==============================================
# Dockerfile Generator for All Use Cases
# ==============================================
# This script creates identical Dockerfiles for all use cases

TEMPLATE='FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared scripts
COPY ../../scripts /app/scripts

# Copy use case files
COPY . /app/use-case

# Set Python path
ENV PYTHONPATH=/app

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

WORKDIR /app/use-case

# Expose port
EXPOSE 8000

# Run main.py
CMD ["python", "main.py"]
'

# Create Dockerfiles for all 10 use cases
for i in {01..10}; do
  case $i in
    01) dir="01-marketing-content-azure" ;;
    02) dir="02-product-image-aws" ;;
    03) dir="03-code-completion-gcp" ;;
    04) dir="04-customer-support-aws" ;;
    05) dir="05-healthcare-summarization-azure" ;;
    06) dir="06-personalized-learning-gcp" ;;
    07) dir="07-creative-ad-gcp" ;;
    08) dir="08-automated-code-review-aws" ;;
    09) dir="09-legal-analysis-azure" ;;
    10) dir="10-manufacturing-simulation-gcp" ;;
  esac
  
  echo "$TEMPLATE" > "use-cases/$dir/Dockerfile"
  echo "Created: use-cases/$dir/Dockerfile"
done

echo "✓ All Dockerfiles created"
