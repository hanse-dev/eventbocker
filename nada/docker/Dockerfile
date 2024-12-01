# Use Python 3.12 slim image as base
FROM python:3.12-slim

# Set working directory in container
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=nada/app \
    FLASK_ENV=production \
    PORT=5001

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        python3-dev \
        curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create instance directory and set permissions
RUN mkdir -p /app/nada/instance && \
    chown -R www-data:www-data /app && \
    chmod -R 777 /app/nada/instance

# Copy and set up entrypoint script
COPY nada/docker/docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh && \
    chown www-data:www-data /usr/local/bin/docker-entrypoint.sh

# Switch to www-data user
USER www-data

# Expose port
EXPOSE ${PORT}

# Set the entrypoint
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0"]
