FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Set work directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./

# Configure Poetry
RUN poetry config virtualenvs.create false

# Install dependencies only (without installing the project itself)
RUN poetry install --without dev --no-root

# Copy application code
COPY . .

# Now install the package
RUN poetry install --only-root

# Create directories for automation queues
RUN mkdir -p \
    content/queue \
    content/done \
    story/queue \
    story/done \
    ads/queue \
    ads/done

# Sicherheit: non-root
RUN addgroup --system app && adduser --system --ingroup app app
RUN chown -R app:app /app
USER app

# Set entrypoint
ENTRYPOINT ["rrtg"]
CMD ["--help"]

# Expose port for Prometheus exporter
EXPOSE 9100 