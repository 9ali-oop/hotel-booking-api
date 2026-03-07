"""
Tests for the authentication system.

Verifies:
  - API key authentication (valid, invalid, missing)
  - JWT token issuance via POST /auth/token
  - JWT token usage for protected endpoints
  - Token expiry behaviour
  - Dual auth support (API key OR Bearer token)
"""


AUTH_HEADER = {"X-API-Key": "hotel-booking-dev-key-2025"}


class TestAPIKeyAuth:
    """Test API key authentication."""

    def test_valid_api_key_allows_write(self, client):
        """Valid API key should allow POST requests."""
        response = client.post("/incidents", json={
            "booking_id": 1,
            "incident_type": "complaint",
            "severity": 2,
            "description": "Testing valid API key authentication",
            "reported_by": "Auth Test"
        }, headers=AUTH_HEADER)
        assert response.status_code == 201

    def test_missing_key_returns_401(self, client):
        """Missing API key should return 401 Unauthorized."""
        response = client.post("/incidents", json={
            "booking_id": 1,
            "incident_type": "complaint",
            "severity": 2,
            "description": "Testing missing auth",
            "reported_by": "Test"
        })
        assert response.status_code == 401
        assert "Authentication required" in response.json()["detail"]

    def test_wrong_key_returns_403(self, client):
        """Invalid API key should return 403 Forbidden."""
        response = client.post("/incidents", json={
            "booking_id": 1,
            "incident_type": "complaint",
            "severity": 2,
            "description": "Testing wrong key",
            "reported_by": "Test"
        }, headers={"X-API-Key": "wrong-key-12345"})
        assert response.status_code == 403
        assert "Invalid API key" in response.json()["detail"]

    def test_read_endpoints_no_auth_needed(self, client):
        """GET endpoints should work without any authentication."""
        endpoints = ["/bookings", "/incidents", "/notes", "/health", "/"]
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200, f"{endpoint} should be public"


class TestJWTTokenAuth:
    """Test JWT token issuance and usage."""

    def test_obtain_token_with_valid_key(self, client):
        """POST /auth/token with valid API key should return a JWT."""
        response = client.post("/auth/token", json={
            "api_key": "hotel-booking-dev-key-2025"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 1800  # 30 min
        assert "issued_at" in data
        assert "expires_at" in data

    def test_obtain_token_with_invalid_key(self, client):
        """POST /auth/token with invalid API key should return 403."""
        response = client.post("/auth/token", json={
            "api_key": "wrong-key"
        })
        assert response.status_code == 403

    def test_use_jwt_for_write_operations(self, client):
        """Bearer token should authenticate write operations."""
        # Step 1: Get a token
        token_resp = client.post("/auth/token", json={
            "api_key": "hotel-booking-dev-key-2025"
        })
        token = token_resp.json()["access_token"]

        # Step 2: Use the token to create an incident
        response = client.post("/incidents", json={
            "booking_id": 1,
            "incident_type": "maintenance",
            "severity": 2,
            "description": "Testing JWT Bearer token authentication",
            "reported_by": "JWT Auth Test"
        }, headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 201

    def test_invalid_jwt_returns_401(self, client):
        """Tampered JWT should return 401."""
        response = client.post("/incidents", json={
            "booking_id": 1,
            "incident_type": "complaint",
            "severity": 2,
            "description": "Testing invalid JWT",
            "reported_by": "Test"
        }, headers={"Authorization": "Bearer fake.token.here"})
        assert response.status_code == 401


class TestHealthEndpoint:
    """Test the health check endpoint."""

    def test_health_returns_status(self, client):
        """GET /health should return database status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "database" in data
        assert "version" in data
