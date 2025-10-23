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
COPY scripts/ ./scripts/

# Copy Alembic files for database migrations
COPY alembic/ ./alembic/
COPY alembic.ini ./alembic.ini

# Copy entrypoint script
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

# Create directories for volumes (will be mounted)
RUN mkdir -p /app/presets /app/output /app/cache /app/uploads

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the API with entrypoint script
CMD ["/app/docker-entrypoint.sh"]
