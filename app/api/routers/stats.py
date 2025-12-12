"""
Statistics and Health Router

Endpoints for system statistics and health checks.
"""

from fastapi import APIRouter, Depends

from app.api.schemas.auth import User
from app.api.dependencies import require_role
from app.services.shipment import shipments_db
from app.models.shipment import ShipmentStatus


router = APIRouter(tags=["Statistics"])


@router.get("/stats")
async def get_shipment_statistics(
    current_user: User = Depends(require_role(["admin"]))
):
    """
    **Shipment Statistics**
    
    Mendapatkan statistik shipment.
    Hanya admin yang dapat mengakses statistik.
    
    **Requires:** Admin role
    """
    total = len(shipments_db)
    
    # Count by status
    status_counts = {}
    for shipment in shipments_db.values():
        status = shipment["current_status"]
        status_counts[status] = status_counts.get(status, 0) + 1
    
    return {
        "total_shipments": total,
        "by_status": status_counts
    }


@router.get("/health")
async def health_check():
    """
    **Health Check**
    
    Endpoint sederhana untuk mengecek status API.
    Tidak memerlukan autentikasi.
    """
    return {
        "status": "healthy",
        "service": "LOGIXPress API",
        "version": "1.0.0"
    }
