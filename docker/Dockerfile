# ===================================================================
# Multi-stage build for Flask application
# ===================================================================

# ===================================================================
# Stage 1: Builder stage for compiling and installing dependencies
# ===================================================================
FROM python:3.11-slim as builder

# Prevent Python from writing pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set the working directory for the build stage
WORKDIR /build

# Install system-level build dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        python3-dev \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install Python dependencies into a separate directory
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ===================================================================
# Stage 2: Final stage with minimal runtime dependencies
# ===================================================================
FROM python:3.11-slim

# Build argument to determine environment (production/development)
ARG ENVIRONMENT=production

# Set environment variables for Flask and Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app \
    FLASK_ENV=${ENVIRONMENT} \
    PORT=5001 \
    PATH="/home/appuser/.local/bin:${PATH}"

# Set the working directory for the application
WORKDIR /app

# Install minimal runtime dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        bash \
        libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy installed Python packages from builder stage
COPY --from=builder /install /usr/local

# Create a non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser -m appuser \
    && mkdir -p /app/instance \
    && chown -R appuser:appuser /app \
    && chmod -R 775 /app/instance

# Copy application code with proper ownership
COPY --chown=appuser:appuser . .

# Set up entrypoint script
COPY --chown=appuser:appuser docker/docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Switch to non-root user for security
USER appuser

# Expose the application port
EXPOSE ${PORT}

# Configure container health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Set the entrypoint script
ENTRYPOINT ["docker-entrypoint.sh"]
