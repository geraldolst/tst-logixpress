from fastapi import FastAPI, HTTPException, status, Query
from scalar_fastapi import get_scalar_api_reference
from typing import List, Optional
from datetime import datetime

from .schemas import (
    ShipmentCreate, ShipmentRead, ShipmentUpdate, ShipmentSummary,
    ShipmentStatus, TrackingEventCreate, TrackingEvent,
    Recipient, Seller, PackageDetails
)

app = FastAPI(
    title="LOGIXPress API",
    description="""Last-Mile Delivery System - Shipment Lifecycle Management API
    
    Bounded Context: **Shipment Lifecycle Management** (Core Domain)
    
    Sistem ini mengelola siklus hidup pengiriman dari pembuatan order hingga delivered,
    dengan tracking events yang lengkap sesuai prinsip Domain-Driven Design (DDD).
    """,
    version="1.0.0",
    contact={
        "name": "Geraldo Linggom Samuel Tampubolon",
        "email": "geraldo.tampubolon@example.com"
    }
)

# === IN-MEMORY DATA STORE (Aggregate Root: Shipment) ===
shipments = {
    12701: {
        "package_details": {
            "content": "aluminum sheets",
            "weight": 8.2,
            "dimensions": "50x30x10",
            "fragile": False
        },
        "recipient": {
            "name": "Ahmad Suryadi",
            "email": "ahmad@example.com",
            "phone": "081234567890",
            "address": "Jl. Sudirman No. 123, Jakarta Pusat"
        },
        "seller": {
            "name": "Metal Supplies Co.",
            "email": "sales@metalsupplies.com",
            "phone": "021-5551234"
        },
        "destination_code": 11002,
        "current_status": "placed",
        "tracking_events": [
            {
                "id": 1,
                "location": "Warehouse Jakarta",
                "description": "Package received at warehouse",
                "status": "placed",
                "timestamp": datetime(2024, 12, 1, 9, 0, 0)
            }
        ],
        "created_at": datetime(2024, 12, 1, 9, 0, 0),
        "updated_at": datetime(2024, 12, 1, 9, 0, 0)
    },
    12702: {
        "package_details": {
            "content": "steel rods",
            "weight": 14.7,
            "dimensions": "200x10x10",
            "fragile": False
        },
        "recipient": {
            "name": "Budi Santoso",
            "email": "budi@example.com",
            "phone": "082345678901",
            "address": "Jl. Industri No. 45, Surabaya"
        },
        "seller": {
            "name": "Steel Works Ltd.",
            "email": "info@steelworks.com",
            "phone": "031-7771234"
        },
        "destination_code": 11003,
        "current_status": "in_transit",
        "tracking_events": [
            {
                "id": 2,
                "location": "Distribution Center Surabaya",
                "description": "In transit to destination",
                "status": "in_transit",
                "timestamp": datetime(2024, 12, 1, 10, 30, 0)
            }
        ],
        "created_at": datetime(2024, 12, 1, 8, 0, 0),
        "updated_at": datetime(2024, 12, 1, 10, 30, 0)
    },
    12703: {
        "package_details": {
            "content": "copper wires",
            "weight": 11.4,
            "dimensions": "40x40x20",
            "fragile": True
        },
        "recipient": {
            "name": "Siti Nurhaliza",
            "email": "siti@example.com",
            "phone": "083456789012",
            "address": "Jl. Merdeka No. 78, Jakarta Selatan"
        },
        "seller": {
            "name": "Copper Tech Inc.",
            "email": "sales@coppertech.com",
            "phone": "021-8881234"
        },
        "destination_code": 11002,
        "current_status": "delivered",
        "tracking_events": [
            {
                "id": 3,
                "location": "Customer Address",
                "description": "Package delivered successfully",
                "status": "delivered",
                "timestamp": datetime(2024, 11, 30, 15, 45, 0)
            }
        ],
        "created_at": datetime(2024, 11, 29, 10, 0, 0),
        "updated_at": datetime(2024, 11, 30, 15, 45, 0)
    }
}

tracking_event_counter = 4  # Counter untuk ID tracking events


# === SHIPMENT ENDPOINTS (Aggregate Root Operations) ===

@app.get("/", tags=["Root"])
def root():
    """Root endpoint - API information"""
    return {
        "message": "LOGIXPress API - Shipment Lifecycle Management",
        "version": "1.0.0",
        "bounded_context": "Shipment Lifecycle Management (Core Domain)",
        "docs": "/docs",
        "scalar_docs": "/scalar"
    }


