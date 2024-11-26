# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory in container
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=nada/app/app.py \
    FLASK_ENV=production

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create instance directory and set permissions
RUN mkdir -p /app/instance && chown -R www-data:www-data /app/instance

# Copy entrypoint script
COPY nada/docker/docker-entrypoint.sh /usr/local/bin/

# Make entrypoint executable
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Switch to non-root user
USER www-data

# Expose port
EXPOSE 5001

# Set entrypoint
ENTRYPOINT ["docker-entrypoint.sh"]

# Command to run
CMD ["flask", "run", "--host=0.0.0.0", "--port=5001"]
