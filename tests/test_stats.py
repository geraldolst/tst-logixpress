"""
Statistics and Health Tests

Tests for statistics endpoints and health checks.
"""



class TestStatistics:
    """Test statistics endpoint"""

    def test_get_stats_as_admin(self, client, admin_token, reset_db):
        """Test getting statistics as admin"""
        response = client.get("/stats", headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 200
        data = response.json()
        assert "total_shipments" in data
        assert "by_status" in data
        assert isinstance(data["total_shipments"], int)
        assert isinstance(data["by_status"], dict)

    def test_get_stats_as_non_admin_forbidden(self, client, courier_token, reset_db):
        """Test non-admin cannot access statistics"""
        response = client.get("/stats", headers={"Authorization": f"Bearer {courier_token}"})
        assert response.status_code == 403

    def test_stats_accuracy(self, client, admin_token, reset_db):
        """Test statistics are accurate"""
        response = client.get("/stats", headers={"Authorization": f"Bearer {admin_token}"})
        data = response.json()

        # Check total matches sum of status counts
        status_sum = sum(data["by_status"].values())
        assert data["total_shipments"] == status_sum


class TestHealthCheck:
    """Test health check endpoint"""

    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"

    def test_health_check_no_auth_required(self, client):
        """Test health check doesn't require authentication"""
        response = client.get("/health")
        assert response.status_code == 200

    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "LOGIXPress" in data["message"]
