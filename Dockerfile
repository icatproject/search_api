# Base Stage
FROM python:3.12.7-alpine3.20@sha256:38e179a0f0436c97ecc76bcd378d7293ab3ee79e4b8c440fdc7113670cb6e204 AS base
WORKDIR /app
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Production Stage
FROM base AS production

# Copy the requirements file to the container
COPY requirements.txt /app/

# Install only production dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create a non-root user named 'search-api-user' and group named 'search-api-group'
RUN addgroup -S search-api-group && \
    adduser -S -D -G search-api-group -H -h /app search-api-user

# Set ownership of /app directory to the non-root user and group
RUN chown -R search-api-user:search-api-group /app

# Switch to the non-root user
USER search-api-user

# Only copy whats needed for production
COPY api /app/api

# Expose the port FastAPI will run on
EXPOSE 8000

# Start FastAPI server
CMD ["fastapi", "run", "/app/api/main.py", "--host", "0.0.0.0", "--port", "8000"]

# Testing Stage
FROM base AS test

# Copy the requirements file for the app & the test dependencies
COPY requirements.txt requirements-test.txt /app/

# Install both production and test dependencies
RUN pip install --no-cache-dir -r requirements.txt -r requirements-test.txt

# Copy everything in
COPY . /app

# Run tests using pytest as the default command for this stage, using the envs in pytest.ini
CMD ["pytest",  "-c", "/app/test/pytest.ini", "--maxfail=1", "--disable-warnings", "-v"]
