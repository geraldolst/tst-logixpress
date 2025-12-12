"""
Tracking Router

Endpoints for shipment tracking events.
"""

from fastapi import APIRouter, status, Depends
from typing import List

from app.api.schemas.shipment import TrackingEvent, TrackingEventCreate
from app.api.schemas.auth import User
from app.api.dependencies import get_current_active_user, require_role
from app.services.shipment import ShipmentService


router = APIRouter(prefix="/shipment", tags=["Tracking"])


@router.get("/{shipment_id}/tracking", response_model=List[TrackingEvent])
async def get_shipment_tracking_history(
    shipment_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """
    **Get Tracking History**
    
    Mengambil riwayat tracking events untuk shipment tertentu.
    
    **Requires:** Any authenticated user
    """
    return ShipmentService.get_tracking_history(shipment_id)


@router.post("/{shipment_id}/tracking", response_model=TrackingEvent, status_code=status.HTTP_201_CREATED)
async def add_tracking_event(
    shipment_id: int,
    event: TrackingEventCreate,
    current_user: User = Depends(require_role(["admin", "courier"]))
):
    """
    **Add Tracking Event**
    
    Menambahkan tracking event baru untuk shipment.
    Event akan otomatis update status shipment.
    
    **Requires:** Admin or Courier role
    """
    return ShipmentService.add_tracking_event(shipment_id, event)
