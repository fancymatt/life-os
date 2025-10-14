# AI-Studio API Dockerfile

FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Set environment variable to indicate Docker environment
ENV DOCKER_ENV=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ai_capabilities/ ./ai_capabilities/
COPY ai_tools/ ./ai_tools/
COPY api/ ./api/
COPY configs/ ./configs/

# Create directories for volumes (will be mounted)
RUN mkdir -p /app/presets /app/output /app/cache /app/uploads

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the API
CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
