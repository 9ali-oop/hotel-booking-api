"""
Tests for the incidents CRUD endpoints.

Verifies the full lifecycle: create → read → update → patch → delete.
Also tests validation rules, error handling, and authentication enforcement.
"""


# Default dev API key for test requests
AUTH_HEADER = {"X-API-Key": "hotel-booking-dev-key-2025"}


class TestIncidentsCRUD:
    """Test the complete CRUD lifecycle for incidents."""

    def test_create_incident(self, client):
        """POST /incidents should create a new incident and return 201."""
        response = client.post("/incidents", json={
            "booking_id": 1,
            "incident_type": "room_mismatch",
            "severity": 3,
            "description": "Guest was assigned wrong room type",
            "reported_by": "Front Desk Staff"
        }, headers=AUTH_HEADER)
        assert response.status_code == 201
        data = response.json()
        assert data["booking_id"] == 1
        assert data["incident_type"] == "room_mismatch"
        assert data["severity"] == 3
        assert data["status"] == "open"
        assert "incident_id" in data
        assert "created_at" in data

    def test_create_incident_no_auth(self, client):
        """POST /incidents without API key should return 401."""
        response = client.post("/incidents", json={
            "booking_id": 1,
            "incident_type": "complaint",
            "severity": 2,
            "description": "Testing auth enforcement",
            "reported_by": "Test"
        })
        assert response.status_code == 401

    def test_create_incident_bad_key(self, client):
        """POST /incidents with wrong API key should return 403."""
        response = client.post("/incidents", json={
            "booking_id": 1,
            "incident_type": "complaint",
            "severity": 2,
            "description": "Testing auth enforcement",
            "reported_by": "Test"
        }, headers={"X-API-Key": "wrong-key"})
        assert response.status_code == 403

    def test_create_incident_invalid_booking(self, client):
        """POST /incidents with non-existent booking should return 404."""
        response = client.post("/incidents", json={
            "booking_id": 99999,
            "incident_type": "complaint",
            "severity": 2,
            "description": "Test incident for non-existent booking",
            "reported_by": "Test"
        }, headers=AUTH_HEADER)
        assert response.status_code == 404

    def test_create_incident_invalid_severity(self, client):
        """POST /incidents with severity > 5 should return 422 validation error."""
        response = client.post("/incidents", json={
            "booking_id": 1,
            "incident_type": "complaint",
            "severity": 10,
            "description": "Invalid severity test",
            "reported_by": "Test"
        }, headers=AUTH_HEADER)
        assert response.status_code == 422

    def test_create_incident_invalid_type(self, client):
        """POST /incidents with invalid incident_type should return 422."""
        response = client.post("/incidents", json={
            "booking_id": 1,
            "incident_type": "invalid_type",
            "severity": 3,
            "description": "Invalid type test",
            "reported_by": "Test"
        }, headers=AUTH_HEADER)
        assert response.status_code == 422

    def test_create_incident_short_description(self, client):
        """POST /incidents with description < 5 chars should return 422."""
        response = client.post("/incidents", json={
            "booking_id": 1,
            "incident_type": "complaint",
            "severity": 3,
            "description": "Hi",
            "reported_by": "Test"
        }, headers=AUTH_HEADER)
        assert response.status_code == 422

    def test_list_incidents_no_auth_required(self, client):
        """GET /incidents should work without authentication (read-only)."""
        response = client.get("/incidents")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_list_incidents_filter_by_severity(self, client):
        """GET /incidents?severity=3 should filter correctly."""
        response = client.get("/incidents?severity=3")
        assert response.status_code == 200
        data = response.json()
        for incident in data:
            assert incident["severity"] == 3

    def test_get_incident_by_id(self, client):
        """GET /incidents/1 should return the correct incident."""
        response = client.get("/incidents/1")
        assert response.status_code == 200
        data = response.json()
        assert data["incident_id"] == 1

    def test_get_incident_not_found(self, client):
        """GET /incidents/99999 should return 404."""
        response = client.get("/incidents/99999")
        assert response.status_code == 404

    def test_put_update_incident(self, client):
        """PUT /incidents/1 should fully update the incident."""
        response = client.put("/incidents/1", json={
            "incident_type": "complaint",
            "severity": 4,
            "description": "Updated: guest escalated complaint to management",
            "reported_by": "Duty Manager",
            "status": "investigating"
        }, headers=AUTH_HEADER)
        assert response.status_code == 200
        data = response.json()
        assert data["severity"] == 4
        assert data["status"] == "investigating"

    def test_put_update_no_auth(self, client):
        """PUT /incidents/1 without auth should return 401."""
        response = client.put("/incidents/1", json={
            "incident_type": "complaint",
            "severity": 2,
            "description": "Should fail without auth",
            "reported_by": "Test",
            "status": "open"
        })
        assert response.status_code == 401

    def test_patch_incident_status(self, client):
        """PATCH /incidents/1 should partially update only specified fields."""
        response = client.patch("/incidents/1", json={
            "status": "resolved"
        }, headers=AUTH_HEADER)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "resolved"
        assert data["severity"] == 4

    def test_delete_incident(self, client):
        """DELETE /incidents should remove the incident."""
        create_resp = client.post("/incidents", json={
            "booking_id": 2,
            "incident_type": "no_show",
            "severity": 1,
            "description": "Guest did not show up for reservation",
            "reported_by": "Night Shift"
        }, headers=AUTH_HEADER)
        incident_id = create_resp.json()["incident_id"]

        response = client.delete(f"/incidents/{incident_id}", headers=AUTH_HEADER)
        assert response.status_code == 200
        assert "deleted" in response.json()["message"].lower()

        get_resp = client.get(f"/incidents/{incident_id}")
        assert get_resp.status_code == 404

    def test_delete_incident_no_auth(self, client):
        """DELETE /incidents without auth should return 401."""
        response = client.delete("/incidents/1")
        assert response.status_code == 401
