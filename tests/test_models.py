"""
Model Tests

Tests for domain models and business logic.
"""

import pytest
from app.models.shipment import ShipmentStatus


class TestShipmentStatus:
    """Test ShipmentStatus enum and transitions"""
    
    def test_status_values(self):
        """Test all status values are defined"""
        assert ShipmentStatus.placed.value == "placed"
        assert ShipmentStatus.in_transit.value == "in_transit"
        assert ShipmentStatus.out_for_delivery.value == "out_for_delivery"
        assert ShipmentStatus.delivered.value == "delivered"
        assert ShipmentStatus.returned.value == "returned"
        assert ShipmentStatus.cancelled.value == "cancelled"
    
    def test_valid_transitions(self):
        """Test valid status transitions"""
        transitions = ShipmentStatus.get_valid_transitions()
        
        # Test placed transitions
        assert "in_transit" in transitions["placed"]
        assert "cancelled" in transitions["placed"]
        
        # Test in_transit transitions
        assert "out_for_delivery" in transitions["in_transit"]
        assert "returned" in transitions["in_transit"]
        
        # Test out_for_delivery transitions
        assert "delivered" in transitions["out_for_delivery"]
        assert "returned" in transitions["out_for_delivery"]
        
        # Test terminal states have no transitions
        assert transitions["delivered"] == []
        assert transitions["returned"] == []
        assert transitions["cancelled"] == []
    
    def test_can_transition_to_valid(self):
        """Test can_transition_to with valid transitions"""
        assert ShipmentStatus.placed.can_transition_to(ShipmentStatus.in_transit) is True
        assert ShipmentStatus.in_transit.can_transition_to(ShipmentStatus.out_for_delivery) is True
        assert ShipmentStatus.out_for_delivery.can_transition_to(ShipmentStatus.delivered) is True
    
    def test_can_transition_to_invalid(self):
        """Test can_transition_to with invalid transitions"""
        assert ShipmentStatus.placed.can_transition_to(ShipmentStatus.delivered) is False
        assert ShipmentStatus.delivered.can_transition_to(ShipmentStatus.in_transit) is False
        assert ShipmentStatus.cancelled.can_transition_to(ShipmentStatus.placed) is False
    
    def test_terminal_states_no_transitions(self):
        """Test terminal states cannot transition"""
        terminal_states = [ShipmentStatus.delivered, ShipmentStatus.returned, ShipmentStatus.cancelled]
        for status in terminal_states:
            for target in ShipmentStatus:
                assert status.can_transition_to(target) is False
