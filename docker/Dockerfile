# ===================================================================
# Multi-stage build for Flask application
# ===================================================================

# ===================================================================
# Stage 1: Builder stage for compiling and installing dependencies
# ===================================================================
FROM python:3.12-slim as builder

# Prevent Python from writing pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set the working directory for the build stage
WORKDIR /build

# Install system-level build dependencies
# gcc: Required for compiling some Python packages
# python3-dev: Required for building Python extensions
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        python3-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install Python dependencies into a separate directory
# This allows us to copy only the installed packages to the final image
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt \
    && pip install --no-cache-dir --prefix=/install flask-migrate

# ===================================================================
# Stage 2: Final stage with minimal runtime dependencies
# ===================================================================
FROM python:3.12-slim

# Build argument to determine environment (production/development)
ARG ENVIRONMENT=production

# Set environment variables for Flask and Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app \
    FLASK_ENV=${ENVIRONMENT} \
    PORT=5001

# Set the working directory for the application
WORKDIR /app

# Install minimal runtime dependencies
# curl: Required for healthcheck and general HTTP requests
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy installed Python packages from builder stage
COPY --from=builder /install /usr/local

# Install environment-specific packages
# Production: gunicorn for production-grade WSGI server
# Development: watchdog for file system monitoring
RUN if [ "$ENVIRONMENT" = "production" ] ; then \
        pip install --no-cache-dir gunicorn ; \
    else \
        pip install --no-cache-dir watchdog[watchmedo] ; \
    fi

# Create a non-root user for security
# Set up proper permissions for application directories
RUN groupadd -r appuser && useradd -r -g appuser appuser \
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
