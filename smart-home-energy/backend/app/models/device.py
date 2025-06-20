import uuid
from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    DateTime,
    func,
    DECIMAL,
    PrimaryKeyConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from ..core.db import Base

class Device(Base):
    """
    Device Model
    Represents a user's smart home device.
    """
    __tablename__ = "devices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    type = Column(String, default="APPLIANCE")
    
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Establishes a bidirectional relationship between Device and User
    owner = relationship("User", back_populates="devices")
    telemetry_data = relationship("Telemetry", cascade="all, delete-orphan")


class Telemetry(Base):
    """
    Telemetry Model
    Represents a single data point of energy usage for a device.
    """
    __tablename__ = "telemetry"

    device_id = Column(UUID(as_uuid=True), ForeignKey("devices.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=func.now())
    energy_usage = Column(DECIMAL(10, 4), nullable=False) # e.g., 123456.7890

    # This creates a composite primary key, which also automatically creates
    # the essential index on (device_id, timestamp) for fast time-series queries.
    __table_args__ = (
        PrimaryKeyConstraint('device_id', 'timestamp'),
    )