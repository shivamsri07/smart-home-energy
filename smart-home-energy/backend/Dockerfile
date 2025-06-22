# --- Stage 1: The Builder ---
# This stage installs all dependencies, including development ones,
# and prepares a clean "packages" directory.
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./app ./app
COPY ./alembic ./alembic
COPY alembic.ini .

CMD ["hypercorn", "main:app", "--bind", "::"]

