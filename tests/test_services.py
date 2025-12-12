"""
Service Layer Tests

Tests for business logic in service layer.
"""

import pytest
from app.services.auth import AuthService
from app.services.shipment import ShipmentService
from app.api.schemas.auth import RegisterRequest
from app.api.schemas.shipment import ShipmentCreate, PackageDetails, Recipient, Seller
from app.core.exceptions import EntityNotFound, DuplicateEntity


class TestAuthService:
    """Test authentication service"""
    
    def test_get_user_exists(self, reset_db):
        """Test getting existing user"""
        user = AuthService.get_user("admin")
        assert user is not None
        assert user.username == "admin"
        assert user.role == "admin"
    
    def test_get_user_not_exists(self, reset_db):
        """Test getting non-existent user"""
        user = AuthService.get_user("nonexistent")
        assert user is None
    
    def test_authenticate_user_valid(self, reset_db):
        """Test authentication with valid credentials"""
        user = AuthService.authenticate_user("admin", "admin123")
        assert user is not None
        assert user.username == "admin"
    
    def test_authenticate_user_invalid_username(self, reset_db):
        """Test authentication with invalid username"""
        user = AuthService.authenticate_user("nonexistent", "password")
        assert user is None
    
    def test_authenticate_user_invalid_password(self, reset_db):
        """Test authentication with invalid password"""
        user = AuthService.authenticate_user("admin", "wrongpassword")
        assert user is None
    
    def test_register_user_success(self, reset_db):
        """Test successful user registration"""
        register_data = RegisterRequest(
            username="newuser",
            email="newuser@example.com",
            password="password123",
            role="customer"
        )
        user = AuthService.register_user(register_data)
        assert user.username == "newuser"
        assert user.role == "customer"
    
    def test_register_user_duplicate_username(self, reset_db):
        """Test registration with duplicate username"""
        register_data = RegisterRequest(
            username="admin",
            email="newemail@example.com",
            password="password123"
        )
        with pytest.raises(DuplicateEntity):
            AuthService.register_user(register_data)
    
    def test_create_access_token_for_user(self, reset_db):
        """Test creating access token for user"""
        user = AuthService.get_user("admin")
        token = AuthService.create_access_token_for_user(user)
        assert isinstance(token, str)
        assert len(token) > 50


class TestShipmentService:
    """Test shipment service"""
    
    def test_get_all_shipments(self, reset_db):
        """Test getting all shipments"""
        shipments = ShipmentService.get_all_shipments()
        assert isinstance(shipments, list)
        assert len(shipments) > 0
    
    def test_get_all_shipments_with_status_filter(self, reset_db):
        """Test filtering shipments by status"""
        from app.models.shipment import ShipmentStatus
        shipments = ShipmentService.get_all_shipments(status_filter=ShipmentStatus.placed)
        for shipment in shipments:
            assert shipment.current_status == "placed"
    
    def test_get_shipment_by_id_exists(self, reset_db):
        """Test getting existing shipment"""
        shipment = ShipmentService.get_shipment_by_id(12701)
        assert shipment.id == 12701
        assert shipment.package_details is not None
    
    def test_get_shipment_by_id_not_exists(self, reset_db):
        """Test getting non-existent shipment"""
        with pytest.raises(EntityNotFound):
            ShipmentService.get_shipment_by_id(99999)
    
    def test_create_shipment(self, reset_db):
        """Test creating new shipment"""
        shipment_data = ShipmentCreate(
            package_details=PackageDetails(
                content="Test Package",
                weight=5.5,
                fragile=True
            ),
            recipient=Recipient(
                name="John Doe",
                email="john@example.com",
                phone="+6281234567890",
                address="Test Address"
            ),
            seller=Seller(
                name="Test Store",
                email="store@example.com",
                phone="+6281234567891"
            ),
            destination_code=11002
        )
        result = ShipmentService.create_shipment(shipment_data)
        assert "id" in result
        assert "message" in result
    
    def test_delete_shipment_exists(self, reset_db):
        """Test deleting existing shipment"""
        result = ShipmentService.delete_shipment(12701)
        assert "deleted" in result["message"].lower()
        
        # Verify deleted
        with pytest.raises(EntityNotFound):
            ShipmentService.get_shipment_by_id(12701)
    
    def test_delete_shipment_not_exists(self, reset_db):
        """Test deleting non-existent shipment"""
        with pytest.raises(EntityNotFound):
            ShipmentService.delete_shipment(99999)
