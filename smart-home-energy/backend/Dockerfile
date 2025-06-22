# --- Stage 1: The Builder ---
# This stage installs all dependencies, including development ones,
# and prepares a clean "packages" directory.
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install pipenv
RUN pip install pipenv

# Copy the dependency files
COPY Pipfile Pipfile.lock ./

# Install all dependencies into a virtual environment
# We add --dev to ensure alembic is available for migrations
RUN pipenv install --system --dev

# --- Stage 2: The Final Runtime Image ---
# This stage creates the final, lean image for production.
FROM python:3.11-slim as runtime

WORKDIR /app

# Copy the installed Python packages from the builder stage.
# This is more efficient than running pip install again.
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy our application source code
COPY ./app ./app
COPY ./alembic ./alembic
COPY ./alembic.ini ./

# The command to run the application. This replaces the Procfile.
CMD ["hypercorn", "main:app", "--bind", "::"]