FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy and install requirements
COPY pyproject.toml ./
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --without dev --no-root

# Copy application code
COPY . .

# Install the package
RUN poetry install --only-root

# Create directories
RUN mkdir -p content/queue content/done story/queue story/done ads/queue ads/done

# Create non-root user
RUN adduser --system --group app
RUN chown -R app:app /app
USER app

# Set entrypoint
ENTRYPOINT ["rrtg"]
CMD ["--help"]

EXPOSE 9100 