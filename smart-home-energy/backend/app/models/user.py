# backend/app/models/user.py

import uuid
from sqlalchemy import Column, String, DateTime, func, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from ..core.db import Base

class User(Base):
    """
    User Model
    Represents the 'users' table in the database.
    """
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

    # Relationship to devices (for future use)
    devices = relationship("Device", back_populates="owner", cascade="all, delete-orphan")