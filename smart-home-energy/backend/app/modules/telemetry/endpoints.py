# backend/app/modules/telemetry/endpoints.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.user import User
from app.models.device import Device, Telemetry
from ..auth.dependencies import get_current_user
from . import schemas

router = APIRouter(
    prefix="/telemetry",
    tags=["Telemetry"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.TelemetryPublic)
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


