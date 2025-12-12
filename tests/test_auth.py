"""
Authentication Tests

Tests for user authentication, registration, and authorization.
Covers: login, register, token validation, role-based access.
"""

from app.core.security import get_password_hash, verify_password


class TestAuthEndpoints:
    """Test authentication endpoints"""

    def test_login_success(self, client, reset_db):
        """Test successful login with valid credentials"""
        response = client.post("/auth/login", json={"username": "admin", "password": "admin123"})
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0

    def test_login_invalid_username(self, client, reset_db):
        """Test login with non-existent username"""
        response = client.post("/auth/login", json={"username": "nonexistent", "password": "admin123"})
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

    def test_login_invalid_password(self, client, reset_db):
        """Test login with wrong password"""
        response = client.post("/auth/login", json={"username": "admin", "password": "wrongpassword"})
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

    def test_login_missing_fields(self, client, reset_db):
        """Test login with missing required fields"""
        response = client.post("/auth/login", json={"username": "admin"})
        assert response.status_code == 422

    def test_register_success(self, client, reset_db):
        """Test successful user registration"""
        response = client.post(
            "/auth/register",
            json={"username": "newuser", "email": "newuser@example.com", "password": "password123", "role": "customer"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert data["role"] == "customer"
        assert "registered successfully" in data["message"]

    def test_register_duplicate_username(self, client, reset_db):
        """Test registration with existing username"""
        response = client.post(
            "/auth/register", json={"username": "admin", "email": "newemail@example.com", "password": "password123"}
        )
        assert response.status_code == 400
        assert "username" in response.json()["detail"].lower()

    def test_register_duplicate_email(self, client, reset_db):
        """Test registration with existing email"""
        response = client.post(
            "/auth/register", json={"username": "newuser", "email": "admin@logixpress.com", "password": "password123"}
        )
        assert response.status_code == 400
        assert "email" in response.json()["detail"].lower()

    def test_register_short_password(self, client, reset_db):
        """Test registration with password < 6 characters"""
        response = client.post(
            "/auth/register", json={"username": "newuser", "email": "newuser@example.com", "password": "12345"}
        )
        assert response.status_code == 422
        assert "6 characters" in response.json()["detail"].lower()

    def test_register_invalid_email(self, client, reset_db):
        """Test registration with invalid email format"""
        response = client.post(
            "/auth/register", json={"username": "newuser", "email": "invalid-email", "password": "password123"}
        )
        assert response.status_code == 422

    def test_register_invalid_role(self, client, reset_db):
        """Test registration with invalid role"""
        response = client.post(
            "/auth/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "password123",
                "role": "invalid_role",
            },
        )
        assert response.status_code == 422
        assert "role" in response.json()["detail"].lower()

    def test_register_default_role(self, client, reset_db):
        """Test registration without specifying role (should default to customer)"""
        response = client.post(
            "/auth/register", json={"username": "newuser", "email": "newuser@example.com", "password": "password123"}
        )
        assert response.status_code == 201
        assert response.json()["role"] == "customer"

    def test_get_current_user(self, client, admin_token, reset_db):
        """Test getting current user info with valid token"""
        response = client.get("/auth/me", headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "admin"
        assert data["role"] == "admin"
        assert "email" in data

    def test_get_current_user_no_token(self, client, reset_db):
        """Test accessing protected endpoint without token"""
        response = client.get("/auth/me")
        assert response.status_code == 403

    def test_get_current_user_invalid_token(self, client, reset_db):
        """Test accessing protected endpoint with invalid token"""
        response = client.get("/auth/me", headers={"Authorization": "Bearer invalid_token_12345"})
        assert response.status_code == 401


class TestPasswordSecurity:
    """Test password hashing and verification"""

    def test_password_hash(self):
        """Test password hashing"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        assert hashed != password
        assert len(hashed) > 20
        assert hashed.startswith("$2b$")

    def test_password_verify_correct(self):
        """Test password verification with correct password"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True

    def test_password_verify_incorrect(self):
        """Test password verification with incorrect password"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        assert verify_password("wrongpassword", hashed) is False

    def test_different_passwords_different_hashes(self):
        """Test that same password generates different hashes (salt)"""
        password = "testpassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        assert hash1 != hash2
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True
