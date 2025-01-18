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
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get remove -y gcc python3-dev \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy application code
COPY . .

# Make the entrypoint script executable
RUN chmod +x /app/docker/docker-entrypoint.sh

EXPOSE 5001

ENTRYPOINT ["/app/docker/docker-entrypoint.sh"]
