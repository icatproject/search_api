# Base Stage
FROM python:3.12.7-alpine AS base
WORKDIR /app
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Production Stage
FROM base AS production

# Copy the requirements file to the container
COPY requirements.txt /app/

# Install only production dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Only copy whats needed for production
COPY api /app/api

# Expose the port FastAPI will run on
EXPOSE 8000

# Start FastAPI server
CMD ["uvicorn", "api.main:app", "--host=0.0.0.0", "--port=8000"]

# Testing Stage
FROM base AS test

# Copy the requirements file for test dependencies
COPY requirements-test.txt /app/

# Install both production and test dependencies
RUN pip install --no-cache-dir -r requirements-test.txt
RUN pip install pytest

# Copy everything in
COPY . /app

# Run tests using pytest as the default command for this stage, using the envs in pytest.ini
CMD ["pytest",  "-c", "/app/test/pytest.ini", "--maxfail=1", "--disable-warnings", "-v"]
