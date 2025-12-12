"""
Edge Cases Tests

Tests for edge cases, boundary conditions, and unusual inputs.
"""



class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_shipment_weight_boundary_max(self, client, admin_token, sample_shipment_data, reset_db):
        """Test shipment at maximum weight (25kg)"""
        sample_shipment_data["package_details"]["weight"] = 25.0
        response = client.post(
            "/shipment", json=sample_shipment_data, headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 201

    def test_shipment_weight_boundary_over_max(self, client, admin_token, sample_shipment_data, reset_db):
        """Test shipment over maximum weight (>25kg)"""
        sample_shipment_data["package_details"]["weight"] = 25.1
        response = client.post(
            "/shipment", json=sample_shipment_data, headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 422

    def test_shipment_weight_boundary_min(self, client, admin_token, sample_shipment_data, reset_db):
        """Test shipment at minimum weight (>0)"""
        sample_shipment_data["package_details"]["weight"] = 0.1
        response = client.post(
            "/shipment", json=sample_shipment_data, headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 201

    def test_shipment_weight_zero(self, client, admin_token, sample_shipment_data, reset_db):
        """Test shipment with zero weight"""
        sample_shipment_data["package_details"]["weight"] = 0.0
        response = client.post(
            "/shipment", json=sample_shipment_data, headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 422

    def test_empty_shipment_list_filter(self, client, admin_token, reset_db):
        """Test filtering shipments with no results"""
        response = client.get("/shipments?status=delivered", headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_very_long_description(self, client, admin_token, sample_shipment_data, reset_db):
        """Test shipment with very long description"""
        sample_shipment_data["package_details"]["content"] = "A" * 10000
        response = client.post(
            "/shipment", json=sample_shipment_data, headers={"Authorization": f"Bearer {admin_token}"}
        )
        # Should either accept or reject with validation error
        assert response.status_code in [201, 422]

    def test_special_characters_in_name(self, client, admin_token, sample_shipment_data, reset_db):
        """Test shipment with special characters in name"""
        sample_shipment_data["recipient"]["name"] = "José María Ñoño"
        response = client.post(
            "/shipment", json=sample_shipment_data, headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 201

    def test_unicode_emoji_in_description(self, client, admin_token, sample_shipment_data, reset_db):
        """Test shipment with emoji in description"""
        sample_shipment_data["package_details"]["content"] = "Package 📦 with emoji 🚚"
        response = client.post(
            "/shipment", json=sample_shipment_data, headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 201

    def test_phone_number_formats(self, client, admin_token, sample_shipment_data, reset_db):
        """Test various phone number formats"""
        formats = ["+6281234567890", "081234567890", "+62-812-3456-7890", "(021) 555-1234"]

        for phone in formats:
            sample_shipment_data["recipient"]["phone"] = phone
            response = client.post(
                "/shipment", json=sample_shipment_data, headers={"Authorization": f"Bearer {admin_token}"}
            )
            assert response.status_code == 201

    def test_concurrent_shipment_creation(self, client, admin_token, sample_shipment_data, reset_db):
        """Test creating multiple shipments in quick succession"""
        responses = []
        for _ in range(5):
            response = client.post(
                "/shipment", json=sample_shipment_data, headers={"Authorization": f"Bearer {admin_token}"}
            )
            responses.append(response)

        # All should succeed
        for response in responses:
            assert response.status_code == 201

        # All should have unique IDs
        ids = [r.json()["id"] for r in responses]
        assert len(set(ids)) == len(ids)

    def test_update_non_existent_field(self, client, admin_token, reset_db):
        """Test updating with non-existent field (should be ignored)"""
        response = client.patch(
            "/shipment/12701", json={"non_existent_field": "value"}, headers={"Authorization": f"Bearer {admin_token}"}
        )
        # Should succeed and ignore unknown field
        assert response.status_code == 200

    def test_get_shipments_limit_boundary(self, client, admin_token, reset_db):
        """Test shipments limit at boundaries"""
        # Min limit
        response1 = client.get("/shipments?limit=1", headers={"Authorization": f"Bearer {admin_token}"})
        assert response1.status_code == 200
        assert len(response1.json()) <= 1

        # Max limit
        response2 = client.get("/shipments?limit=100", headers={"Authorization": f"Bearer {admin_token}"})
        assert response2.status_code == 200

        # Over max limit
        response3 = client.get("/shipments?limit=101", headers={"Authorization": f"Bearer {admin_token}"})
        assert response3.status_code == 422

    def test_password_edge_cases(self, client, reset_db):
        """Test password edge cases during registration"""
        # Exactly 6 characters (minimum)
        response1 = client.post(
            "/auth/register", json={"username": "user1", "email": "user1@example.com", "password": "123456"}
        )
        assert response1.status_code == 201

        # 5 characters (below minimum)
        response2 = client.post(
            "/auth/register", json={"username": "user2", "email": "user2@example.com", "password": "12345"}
        )
        assert response2.status_code == 422

        # Very long password
        response3 = client.post(
            "/auth/register", json={"username": "user3", "email": "user3@example.com", "password": "A" * 1000}
        )
        assert response3.status_code == 201