@app.get("/shipments", response_model=List[ShipmentSummary], tags=["Shipments"])
def get_all_shipments(
    status: Optional[ShipmentStatus] = Query(None, description="Filter by shipment status"),
    destination_code: Optional[int] = Query(None, description="Filter by destination code"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results")
):
    """
    **C0102: Shipment Tracking & Status Update**
    
    Mengambil daftar shipment dengan opsi filtering berdasarkan status dan destination.
    Mengembalikan summary view untuk efisiensi.
    """
    result = []
    
    for shipment_id, shipment_data in shipments.items():
        # Apply filters
        if status and shipment_data["current_status"] != status:
            continue
        if destination_code and shipment_data["destination_code"] != destination_code:
            continue
        
        result.append(ShipmentSummary(
            id=shipment_id,
            content=shipment_data["package_details"]["content"],
            weight=shipment_data["package_details"]["weight"],
            current_status=shipment_data["current_status"],
            destination_code=shipment_data["destination_code"],
            recipient_name=shipment_data["recipient"]["name"],
            created_at=shipment_data["created_at"]
        ))
        
        if len(result) >= limit:
            break
    
    return result


@app.get("/shipment/{shipment_id}", response_model=ShipmentRead, tags=["Shipments"])
def get_shipment_by_id(shipment_id: int):
    """
    **C0102: Shipment Tracking & Status Update**
    
    Mengambil detail lengkap shipment berdasarkan Tracking Number (ID).
    Mengembalikan Aggregate Root lengkap dengan semua Value Objects dan Tracking Events.
    """
    if shipment_id not in shipments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shipment with tracking number {shipment_id} not found"
        )
    
    shipment_data = shipments[shipment_id]
    
    return ShipmentRead(
        id=shipment_id,
        package_details=PackageDetails(**shipment_data["package_details"]),
        recipient=Recipient(**shipment_data["recipient"]),
        seller=Seller(**shipment_data["seller"]),
        destination_code=shipment_data["destination_code"],
        current_status=shipment_data["current_status"],
        tracking_events=[TrackingEvent(**event) for event in shipment_data["tracking_events"]],
        created_at=shipment_data["created_at"],
        updated_at=shipment_data["updated_at"]
    )


@app.post("/shipment", response_model=dict[str, int], status_code=status.HTTP_201_CREATED, tags=["Shipments"])
def create_shipment(shipment: ShipmentCreate):
    """
    **C0101: Shipment Order Creation**
    
    Membuat shipment baru (Aggregate Root).
    Status awal selalu 'placed' dan tracking event pertama dibuat otomatis.
    """
    global tracking_event_counter
    
    # Generate new Tracking Number (ID)
    new_id = max(shipments.keys()) + 1 if shipments else 1
    now = datetime.now()
    
    # Create initial tracking event
    initial_event = {
        "id": tracking_event_counter,
        "location": "Warehouse",
        "description": "Shipment order created and received at warehouse",
        "status": "placed",
        "timestamp": now
    }
    tracking_event_counter += 1
    
    # Create Aggregate Root
    shipments[new_id] = {
        "package_details": shipment.package_details.model_dump(),
        "recipient": shipment.recipient.model_dump(),
        "seller": shipment.seller.model_dump(),
        "destination_code": shipment.destination_code,
        "current_status": "placed",
        "tracking_events": [initial_event],
        "created_at": now,
        "updated_at": now
    }
    
    return {"id": new_id, "message": "Shipment created successfully"}


