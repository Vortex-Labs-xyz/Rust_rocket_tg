# Use Python 3.13 slim image
FROM python:3.13-slim

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry==1.8.4

# Configure Poetry
ENV POETRY_NO_INTERACTION=1
ENV POETRY_VIRTUALENVS_CREATE=false
ENV POETRY_CACHE_DIR=/tmp/poetry_cache

# Set working directory
WORKDIR /app

# Copy dependency files first (for better Docker layer caching)
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --only main --no-root && rm -rf $POETRY_CACHE_DIR

# Copy source code
COPY rustrocket_x/ ./rustrocket_x/
COPY README.md ./

# Install the package
RUN poetry install --only main

# Set the entry point
CMD ["python", "-m", "rustrocket_x"]

EXPOSE 9100 