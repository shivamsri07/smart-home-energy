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
    time_window: schemas.TimeWindow,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get energy usage summary for a specific device over different time windows:
    - 7d: Last 7 days data with daily aggregation (7 bars)
    - 12h: Last 12 hours data with hourly aggregation (12 bars)
    - 6h: Last 6 hours data with hourly aggregation (6 bars)
    """
    # Security Check: Verify the device belongs to the current user
    device = db.query(Device).filter(Device.id == device_id, Device.owner_id == current_user.id).first()
    if not device:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Device not found")

    # Calculate the time window
    now = datetime.now(timezone.utc)
    if time_window == schemas.TimeWindow.SEVEN_DAYS:
        start_date = now - timedelta(days=7)
        # For 7 days, we group by date
        stats = db.query(
            func.date_trunc('day', Telemetry.timestamp).label('timestamp'),
            func.sum(Telemetry.energy_usage).label('total_energy')
        ).filter(
            Telemetry.device_id == device_id,
            Telemetry.timestamp >= start_date
        ).group_by(
            func.date_trunc('day', Telemetry.timestamp)
        ).order_by(
            func.date_trunc('day', Telemetry.timestamp).desc()
        ).all()

        # Convert to data points with day labels
        data_points = [
            schemas.EnergyUsagePoint(
                timestamp=stat.timestamp,
                total_energy=stat.total_energy,
                label=stat.timestamp.strftime("%A")  # Day name
            ) for stat in stats
        ]

    else:  # 12h or 6h
        hours = 12 if time_window == schemas.TimeWindow.TWELVE_HOURS else 6
        start_date = now - timedelta(hours=hours)
        
        # For hours, we group by hour
        stats = db.query(
            func.date_trunc('hour', Telemetry.timestamp).label('timestamp'),
            func.sum(Telemetry.energy_usage).label('total_energy')
        ).filter(
            Telemetry.device_id == device_id,
            Telemetry.timestamp >= start_date
        ).group_by(
            func.date_trunc('hour', Telemetry.timestamp)
        ).order_by(
            func.date_trunc('hour', Telemetry.timestamp).desc()
        ).all()

        # Convert to data points with hour labels
        data_points = [
            schemas.EnergyUsagePoint(
                timestamp=stat.timestamp,
                total_energy=stat.total_energy,
                label=stat.timestamp.strftime("%H:00")  # Hour in 24-hour format
            ) for stat in stats
        ]

    return schemas.DeviceStats(
        device_id=device_id,
        time_window=time_window,
        data_points=data_points
    )
