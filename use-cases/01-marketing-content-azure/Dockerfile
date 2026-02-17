# ===================================================
# Use Case 01: Marketing Content Generation (Azure)
# ===================================================

FROM python:3.11-slim

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

# Expose port for future API
EXPOSE 8000

# Run main.py
CMD ["python", "main.py", "--help"]
