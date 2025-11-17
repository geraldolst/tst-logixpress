from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional


class ShipmentStatus(str, Enum):
    placed = "placed"
    in_transit = "in_transit"
    out_for_delivery = "out_for_delivery"
    delivered = "delivered"


class BaseShipment(BaseModel):
    content: str = Field(description="Content description")
    weight: float = Field(le=25, gt=0, description="Weight must be between 0-25kg")
    destination: int = Field(description="Destination code")


class ShipmentRead(BaseShipment):
    status: ShipmentStatus


class ShipmentCreate(BaseShipment):
    pass
    

class ShipmentUpdate(BaseModel):
    content: Optional[str] = Field(default=None)
    weight: Optional[float] = Field(default=None, le=25, gt=0)
    destination: Optional[int] = Field(default=None)
    status: Optional[ShipmentStatus] = Field(default=None)