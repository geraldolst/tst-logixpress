"""
Shipment Service

Business logic for shipment management including CRUD operations,
status transitions, and tracking events.
"""

from datetime import datetime
from typing import Optional

from app.api.schemas.shipment import (
    PackageDetails,
    Recipient,
    Seller,
    ShipmentCreate,
    ShipmentRead,
    ShipmentSummary,
    ShipmentUpdate,
    TrackingEvent,
    TrackingEventCreate,
)
from app.core.exceptions import EntityNotFound, InvalidStatusTransition
from app.models.shipment import ShipmentStatus

# In-memory shipment storage (simulating database)
# In production, this would be replaced with actual database
shipments_db = {}
tracking_event_counter = 1


class ShipmentService:
    """Service for shipment business logic"""

    @staticmethod
    def get_all_shipments(
        status_filter: Optional[ShipmentStatus] = None, destination_filter: Optional[int] = None, limit: int = 10
    ) -> list[ShipmentSummary]:
        """
        Get all shipments with optional filters

        Args:
            status_filter: Filter by status
            destination_filter: Filter by destination code
            limit: Maximum number of results

        Returns:
            List of shipment summaries
        """
        result = []

        for shipment_id, shipment_data in shipments_db.items():
            # Apply filters
            if status_filter and shipment_data["current_status"] != status_filter.value:
                continue
            if destination_filter and shipment_data["destination_code"] != destination_filter:
                continue

            # Create summary
            summary = ShipmentSummary(
                id=shipment_id,
                content=shipment_data["package_details"]["content"],
                weight=shipment_data["package_details"]["weight"],
                current_status=shipment_data["current_status"],
                destination_code=shipment_data["destination_code"],
                recipient_name=shipment_data["recipient"]["name"],
                created_at=shipment_data["created_at"],
            )
            result.append(summary)

            if len(result) >= limit:
                break

        return result

    @staticmethod
    def get_shipment_by_id(shipment_id: int) -> ShipmentRead:
        """
        Get shipment by ID

        Args:
            shipment_id: Shipment tracking number

        Returns:
            Full shipment details

        Raises:
            EntityNotFound: If shipment not found
        """
        if shipment_id not in shipments_db:
            raise EntityNotFound("Shipment", shipment_id)

        shipment_data = shipments_db[shipment_id]

        return ShipmentRead(
            id=shipment_id,
            package_details=PackageDetails(**shipment_data["package_details"]),
            recipient=Recipient(**shipment_data["recipient"]),
            seller=Seller(**shipment_data["seller"]),
            destination_code=shipment_data["destination_code"],
            current_status=shipment_data["current_status"],
            tracking_events=[TrackingEvent(**event) for event in shipment_data["tracking_events"]],
            created_at=shipment_data["created_at"],
            updated_at=shipment_data["updated_at"],
        )

    @staticmethod
    def create_shipment(shipment_data: ShipmentCreate) -> dict:
        """
        Create a new shipment

        Args:
            shipment_data: Shipment creation data

        Returns:
            Dictionary with shipment ID and message
        """
        global tracking_event_counter

        # Generate new ID
        new_id = max(shipments_db.keys()) + 1 if shipments_db else 12701
        now = datetime.now()

        # Create initial tracking event
        initial_event = {
            "id": tracking_event_counter,
            "location": "Warehouse",
            "description": "Shipment order created and received at warehouse",
            "status": ShipmentStatus.placed.value,
            "timestamp": now,
        }
        tracking_event_counter += 1

        # Store shipment
        shipments_db[new_id] = {
            "package_details": shipment_data.package_details.model_dump(),
            "recipient": shipment_data.recipient.model_dump(),
            "seller": shipment_data.seller.model_dump(),
            "destination_code": shipment_data.destination_code,
            "current_status": ShipmentStatus.placed.value,
            "tracking_events": [initial_event],
            "created_at": now,
            "updated_at": now,
        }

        return {"id": new_id, "message": "Shipment created successfully"}

    @staticmethod
    def update_shipment(shipment_id: int, update_data: ShipmentUpdate) -> ShipmentRead:
        """
        Update shipment

        Args:
            shipment_id: Shipment ID to update
            update_data: Update data

        Returns:
            Updated shipment

        Raises:
            EntityNotFound: If shipment not found
            InvalidStatusTransition: If status transition is invalid
        """
        global tracking_event_counter

        if shipment_id not in shipments_db:
            raise EntityNotFound("Shipment", shipment_id)

        shipment = shipments_db[shipment_id]
        update_dict = update_data.model_dump(exclude_none=True)

        # Handle status update with validation
        if "current_status" in update_dict:
            current_status = ShipmentStatus(shipment["current_status"])
            new_status = update_dict["current_status"]

            # Validate transition
            if not current_status.can_transition_to(new_status):
                valid_transitions = ShipmentStatus.get_valid_transitions()
                valid_next = ", ".join(valid_transitions[current_status.value])
                raise InvalidStatusTransition(current_status.value, new_status.value, valid_next)

            # Create tracking event for status change
            new_event = {
                "id": tracking_event_counter,
                "location": "In Transit",
                "description": f"Status updated to {new_status.value}",
                "status": new_status.value,
                "timestamp": datetime.now(),
            }
            tracking_event_counter += 1
            shipment["tracking_events"].append(new_event)

        # Update fields
        if "package_details" in update_dict:
            if isinstance(update_dict["package_details"], dict):
                shipment["package_details"].update(update_dict["package_details"])
            else:
                shipment["package_details"].update(update_dict["package_details"].model_dump())
        if "recipient" in update_dict:
            if isinstance(update_dict["recipient"], dict):
                shipment["recipient"].update(update_dict["recipient"])
            else:
                shipment["recipient"].update(update_dict["recipient"].model_dump())
        if "destination_code" in update_dict:
            shipment["destination_code"] = update_dict["destination_code"]
        if "current_status" in update_dict:
            if isinstance(update_dict["current_status"], str):
                shipment["current_status"] = update_dict["current_status"]
            else:
                shipment["current_status"] = update_dict["current_status"].value

        shipment["updated_at"] = datetime.now()

        return ShipmentService.get_shipment_by_id(shipment_id)

    @staticmethod
    def delete_shipment(shipment_id: int) -> dict:
        """
        Delete shipment

        Args:
            shipment_id: Shipment ID to delete

        Returns:
            Success message

        Raises:
            EntityNotFound: If shipment not found
        """
        if shipment_id not in shipments_db:
            raise EntityNotFound("Shipment", shipment_id)

        del shipments_db[shipment_id]
        return {"message": f"Shipment with tracking number {shipment_id} has been deleted"}

    @staticmethod
    def add_tracking_event(shipment_id: int, event_data: TrackingEventCreate) -> TrackingEvent:
        """
        Add tracking event to shipment

        Args:
            shipment_id: Shipment ID
            event_data: Tracking event data

        Returns:
            Created tracking event

        Raises:
            EntityNotFound: If shipment not found
        """
        global tracking_event_counter

        if shipment_id not in shipments_db:
            raise EntityNotFound("Shipment", shipment_id)

        shipment = shipments_db[shipment_id]

        new_event = {
            "id": tracking_event_counter,
            "location": event_data.location,
            "description": event_data.description,
            "status": event_data.status.value,
            "timestamp": datetime.now(),
        }
        tracking_event_counter += 1

        shipment["tracking_events"].append(new_event)
        shipment["current_status"] = event_data.status.value
        shipment["updated_at"] = datetime.now()

        return TrackingEvent(**new_event)

    @staticmethod
    def get_tracking_history(shipment_id: int) -> list[TrackingEvent]:
        """
        Get tracking history for shipment

        Args:
            shipment_id: Shipment ID

        Returns:
            List of tracking events

        Raises:
            EntityNotFound: If shipment not found
        """
        if shipment_id not in shipments_db:
            raise EntityNotFound("Shipment", shipment_id)

        shipment = shipments_db[shipment_id]
        return [TrackingEvent(**event) for event in shipment["tracking_events"]]


