"""
Shipment Tests

Tests for shipment CRUD operations, status transitions, and permissions.
Covers: create, read, update, delete, filtering, role-based access.
"""

import pytest


class TestShipmentCRUD:
    """Test shipment CRUD operations"""
    
    def test_create_shipment_as_admin(self, client, admin_token, sample_shipment_data, reset_db):
        """Test shipment creation by admin"""
        response = client.post(
            "/shipment",
            json=sample_shipment_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["message"] == "Shipment created successfully"
    
    def test_create_shipment_as_customer(self, client, customer_token, sample_shipment_data, reset_db):
        """Test shipment creation by customer"""
        response = client.post(
            "/shipment",
            json=sample_shipment_data,
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        assert response.status_code == 201
    
    def test_create_shipment_as_courier_forbidden(self, client, courier_token, sample_shipment_data, reset_db):
        """Test shipment creation by courier (should fail)"""
        response = client.post(
            "/shipment",
            json=sample_shipment_data,
            headers={"Authorization": f"Bearer {courier_token}"}
        )
        assert response.status_code == 403
        assert "Required roles" in response.json()["detail"]
    
    def test_create_shipment_no_auth(self, client, sample_shipment_data, reset_db):
        """Test shipment creation without authentication"""
        response = client.post("/shipment", json=sample_shipment_data)
        assert response.status_code == 403
    
    def test_create_shipment_invalid_weight(self, client, admin_token, sample_shipment_data, reset_db):
        """Test shipment creation with weight > 25kg"""
        sample_shipment_data["package_details"]["weight"] = 30.0
        response = client.post(
            "/shipment",
            json=sample_shipment_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 422
    
    def test_create_shipment_negative_weight(self, client, admin_token, sample_shipment_data, reset_db):
        """Test shipment creation with negative weight"""
        sample_shipment_data["package_details"]["weight"] = -5.0
        response = client.post(
            "/shipment",
            json=sample_shipment_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 422
    
    def test_create_shipment_invalid_email(self, client, admin_token, sample_shipment_data, reset_db):
        """Test shipment creation with invalid recipient email"""
        sample_shipment_data["recipient"]["email"] = "invalid-email"
        response = client.post(
            "/shipment",
            json=sample_shipment_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 422
    
    def test_create_shipment_missing_required_fields(self, client, admin_token, reset_db):
        """Test shipment creation with missing required fields"""
        response = client.post(
            "/shipment",
            json={"package_details": {"content": "test"}},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 422
    
    def test_get_shipment_by_id(self, client, admin_token, reset_db):
        """Test getting shipment by ID"""
        response = client.get(
            "/shipment/12701",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 12701
        assert "package_details" in data
        assert "recipient" in data
        assert "tracking_events" in data
    
    def test_get_shipment_not_found(self, client, admin_token, reset_db):
        """Test getting non-existent shipment"""
        response = client.get(
            "/shipment/99999",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_get_all_shipments(self, client, admin_token, reset_db):
        """Test getting all shipments"""
        response = client.get(
            "/shipments",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_get_shipments_filter_by_status(self, client, admin_token, reset_db):
        """Test filtering shipments by status"""
        response = client.get(
            "/shipments?status=placed",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        for shipment in data:
            assert shipment["current_status"] == "placed"
    
    def test_get_shipments_filter_by_destination(self, client, admin_token, reset_db):
        """Test filtering shipments by destination code"""
        response = client.get(
            "/shipments?destination_code=11002",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        for shipment in data:
            assert shipment["destination_code"] == 11002
    
    def test_get_shipments_with_limit(self, client, admin_token, reset_db):
        """Test limiting shipment results"""
        response = client.get(
            "/shipments?limit=1",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 1
    
    def test_update_shipment_status(self, client, admin_token, reset_db):
        """Test updating shipment status"""
        response = client.patch(
            "/shipment/12701",
            json={"current_status": "in_transit"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["current_status"] == "in_transit"
    
    def test_update_shipment_invalid_transition(self, client, admin_token, reset_db):
        """Test invalid status transition"""
        response = client.patch(
            "/shipment/12701",
            json={"current_status": "delivered"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 400
        assert "transition" in response.json()["detail"].lower()
    
    def test_update_shipment_package_details(self, client, admin_token, reset_db):
        """Test updating package details"""
        response = client.patch(
            "/shipment/12701",
            json={
                "package_details": {
                    "content": "Updated content",
                    "weight": 10.0,
                    "fragile": True
                }
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["package_details"]["content"] == "Updated content"
        assert data["package_details"]["weight"] == 10.0
    
    def test_update_shipment_as_courier(self, client, courier_token, reset_db):
        """Test courier can update shipment status"""
        response = client.patch(
            "/shipment/12701",
            json={"current_status": "in_transit"},
            headers={"Authorization": f"Bearer {courier_token}"}
        )
        assert response.status_code == 200
    
    def test_update_shipment_as_customer_forbidden(self, client, customer_token, reset_db):
        """Test customer cannot update shipment"""
        response = client.patch(
            "/shipment/12701",
            json={"current_status": "in_transit"},
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        assert response.status_code == 403
    
    def test_delete_shipment_as_admin(self, client, admin_token, reset_db):
        """Test deleting shipment as admin"""
        response = client.delete(
            "/shipment/12701",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        assert "deleted" in response.json()["message"].lower()
        
        # Verify shipment is deleted
        get_response = client.get(
            "/shipment/12701",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert get_response.status_code == 404
    
    def test_delete_shipment_as_courier_forbidden(self, client, courier_token, reset_db):
        """Test courier cannot delete shipment"""
        response = client.delete(
            "/shipment/12701",
            headers={"Authorization": f"Bearer {courier_token}"}
        )
        assert response.status_code == 403
    
    def test_delete_shipment_not_found(self, client, admin_token, reset_db):
        """Test deleting non-existent shipment"""
        response = client.delete(
            "/shipment/99999",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 404


class TestShipmentWorkflow:
    """Test complete shipment workflow"""
    
    def test_complete_workflow(self, client, admin_token, courier_token, sample_shipment_data, reset_db):
        """Test complete shipment lifecycle from creation to delivery"""
        # 1. Create shipment
        create_response = client.post(
            "/shipment",
            json=sample_shipment_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert create_response.status_code == 201
        shipment_id = create_response.json()["id"]
        
        # 2. Update to in_transit
        update1 = client.patch(
            f"/shipment/{shipment_id}",
            json={"current_status": "in_transit"},
            headers={"Authorization": f"Bearer {courier_token}"}
        )
        assert update1.status_code == 200
        assert update1.json()["current_status"] == "in_transit"
        
        # 3. Update to out_for_delivery
        update2 = client.patch(
            f"/shipment/{shipment_id}",
            json={"current_status": "out_for_delivery"},
            headers={"Authorization": f"Bearer {courier_token}"}
        )
        assert update2.status_code == 200
        
        # 4. Update to delivered
        update3 = client.patch(
            f"/shipment/{shipment_id}",
            json={"current_status": "delivered"},
            headers={"Authorization": f"Bearer {courier_token}"}
        )
        assert update3.status_code == 200
        assert update3.json()["current_status"] == "delivered"
