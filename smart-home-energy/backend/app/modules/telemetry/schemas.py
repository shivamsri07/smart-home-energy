# backend/app/modules/telemetry/schemas.py

import uuid
from datetime import datetime
from pydantic import BaseModel, Field

class TelemetryCreate(BaseModel):
    """
    Schema for a single telemetry data point payload.
    """
    device_id: uuid.UUID = Field(..., alias="deviceId")
    timestamp: datetime
    energy_usage: float = Field(..., alias="energyWatts")

class TelemetryPublic(BaseModel):
    """
    Schema for representing a returned telemetry data point.
    """
    device_id: uuid.UUID
    timestamp: datetime
    energy_usage: float

    class Config:
        from_attributes = True

# --- We'll also add schemas for Device management now ---

class DeviceCreate(BaseModel):
    name: str
    type: str = "APPLIANCE"

class DevicePublic(DeviceCreate):
    id: uuid.UUID
    owner_id: uuid.UUID

    class Config:
        from_attributes = True

class DeviceStats(BaseModel):
    """
    Schema for returning aggregated device statistics.
    """
    device_id: uuid.UUID
    time_period_days: int
    max_usage: float | None
    min_usage: float | None
    avg_usage: float | None