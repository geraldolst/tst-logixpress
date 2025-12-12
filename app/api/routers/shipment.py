"""
Shipment Router

Endpoints for shipment CRUD operations.
"""

from fastapi import APIRouter, status, Query, Depends
from typing import Optional, List

from app.api.schemas.shipment import (
    ShipmentCreate,
    ShipmentRead,
    ShipmentUpdate,
    ShipmentSummary,
    ShipmentCreationResponse
)
from app.models.shipment import ShipmentStatus
from app.api.schemas.auth import User
from app.api.dependencies import get_current_active_user, require_role
from app.services.shipment import ShipmentService


router = APIRouter(prefix="/shipment", tags=["Shipments"])


@router.get("s", response_model=List[ShipmentSummary])
async def get_all_shipments(
    status_filter: Optional[ShipmentStatus] = Query(None, alias="status", description="Filter by shipment status"),
    destination_code: Optional[int] = Query(None, description="Filter by destination code"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results"),
    current_user: User = Depends(get_current_active_user)
):
    """
    **C0102: Shipment Tracking & Status Update**
    
    Mengambil daftar shipment dengan opsi filtering berdasarkan status dan destination.
    Mengembalikan summary view untuk efisiensi.
    
    **Requires:** Any authenticated user
    """
    return ShipmentService.get_all_shipments(
        status_filter=status_filter,
        destination_filter=destination_code,
        limit=limit
    )


@router.get("/{shipment_id}", response_model=ShipmentRead)
async def get_shipment_by_id(
    shipment_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """
    **C0102: Shipment Tracking & Status Update**
    
    Mengambil detail lengkap shipment berdasarkan Tracking Number (ID).
    Mengembalikan Aggregate Root lengkap dengan semua Value Objects dan Tracking Events.
    
    **Requires:** Any authenticated user
    """
    return ShipmentService.get_shipment_by_id(shipment_id)


@router.post("", response_model=ShipmentCreationResponse, status_code=status.HTTP_201_CREATED)
async def create_shipment(
    shipment: ShipmentCreate,
    current_user: User = Depends(require_role(["admin", "customer"]))
):
    """
    **C0101: Shipment Order Creation**
    
    Membuat shipment baru (Aggregate Root).
    Status awal selalu 'placed' dan tracking event pertama dibuat otomatis.
    
    **Requires:** Admin or Customer role
    """
    return ShipmentService.create_shipment(shipment)


@router.patch("/{shipment_id}", response_model=ShipmentRead)
async def update_shipment(
    shipment_id: int,
    update_data: ShipmentUpdate,
    current_user: User = Depends(require_role(["admin", "courier"]))
):
    """
    **C0102: Shipment Tracking & Status Update**
    
    Update shipment details. Jika status berubah, tracking event baru akan dibuat.
    Hanya Aggregate Root yang boleh memodifikasi Internal Entities.
    
    **Requires:** Admin or Courier role
    """
    return ShipmentService.update_shipment(shipment_id, update_data)


@router.delete("/{shipment_id}")
async def delete_shipment(
    shipment_id: int,
    current_user: User = Depends(require_role(["admin"]))
):
    """
    **Delete Shipment**
    
    Menghapus shipment dari sistem.
    Hanya admin yang dapat menghapus shipment.
    
    **Requires:** Admin role
    """
    return ShipmentService.delete_shipment(shipment_id)
