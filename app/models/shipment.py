"""
Shipment Domain Models

Contains domain models and enums for the shipment bounded context.
"""

from enum import Enum


class ShipmentStatus(str, Enum):
    """Status pengiriman - Value Object (Enum)"""
    placed = "placed"
    in_transit = "in_transit"
    out_for_delivery = "out_for_delivery"
    delivered = "delivered"
    returned = "returned"
    cancelled = "cancelled"
    
    @classmethod
    def get_valid_transitions(cls) -> dict[str, list[str]]:
        """
        Define valid status transitions
        
        Returns:
            Dictionary mapping current status to list of valid next statuses
        """
        return {
            cls.placed.value: [cls.in_transit.value, cls.cancelled.value],
            cls.in_transit.value: [cls.out_for_delivery.value, cls.returned.value, cls.cancelled.value],
            cls.out_for_delivery.value: [cls.delivered.value, cls.returned.value],
            cls.delivered.value: [],  # Terminal state
            cls.returned.value: [],  # Terminal state
            cls.cancelled.value: [],  # Terminal state
        }
    
    def can_transition_to(self, new_status: "ShipmentStatus") -> bool:
        """
        Check if transition to new status is valid
        
        Args:
            new_status: Target status
            
        Returns:
            True if transition is valid, False otherwise
        """
        transitions = self.get_valid_transitions()
        return new_status.value in transitions.get(self.value, [])
