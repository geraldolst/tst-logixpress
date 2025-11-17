from fastapi import FastAPI, HTTPException, status, Query
from scalar_fastapi import get_scalar_api_reference
from typing import List, Optional

from .schemas import ShipmentCreate, ShipmentRead, ShipmentUpdate, ShipmentStatus

app = FastAPI(
    title="LogixPress API",
    description="A simple logistics management API inspired by FastShip",
    version="1.0.0"
)

### Shipments datastore
shipments = {
    12701: {"weight": 8.2, "content": "aluminum sheets", "status": "placed", "destination": 11002},
    12702: {"weight": 14.7, "content": "steel rods", "status": "in_transit", "destination": 11003},
    12703: {"weight": 11.4, "content": "copper wires", "status": "delivered", "destination": 11002},
    12704: {"weight": 17.8, "content": "iron plates", "status": "out_for_delivery", "destination": 11005},
    12705: {"weight": 10.3, "content": "brass fittings", "status": "placed", "destination": 11008},
}


### Get all shipments or filter by status
@app.get("/shipments", response_model=List[ShipmentRead])
def get_shipments(status: Optional[ShipmentStatus] = Query(None)):
    """Get all shipments or filter by status"""
    result = []
    for shipment_id, shipment_data in shipments.items():
        if status is None or shipment_data["status"] == status:
            result.append({
                "content": shipment_data["content"],
                "weight": shipment_data["weight"],
                "destination": shipment_data["destination"],
                "status": shipment_data["status"]
            })
    return result


### Get a shipment by id
@app.get("/shipment", response_model=ShipmentRead)
def get_shipment(id: int):
    """Get a specific shipment by ID"""
    if id not in shipments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shipment not found"
        )
    
    shipment = shipments[id]
    return ShipmentRead(
        content=shipment["content"],
        weight=shipment["weight"],
        destination=shipment["destination"],
        status=shipment["status"]
    )


### Create a new shipment
@app.post("/shipment", response_model=dict[str, int], status_code=status.HTTP_201_CREATED)
def submit_shipment(shipment: ShipmentCreate) -> dict[str, int]:
    """Create a new shipment"""
    # Generate new ID
    new_id = max(shipments.keys()) + 1 if shipments else 1
    
    # Add shipment with default status
    shipments[new_id] = {
        **shipment.model_dump(),
        "status": "placed"
    }
    
    return {"id": new_id}


### Update shipment fields
@app.patch("/shipment", response_model=ShipmentRead)
def update_shipment(id: int, body: ShipmentUpdate):
    """Update shipment details"""
    if id not in shipments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shipment not found"
        )
    
    # Update only provided fields
    update_data = body.model_dump(exclude_none=True)
    shipments[id].update(update_data)
    
    return ShipmentRead(
        content=shipments[id]["content"],
        weight=shipments[id]["weight"],
        destination=shipments[id]["destination"],
        status=shipments[id]["status"]
    )


### Delete a shipment
@app.delete("/shipment")
def delete_shipment(id: int) -> dict[str, str]:
    """Delete a shipment by ID"""
    if id not in shipments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shipment not found"
        )
    
    shipments.pop(id)
    return {"detail": f"Shipment with id #{id} deleted successfully"}


### Get shipment count by status
@app.get("/shipments/stats")
def get_shipment_stats():
    """Get shipment statistics"""
    stats = {}
    total = 0
    
    for shipment in shipments.values():
        status_key = shipment["status"]
        stats[status_key] = stats.get(status_key, 0) + 1
        total += 1
    
    return {
        "total_shipments": total,
        "by_status": stats
    }


### Get shipments by destination
@app.get("/shipments/destination/{destination_id}", response_model=List[ShipmentRead])
def get_shipments_by_destination(destination_id: int):
    """Get all shipments for a specific destination"""
    result = []
    
    for shipment_data in shipments.values():
        if shipment_data["destination"] == destination_id:
            result.append(ShipmentRead(
                content=shipment_data["content"],
                weight=shipment_data["weight"],
                destination=shipment_data["destination"],
                status=shipment_data["status"]
            ))
    
    return result

### API Documentation with Scalar
@app.get("/scalar", include_in_schema=False)
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="LogixPress API Documentation",
    )