@app.patch("/shipment/{shipment_id}", response_model=ShipmentRead, tags=["Shipments"])
def update_shipment(shipment_id: int, update_data: ShipmentUpdate):
    """
    **C0102: Shipment Tracking & Status Update**
    
    Update shipment details. Jika status berubah, tracking event baru akan dibuat.
    Hanya Aggregate Root yang boleh memodifikasi Internal Entities.
    """
    global tracking_event_counter
    
    if shipment_id not in shipments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shipment {shipment_id} not found"
        )
    
    shipment = shipments[shipment_id]
    update_dict = update_data.model_dump(exclude_none=True)
    
    # Check if status is being updated
    status_changed = False
    if "current_status" in update_dict:
        new_status = update_dict["current_status"]
        if new_status != shipment["current_status"]:
            status_changed = True
            old_status = shipment["current_status"]
            
            # Validate status transition (basic validation)
            valid_transitions = {
                "placed": ["in_transit", "cancelled"],
                "in_transit": ["out_for_delivery", "returned"],
                "out_for_delivery": ["delivered", "returned"],
                "delivered": [],
                "cancelled": [],
                "returned": []
            }
            
            if new_status not in valid_transitions.get(old_status, []):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status transition from {old_status} to {new_status}"
                )
    
    # Update fields
    if "package_details" in update_dict:
        shipment["package_details"].update(update_dict["package_details"])
    if "recipient" in update_dict:
        shipment["recipient"].update(update_dict["recipient"])
    if "destination_code" in update_dict:
        shipment["destination_code"] = update_dict["destination_code"]
    if "current_status" in update_dict:
        shipment["current_status"] = update_dict["current_status"]
    
    shipment["updated_at"] = datetime.now()
    
    # Add tracking event if status changed
    if status_changed:
        location_map = {
            "in_transit": "Distribution Center",
            "out_for_delivery": "Local Hub",
            "delivered": "Customer Address",
            "returned": "Return Center",
            "cancelled": "Warehouse"
        }
        
        new_event = {
            "id": tracking_event_counter,
            "location": location_map.get(new_status, "Unknown"),
            "description": f"Status changed to {new_status}",
            "status": new_status,
            "timestamp": datetime.now()
        }
        tracking_event_counter += 1
        shipment["tracking_events"].append(new_event)
    
    return get_shipment_by_id(shipment_id)


@app.delete("/shipment/{shipment_id}", tags=["Shipments"])
def delete_shipment(shipment_id: int):
    """Delete a shipment (for admin purposes only)"""
    if shipment_id not in shipments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shipment {shipment_id} not found"
        )
    
    shipments.pop(shipment_id)
    return {"message": f"Shipment {shipment_id} deleted successfully"}


# === TRACKING EVENTS ENDPOINTS (Internal Entity Operations) ===

@app.get("/shipment/{shipment_id}/tracking", response_model=List[TrackingEvent], tags=["Tracking"])
def get_shipment_tracking_history(shipment_id: int):
    """
    **C0102: Shipment Tracking & Status Update**
    
    Mengambil riwayat tracking events (timeline) dari suatu shipment.
    Tracking Event adalah Internal Entity yang hanya dapat diakses melalui Aggregate Root.
    """
    if shipment_id not in shipments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shipment {shipment_id} not found"
        )
    
    events = shipments[shipment_id]["tracking_events"]
    return [TrackingEvent(**event) for event in events]


@app.post("/shipment/{shipment_id}/tracking", response_model=TrackingEvent, status_code=status.HTTP_201_CREATED, tags=["Tracking"])
def add_tracking_event(shipment_id: int, event: TrackingEventCreate):
    """
    **C0102: Shipment Tracking & Status Update**
    
    Menambahkan tracking event baru ke shipment.
    Event hanya bisa ditambahkan melalui Aggregate Root untuk menjaga konsistensi.
    """
    global tracking_event_counter
    
    if shipment_id not in shipments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shipment {shipment_id} not found"
        )
    
    shipment = shipments[shipment_id]
    
    # Create new tracking event
    new_event = {
        "id": tracking_event_counter,
        "location": event.location,
        "description": event.description,
        "status": event.status,
        "timestamp": datetime.now()
    }
    tracking_event_counter += 1
    
    # Add to shipment's tracking events
    shipment["tracking_events"].append(new_event)
    
    # Update current status if different
    if event.status != shipment["current_status"]:
        shipment["current_status"] = event.status
        shipment["updated_at"] = datetime.now()
    
    return TrackingEvent(**new_event)


# === STATISTICS & REPORTING ===

@app.get("/stats", tags=["Statistics"])
def get_shipment_statistics():
    """
    **C0601: Performance Reporting Management**
    
    Mendapatkan statistik agregat dari seluruh shipment.
    """
    if not shipments:
        return {
            "total_shipments": 0,
            "by_status": {},
            "total_weight": 0.0,
            "avg_weight": 0.0
        }
    
    status_count = {}
    total_weight = 0.0
    
    for shipment in shipments.values():
        status_key = shipment["current_status"]
        status_count[status_key] = status_count.get(status_key, 0) + 1
        total_weight += shipment["package_details"]["weight"]
    
    return {
        "total_shipments": len(shipments),
        "by_status": status_count,
        "total_weight": round(total_weight, 2),
        "avg_weight": round(total_weight / len(shipments), 2)
    }


@app.get("/health", tags=["Health"])
def health_check():
    """API health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "total_shipments": len(shipments),
        "bounded_context": "Shipment Lifecycle Management"
    }


# === API DOCUMENTATION ===

@app.get("/scalar", include_in_schema=False)
def get_scalar_docs():
    """Scalar API Documentation"""
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="LOGIXPress API Documentation",
    )
