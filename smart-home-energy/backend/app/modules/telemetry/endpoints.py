# backend/app/modules/telemetry/endpoints.py
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.db import get_db
from app.models.user import User
from app.models.device import Device, Telemetry
from ..auth.dependencies import get_current_user
from . import schemas
from datetime import datetime, timezone, timedelta
from sqlalchemy import func

telemetry_router = APIRouter(
    prefix="/telemetry",
    tags=["Telemetry"],
    responses={404: {"description": "Not found"}},
)

device_router = APIRouter(
    prefix="/devices",
    tags=["Devices"],
    dependencies=[Depends(get_current_user)] # Protect all routes in this router
)


@telemetry_router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.TelemetryPublic)
def submit_telemetry_data(
    telemetry_in: schemas.TelemetryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Submit a new telemetry data point for a device.
    The device must belong to the authenticated user.
    """
    # Security Check: Verify the device belongs to the current user
    device = db.query(Device).filter(
        Device.id == telemetry_in.device_id,
        Device.owner_id == current_user.id
    ).first()

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found or you do not have permission to access it.",
        )

    # Create the new telemetry record
    db_telemetry = Telemetry(
        device_id=telemetry_in.device_id,
        timestamp=telemetry_in.timestamp,
        energy_usage=telemetry_in.energy_usage
    )
    db.add(db_telemetry)
    db.commit()
    db.refresh(db_telemetry)
    
    return db_telemetry


@device_router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.DevicePublic)
def create_device(
    device_in: schemas.DeviceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new device for the authenticated user.
    """
    db_device = Device(**device_in.model_dump(), owner_id=current_user.id)
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device


@device_router.get("/", response_model=List[schemas.DevicePublic])
def list_user_devices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all devices owned by the authenticated user.
    """
    return db.query(Device).filter(Device.owner_id == current_user.id).all()


@device_router.get("/{device_id}/stats", response_model=schemas.DeviceStats)
def get_device_stats(
    device_id: uuid.UUID,
    days: int = 7, # Default to the last 7 days
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get aggregated energy usage statistics (MIN, MAX, AVG) for a specific device
    over a given number of past days.
    """
    # Security Check: Verify the device belongs to the current user
    device = db.query(Device).filter(Device.id == device_id, Device.owner_id == current_user.id).first()
    if not device:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Device not found")

    # Calculate the time window
    start_date = datetime.now(timezone.utc) - timedelta(days=days)

    # Query for the aggregated data
    stats = db.query(
        func.max(Telemetry.energy_usage).label("max_usage"),
        func.min(Telemetry.energy_usage).label("min_usage"),
        func.avg(Telemetry.energy_usage).label("avg_usage")
    ).filter(
        Telemetry.device_id == device_id,
        Telemetry.timestamp >= start_date
    ).one()

    return schemas.DeviceStats(
        device_id=device_id,
        time_period_days=days,
        max_usage=stats.max_usage,
        min_usage=stats.min_usage,
        avg_usage=stats.avg_usage
    )
