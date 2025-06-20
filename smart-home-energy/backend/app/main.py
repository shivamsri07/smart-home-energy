# backend/app/main.py

from fastapi import FastAPI
from .api.router import api_router
from .core.db import engine, Base

# This line creates all the tables defined by our models in the database.
# In a real production app, you would use a migration tool like Alembic.
# For our prototype, this is sufficient.

app = FastAPI(
    title="Smart Home Energy API",
    description="API for monitoring energy consumption of smart home devices.",
    version="0.1.0"
)

@app.get("/", tags=["Health Check"])
def read_root():
    """A simple health check endpoint."""
    return {"status": "ok"}

# Include the main API router
app.include_router(api_router, prefix="/api")