"""
Tests for the incidents CRUD endpoints.

Verifies the full lifecycle: create → read → update → patch → delete.
Also tests validation rules and error handling.
"""


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
        })
        assert response.status_code == 201
        data = response.json()
        assert data["booking_id"] == 1
        assert data["incident_type"] == "room_mismatch"
        assert data["severity"] == 3
        assert data["status"] == "open"
        assert "incident_id" in data
        assert "created_at" in data

    def test_create_incident_invalid_booking(self, client):
        """POST /incidents with non-existent booking should return 404."""
        response = client.post("/incidents", json={
            "booking_id": 99999,
            "incident_type": "complaint",
            "severity": 2,
            "description": "Test incident for non-existent booking",
            "reported_by": "Test"
        })
        assert response.status_code == 404

    def test_create_incident_invalid_severity(self, client):
        """POST /incidents with severity > 5 should return 422 validation error."""
        response = client.post("/incidents", json={
            "booking_id": 1,
            "incident_type": "complaint",
            "severity": 10,
            "description": "Invalid severity test",
            "reported_by": "Test"
        })
        assert response.status_code == 422

    def test_create_incident_invalid_type(self, client):
        """POST /incidents with invalid incident_type should return 422."""
        response = client.post("/incidents", json={
            "booking_id": 1,
            "incident_type": "invalid_type",
            "severity": 3,
            "description": "Invalid type test",
            "reported_by": "Test"
        })
        assert response.status_code == 422

    def test_list_incidents(self, client):
        """GET /incidents should return a list of incidents."""
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
        })
        assert response.status_code == 200
        data = response.json()
        assert data["severity"] == 4
        assert data["status"] == "investigating"

    def test_patch_incident_status(self, client):
        """PATCH /incidents/1 should partially update only specified fields."""
        response = client.patch("/incidents/1", json={
            "status": "resolved"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "resolved"
        # Other fields should be unchanged
        assert data["severity"] == 4

    def test_delete_incident(self, client):
        """DELETE /incidents should remove the incident."""
        # First create one to delete
        create_resp = client.post("/incidents", json={
            "booking_id": 2,
            "incident_type": "no_show",
            "severity": 1,
            "description": "Guest did not show up for reservation",
            "reported_by": "Night Shift"
        })
        incident_id = create_resp.json()["incident_id"]

        # Delete it
        response = client.delete(f"/incidents/{incident_id}")
        assert response.status_code == 200
        assert "deleted" in response.json()["message"].lower()

        # Verify it's gone
        get_resp = client.get(f"/incidents/{incident_id}")
        assert get_resp.status_code == 404
