# Use Python 3.12 slim image as base
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app \
    FLASK_ENV=production \
    PORT=5001

# Set working directory in container
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        python3-dev \
        curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir flask-migrate \
    && pip install --no-cache-dir gunicorn

# Copy application code
COPY . .

# Create instance directory and set permissions
RUN mkdir -p /app/instance && \
    chown -R 1000:1000 /app && \
    chmod -R 775 /app/instance && \
    chmod -R 775 /app

# Copy and set up entrypoint script
COPY docker/docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh && \
    chown 1000:1000 /usr/local/bin/docker-entrypoint.sh

# Switch to non-root user
USER 1000

# Expose port
EXPOSE ${PORT}

# Set the entrypoint
ENTRYPOINT ["docker-entrypoint.sh"]
