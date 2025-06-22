# --- Stage 1: The Builder ---
# This stage installs all dependencies, including development ones,
# and prepares a clean "packages" directory.
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

WORKDIR /app

# Copy our application source code
COPY ./app ./app
COPY ./alembic ./alembic
COPY ./alembic.ini ./

RUN pip install --no-cache-dir -r requirements.txt


# The command to run the application. This replaces the Procfile.
CMD ["hypercorn", "main:app", "--bind", "::"]