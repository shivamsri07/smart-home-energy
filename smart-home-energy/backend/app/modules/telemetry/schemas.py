# backend/app/modules/telemetry/schemas.py

import uuid
from datetime import datetime, date
from pydantic import BaseModel, Field, UUID4
from typing import List, Optional
from enum import Enum

class TimeWindow(str, Enum):
    SEVEN_DAYS = "7d"
    TWELVE_HOURS = "12h"
    SIX_HOURS = "6h"

class TelemetryBase(BaseModel):
    device_id: UUID4
    timestamp: datetime
    energy_usage: float

class TelemetryCreate(TelemetryBase):
    """
    Schema for a single telemetry data point payload.
    """
    pass

class TelemetryPublic(TelemetryBase):
    """
    Schema for representing a returned telemetry data point.
    """
    id: UUID4

    class Config:
        from_attributes = True

# --- We'll also add schemas for Device management now ---

class DeviceCreate(BaseModel):
    name: str
    type: str = "APPLIANCE"

class DevicePublic(DeviceCreate):
    id: UUID4
    owner_id: UUID4

    class Config:
        from_attributes = True

class EnergyUsagePoint(BaseModel):
    timestamp: datetime
    total_energy: float
    label: str  # "Monday", "Tuesday", etc. for days or "14:00", "15:00" etc. for hours

class DeviceStats(BaseModel):
    """
    Schema for returning hourly energy usage data for a device.
    """
    device_id: UUID4
    time_window: TimeWindow
    data_points: list[EnergyUsagePoint]