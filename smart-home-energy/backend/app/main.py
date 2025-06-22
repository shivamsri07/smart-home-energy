# backend/app/main.py

import os
import uvicorn
from fastapi import FastAPI
from .api.router import api_router
from .core.db import engine, Base
from fastapi.middleware.cors import CORSMiddleware

# This line creates all the tables defined by our models in the database.
# In a real production app, you would use a migration tool like Alembic.
# For our prototype, this is sufficient.

app = FastAPI(
    title="Smart Home Energy API",
    description="API for monitoring energy consumption of smart home devices.",
    version="0.1.0"
)

origins = [
    "http://localhost:5173", # The address of our React frontend
    "http://localhost:3000", # A common alternative React dev port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allow all methods (GET, POST, etc.)
    allow_headers=["*"], # Allow all headers
)

@app.get("/", tags=["Health Check"])
def read_root():
    """A simple health check endpoint."""
    return {"status": "ok"}

# Include the main API router
app.include_router(api_router, prefix="/api")