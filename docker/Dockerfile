# Simplified Dockerfile for Flask application

FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app \
    PORT=5001

WORKDIR /app

# Install system dependencies and Python packages
COPY requirements.txt .
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        python3-dev \
        libpq-dev \
        sqlite3 \
        curl \
        dos2unix \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get remove -y gcc python3-dev \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user
RUN useradd -m -u 1000 flaskuser && \
    mkdir -p /app/instance /app/migrations && \
    chown -R flaskuser:flaskuser /app

# Copy application code
COPY --chown=flaskuser:flaskuser . .

# Switch to non-root user
USER flaskuser

# Fix line endings and make the entrypoint script executable
RUN dos2unix /app/docker/docker-entrypoint.sh \
    && chmod +x /app/docker/docker-entrypoint.sh

# Expose port
EXPOSE ${PORT}

# Run the application
CMD ["python", "wsgi.py"]
