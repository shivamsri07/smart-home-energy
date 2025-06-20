# backend/app/core/db.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# Create the SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    # connect_args={"check_same_thread": False} # This is only needed for SQLite
)

# Create a sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for our models to inherit from
Base = declarative_base()

# Dependency for FastAPI to get a DB session
def get_db():
    """
    FastAPI dependency that provides a SQLAlchemy database session.
    Ensures the session is always closed after the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()