"""
Shipment Schemas

Request and response models for shipment and tracking endpoints.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

from app.models.shipment import ShipmentStatus


# === VALUE OBJECTS (Pydantic Models) ===
class Recipient(BaseModel):
    """Informasi penerima - Value Object"""
    name: str = Field(..., min_length=1, description="Nama penerima")
    email: EmailStr = Field(..., description="Email penerima")
    phone: str = Field(..., description="Nomor telepon penerima")
    address: str = Field(..., description="Alamat lengkap penerima")


class Seller(BaseModel):
    """Informasi pengirim/seller - Value Object"""
    name: str = Field(..., description="Nama seller")
    email: EmailStr = Field(..., description="Email seller")
    phone: str = Field(..., description="Nomor telepon seller")


class PackageDetails(BaseModel):
    """Detail paket - Value Object"""
    content: str = Field(..., min_length=1, description="Deskripsi isi paket")
    weight: float = Field(..., gt=0, le=25, description="Berat paket (kg), max 25kg")
    dimensions: Optional[str] = Field(None, description="Dimensi paket (PxLxT cm)")
    fragile: bool = Field(default=False, description="Apakah barang mudah pecah")


# === ENTITIES ===
class TrackingEvent(BaseModel):
    """Tracking Event - Internal Entity dalam Aggregate Shipment"""
    id: int
    location: str = Field(..., description="Lokasi kejadian")
    description: str = Field(..., description="Deskripsi kejadian")
    status: ShipmentStatus
    timestamp: datetime = Field(default_factory=datetime.now)


class TrackingEventCreate(BaseModel):
    """Schema untuk membuat tracking event baru"""
    location: str = Field(..., description="Lokasi kejadian")
    description: str = Field(..., description="Deskripsi kejadian")
    status: ShipmentStatus


# === AGGREGATE ROOT: Shipment Schemas ===
class ShipmentBase(BaseModel):
    """Base schema untuk Shipment"""
    package_details: PackageDetails
    recipient: Recipient
    destination_code: int = Field(..., description="Kode tujuan pengiriman")


class ShipmentCreate(ShipmentBase):
    """Schema untuk membuat shipment baru"""
    seller: Seller


class ShipmentRead(ShipmentBase):
    """Schema untuk membaca shipment - Aggregate Root"""
    id: int = Field(..., description="Tracking Number / Shipment ID")
    seller: Seller
    current_status: ShipmentStatus
    tracking_events: List[TrackingEvent] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class ShipmentUpdate(BaseModel):
    """Schema untuk update shipment"""
    package_details: Optional[PackageDetails] = None
    recipient: Optional[Recipient] = None
    destination_code: Optional[int] = None
    current_status: Optional[ShipmentStatus] = None


class ShipmentSummary(BaseModel):
    """Schema ringkasan shipment untuk list view"""
    id: int
    content: str
    weight: float
    current_status: ShipmentStatus
    destination_code: int
    recipient_name: str
    created_at: datetime


class ShipmentCreationResponse(BaseModel):
    """Response when creating a new shipment"""
    id: int
    message: str
