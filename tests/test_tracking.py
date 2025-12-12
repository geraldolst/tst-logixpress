"""
Tracking Tests

Tests for tracking event operations and history.
Covers: adding events, retrieving history, permissions.
"""

import pytest


class TestTrackingOperations:
    """Test tracking event operations"""
    
    def test_get_tracking_history(self, client, admin_token, reset_db):
        """Test getting tracking history for shipment"""
        response = client.get(
            "/shipment/12701/tracking",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert "location" in data[0]
        assert "description" in data[0]
        assert "status" in data[0]
    
    def test_get_tracking_history_not_found(self, client, admin_token, reset_db):
        """Test getting tracking for non-existent shipment"""
        response = client.get(
            "/shipment/99999/tracking",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 404
    
    def test_add_tracking_event_as_courier(self, client, courier_token, reset_db):
        """Test adding tracking event as courier"""
        response = client.post(
            "/shipment/12701/tracking",
            json={
                "location": "Distribution Center",
                "description": "Package sorted",
                "status": "in_transit"
            },
            headers={"Authorization": f"Bearer {courier_token}"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["location"] == "Distribution Center"
        assert data["status"] == "in_transit"
        assert "timestamp" in data
    
    def test_add_tracking_event_as_admin(self, client, admin_token, reset_db):
        """Test adding tracking event as admin"""
        response = client.post(
            "/shipment/12701/tracking",
            json={
                "location": "Test Location",
                "description": "Test event",
                "status": "in_transit"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 201
    
    def test_add_tracking_event_as_customer_forbidden(self, client, customer_token, reset_db):
        """Test customer cannot add tracking events"""
        response = client.post(
            "/shipment/12701/tracking",
            json={
                "location": "Test",
                "description": "Test",
                "status": "in_transit"
            },
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        assert response.status_code == 403
    
    def test_add_tracking_event_updates_shipment_status(self, client, courier_token, admin_token, reset_db):
        """Test adding tracking event updates shipment status"""
        # Add tracking event
        client.post(
            "/shipment/12701/tracking",
            json={
                "location": "On delivery vehicle",
                "description": "Out for delivery",
                "status": "out_for_delivery"
            },
            headers={"Authorization": f"Bearer {courier_token}"}
        )
        
        # Check shipment status updated
        response = client.get(
            "/shipment/12701",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.json()["current_status"] == "out_for_delivery"
    
    def test_add_tracking_event_invalid_status(self, client, courier_token, reset_db):
        """Test adding tracking event with invalid status"""
        response = client.post(
            "/shipment/12701/tracking",
            json={
                "location": "Test",
                "description": "Test",
                "status": "invalid_status"
            },
            headers={"Authorization": f"Bearer {courier_token}"}
        )
        assert response.status_code == 422
    
    def test_add_tracking_event_missing_fields(self, client, courier_token, reset_db):
        """Test adding tracking event with missing fields"""
        response = client.post(
            "/shipment/12701/tracking",
            json={"location": "Test"},
            headers={"Authorization": f"Bearer {courier_token}"}
        )
        assert response.status_code == 422
    
    def test_tracking_history_chronological_order(self, client, courier_token, admin_token, reset_db):
        """Test tracking events are in chronological order"""
        # Add multiple events
        for i in range(3):
            client.post(
                "/shipment/12701/tracking",
                json={
                    "location": f"Location {i}",
                    "description": f"Event {i}",
                    "status": "in_transit"
                },
                headers={"Authorization": f"Bearer {courier_token}"}
            )
        
        # Get history
        response = client.get(
            "/shipment/12701/tracking",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        events = response.json()
        
        # Check chronological order (oldest first)
        for i in range(len(events) - 1):
            assert events[i]["timestamp"] <= events[i + 1]["timestamp"]
