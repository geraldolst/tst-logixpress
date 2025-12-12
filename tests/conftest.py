"""
Pytest Configuration and Fixtures

Shared fixtures for all tests to ensure consistent test environment.
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime

from app.main import app
from app.services.auth import fake_users_db
from app.services.shipment import shipments_db, tracking_event_counter


@pytest.fixture(scope="function")
def client():
    """FastAPI test client fixture"""
    return TestClient(app)


@pytest.fixture(scope="function")
def reset_db():
    """Reset in-memory databases before each test"""
    # Clear and reinitialize users  
    fake_users_db.clear()
    fake_users_db.update({
        "admin": {
            "username": "admin",
            "email": "admin@logixpress.com",
            "plain_password": "admin123",
            "role": "admin",
            "disabled": False,
        },
        "courier": {
            "username": "courier",
            "email": "courier@logixpress.com",
            "plain_password": "courier123",
            "role": "courier",
            "disabled": False,
        },
        "customer": {
            "username": "customer",
            "email": "customer@example.com",
            "plain_password": "customer123",
            "role": "customer",
            "disabled": False,
        }
    })
    
    # Clear and reinitialize shipments
    shipments_db.clear()
    shipments_db.update({
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
        }
    })
    
    yield
    
    # Cleanup after test
    fake_users_db.clear()
    shipments_db.clear()


@pytest.fixture
def admin_token(client, reset_db):
    """Get admin JWT token"""
    response = client.post(
        "/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    return response.json()["access_token"]


@pytest.fixture
def courier_token(client, reset_db):
    """Get courier JWT token"""
    response = client.post(
        "/auth/login",
        json={"username": "courier", "password": "courier123"}
    )
    return response.json()["access_token"]


@pytest.fixture
def customer_token(client, reset_db):
    """Get customer JWT token"""
    response = client.post(
        "/auth/login",
        json={"username": "customer", "password": "customer123"}
    )
    return response.json()["access_token"]


@pytest.fixture
def sample_shipment_data():
    """Sample shipment creation data"""
    return {
        "package_details": {
            "content": "Test Package",
            "weight": 5.5,
            "dimensions": "30x20x15",
            "fragile": True
        },
        "recipient": {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "+6281234567890",
            "address": "Jl. Test No. 123, Jakarta"
        },
        "seller": {
            "name": "Test Store",
            "email": "sales@teststore.com",
            "phone": "+6281234567891"
        },
        "destination_code": 11002
    }


@pytest.fixture
def auth_headers(admin_token):
    """Authorization headers with admin token"""
    return {"Authorization": f"Bearer {admin_token}"}