# Initialize with sample data
def initialize_sample_data():
    """Initialize database with sample shipments"""
    global shipments_db, tracking_event_counter

    shipments_db = {
        12701: {
            "package_details": {
                "content": "aluminum sheets",
                "weight": 8.2,
                "dimensions": "50x30x10",
                "fragile": False,
            },
            "recipient": {
                "name": "Ahmad Suryadi",
                "email": "ahmad@example.com",
                "phone": "081234567890",
                "address": "Jl. Sudirman No. 123, Jakarta Pusat",
            },
            "seller": {"name": "Metal Supplies Co.", "email": "sales@metalsupplies.com", "phone": "021-5551234"},
            "destination_code": 11002,
            "current_status": "placed",
            "tracking_events": [
                {
                    "id": 1,
                    "location": "Warehouse Jakarta",
                    "description": "Package received at warehouse",
                    "status": "placed",
                    "timestamp": datetime(2024, 12, 1, 9, 0, 0),
                }
            ],
            "created_at": datetime(2024, 12, 1, 9, 0, 0),
            "updated_at": datetime(2024, 12, 1, 9, 0, 0),
        },
        12702: {
            "package_details": {"content": "steel rods", "weight": 14.7, "dimensions": "200x10x10", "fragile": False},
            "recipient": {
                "name": "Budi Santoso",
                "email": "budi@example.com",
                "phone": "082345678901",
                "address": "Jl. Industri No. 45, Surabaya",
            },
            "seller": {"name": "Steel Works Ltd.", "email": "info@steelworks.com", "phone": "031-7771234"},
            "destination_code": 11003,
            "current_status": "in_transit",
            "tracking_events": [
                {
                    "id": 2,
                    "location": "Distribution Center Surabaya",
                    "description": "In transit to destination",
                    "status": "in_transit",
                    "timestamp": datetime(2024, 12, 1, 10, 30, 0),
                }
            ],
            "created_at": datetime(2024, 12, 1, 8, 0, 0),
            "updated_at": datetime(2024, 12, 1, 10, 30, 0),
        },
        12703: {
            "package_details": {"content": "copper wires", "weight": 11.4, "dimensions": "40x40x20", "fragile": True},
            "recipient": {
                "name": "Siti Nurhaliza",
                "email": "siti@example.com",
                "phone": "083456789012",
                "address": "Jl. Merdeka No. 78, Jakarta Selatan",
            },
            "seller": {"name": "Copper Tech Inc.", "email": "sales@coppertech.com", "phone": "021-8881234"},
            "destination_code": 11002,
            "current_status": "delivered",
            "tracking_events": [
                {
                    "id": 3,
                    "location": "Customer Address",
                    "description": "Package delivered successfully",
                    "status": "delivered",
                    "timestamp": datetime(2024, 11, 30, 15, 45, 0),
                }
            ],
            "created_at": datetime(2024, 11, 29, 10, 0, 0),
            "updated_at": datetime(2024, 11, 30, 15, 45, 0),
        },
    }

    tracking_event_counter = 4


# Initialize sample data on module load
initialize_sample_data()
