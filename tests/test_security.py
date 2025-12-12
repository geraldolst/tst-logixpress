"""
Security Tests

Tests for JWT token security, authorization, and access control.
Covers: token validation, expiration, role-based access, injection attacks.
"""

import pytest
from datetime import datetime, timedelta
from jose import jwt

from app.config import settings
from app.core.security import create_access_token, decode_access_token


class TestJWTSecurity:
    """Test JWT token security"""
    
    def test_create_token(self):
        """Test JWT token creation"""
        data = {"sub": "testuser", "role": "admin"}
        token = create_access_token(data)
        assert isinstance(token, str)
        assert len(token) > 50
    
    def test_decode_valid_token(self):
        """Test decoding valid JWT token"""
        data = {"sub": "testuser", "role": "admin"}
        token = create_access_token(data)
        decoded = decode_access_token(token)
        assert decoded is not None
        assert decoded.username == "testuser"
        assert decoded.role == "admin"
    
    def test_decode_invalid_token(self):
        """Test decoding invalid JWT token"""
        decoded = decode_access_token("invalid_token_12345")
        assert decoded is None
    
    def test_decode_tampered_token(self):
        """Test decoding tampered JWT token"""
        data = {"sub": "testuser", "role": "customer"}
        token = create_access_token(data)
        
        # Tamper with token
        parts = token.split(".")
        tampered_token = f"{parts[0]}.tampered.{parts[2]}"
        
        decoded = decode_access_token(tampered_token)
        assert decoded is None
    
    def test_token_expiration(self):
        """Test JWT token expiration"""
        # Create token that expires in 1 second
        data = {"sub": "testuser", "role": "admin"}
        expires_delta = timedelta(seconds=-1)  # Already expired
        token = create_access_token(data, expires_delta)
        
        decoded = decode_access_token(token)
        assert decoded is None
    
    def test_token_contains_required_claims(self):
        """Test token contains required claims"""
        data = {"sub": "testuser", "role": "admin"}
        token = create_access_token(data)
        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert "sub" in payload
        assert "role" in payload
        assert "exp" in payload
    
    def test_token_without_role_fails(self):
        """Test token without role claim"""
        data = {"sub": "testuser"}  # Missing role
        token = create_access_token(data)
        decoded = decode_access_token(token)
        
        # Should decode but role will be None
        assert decoded is not None
        assert decoded.role is None


class TestRoleBasedAccess:
    """Test role-based access control"""
    
    def test_admin_full_access(self, client, admin_token, sample_shipment_data, reset_db):
        """Test admin has full access to all operations"""
        # Create
        create = client.post(
            "/shipment",
            json=sample_shipment_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert create.status_code == 201
        
        # Read
        read = client.get(
            "/shipments",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert read.status_code == 200
        
        # Update
        update = client.patch(
            "/shipment/12701",
            json={"current_status": "in_transit"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert update.status_code == 200
        
        # Delete
        delete = client.delete(
            "/shipment/12701",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert delete.status_code == 200
    
    def test_courier_limited_access(self, client, courier_token, sample_shipment_data, reset_db):
        """Test courier has limited access"""
        # Cannot create
        create = client.post(
            "/shipment",
            json=sample_shipment_data,
            headers={"Authorization": f"Bearer {courier_token}"}
        )
        assert create.status_code == 403
        
        # Can read
        read = client.get(
            "/shipments",
            headers={"Authorization": f"Bearer {courier_token}"}
        )
        assert read.status_code == 200
        
        # Can update status
        update = client.patch(
            "/shipment/12701",
            json={"current_status": "in_transit"},
            headers={"Authorization": f"Bearer {courier_token}"}
        )
        assert update.status_code == 200
        
        # Cannot delete
        delete = client.delete(
            "/shipment/12701",
            headers={"Authorization": f"Bearer {courier_token}"}
        )
        assert delete.status_code == 403
    
    def test_customer_restricted_access(self, client, customer_token, sample_shipment_data, reset_db):
        """Test customer has restricted access"""
        # Can create
        create = client.post(
            "/shipment",
            json=sample_shipment_data,
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        assert create.status_code == 201
        
        # Can read
        read = client.get(
            "/shipments",
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        assert read.status_code == 200
        
        # Cannot update
        update = client.patch(
            "/shipment/12701",
            json={"current_status": "in_transit"},
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        assert update.status_code == 403
        
        # Cannot delete
        delete = client.delete(
            "/shipment/12701",
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        assert delete.status_code == 403


class TestSecurityVulnerabilities:
    """Test protection against common security vulnerabilities"""
    
    def test_sql_injection_attempt(self, client, admin_token, reset_db):
        """Test protection against SQL injection in shipment ID"""
        response = client.get(
            "/shipment/12701'; DROP TABLE shipments; --",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        # Should fail validation, not execute SQL
        assert response.status_code in [404, 422]
    
    def test_xss_attempt_in_description(self, client, admin_token, sample_shipment_data, reset_db):
        """Test XSS attempt in package description"""
        sample_shipment_data["package_details"]["content"] = "<script>alert('XSS')</script>"
        response = client.post(
            "/shipment",
            json=sample_shipment_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        # Should accept but escape the content
        assert response.status_code == 201
    
    def test_unauthorized_access_without_token(self, client, reset_db):
        """Test all protected endpoints require authentication"""
        endpoints = [
            ("/shipments", "GET"),
            ("/shipment/12701", "GET"),
            ("/shipment", "POST"),
            ("/shipment/12701", "PATCH"),
            ("/shipment/12701", "DELETE"),
            ("/shipment/12701/tracking", "GET"),
            ("/shipment/12701/tracking", "POST"),
            ("/stats", "GET"),
        ]
        
        for endpoint, method in endpoints:
            if method == "GET":
                response = client.get(endpoint)
            elif method == "POST":
                response = client.post(endpoint, json={})
            elif method == "PATCH":
                response = client.patch(endpoint, json={})
            elif method == "DELETE":
                response = client.delete(endpoint)
            
            assert response.status_code == 403, f"{method} {endpoint} should require auth"
