# backend/app/modules/telemetry/schemas.py

import uuid
from datetime import datetime, date
from pydantic import BaseModel, Field
from typing import List

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

class HourlyEnergyUsage(BaseModel):
    """
    Schema for hourly energy usage summary.
    """
    date: date
    hour: int
    total_energy: float

class DeviceStats(BaseModel):
    """
    Schema for returning hourly energy usage data for a device.
    """
    device_id: uuid.UUID
    time_period_days: int
    hourly_usage: List[HourlyEnergyUsage]