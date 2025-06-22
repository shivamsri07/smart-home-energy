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

# create a bash script to run the FastAPI project
# this script will execute at runtime when
# the container starts and the database is available
RUN printf "#!/bin/bash\n" > ./paracord_runner.sh && \
    printf "RUN_PORT=\"\${PORT:-8000}\"\n\n" >> ./paracord_runner.sh && \
    printf "gunicorn ${PROJ_NAME}:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind \"[::]:\$RUN_PORT\"\n" >> ./paracord_runner.sh

# make the bash script executable
RUN chmod +x paracord_runner.sh

CMD ./paracord_runner.sh

