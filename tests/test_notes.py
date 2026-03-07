"""
Tests for the manager notes CRUD endpoints.

Verifies create, list, get-by-id, and delete operations,
plus validation, error handling, and authentication enforcement.
"""


AUTH_HEADER = {"X-API-Key": "hotel-booking-dev-key-2025"}


class TestNotesCRUD:
    """Test the CRUD operations for manager notes."""

    def test_create_note(self, client):
        """POST /notes should create a new note and return 201."""
        response = client.post("/notes", json={
            "booking_id": 1,
            "note_text": "VIP guest — ensure room is ready early",
            "author": "General Manager"
        }, headers=AUTH_HEADER)
        assert response.status_code == 201
        data = response.json()
        assert data["booking_id"] == 1
        assert data["author"] == "General Manager"
        assert "note_id" in data

    def test_create_note_no_auth(self, client):
        """POST /notes without API key should return 401."""
        response = client.post("/notes", json={
            "booking_id": 1,
            "note_text": "Should fail without auth",
            "author": "Test"
        })
        assert response.status_code == 401

    def test_create_note_bad_key(self, client):
        """POST /notes with wrong API key should return 403."""
        response = client.post("/notes", json={
            "booking_id": 1,
            "note_text": "Should fail with bad key",
            "author": "Test"
        }, headers={"X-API-Key": "wrong-key"})
        assert response.status_code == 403

    def test_create_note_invalid_booking(self, client):
        """POST /notes with non-existent booking should return 404."""
        response = client.post("/notes", json={
            "booking_id": 99999,
            "note_text": "This should fail",
            "author": "Test"
        }, headers=AUTH_HEADER)
        assert response.status_code == 404

    def test_create_note_empty_text(self, client):
        """POST /notes with empty note text should return 422."""
        response = client.post("/notes", json={
            "booking_id": 1,
            "note_text": "",
            "author": "Test"
        }, headers=AUTH_HEADER)
        assert response.status_code == 422

    def test_list_notes_no_auth_required(self, client):
        """GET /notes should work without authentication (read-only)."""
        response = client.get("/notes")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_list_notes_filter_by_booking(self, client):
        """GET /notes?booking_id=1 should return only notes for that booking."""
        response = client.get("/notes?booking_id=1")
        assert response.status_code == 200
        data = response.json()
        for note in data:
            assert note["booking_id"] == 1

    def test_get_note_by_id(self, client):
        """GET /notes/1 should return the correct note."""
        response = client.get("/notes/1")
        assert response.status_code == 200
        data = response.json()
        assert data["note_id"] == 1

    def test_get_note_not_found(self, client):
        """GET /notes/99999 should return 404."""
        response = client.get("/notes/99999")
        assert response.status_code == 404

    def test_delete_note(self, client):
        """DELETE /notes should remove the note."""
        create_resp = client.post("/notes", json={
            "booking_id": 2,
            "note_text": "Temporary note for deletion test",
            "author": "Test Manager"
        }, headers=AUTH_HEADER)
        note_id = create_resp.json()["note_id"]

        response = client.delete(f"/notes/{note_id}", headers=AUTH_HEADER)
        assert response.status_code == 200

        get_resp = client.get(f"/notes/{note_id}")
        assert get_resp.status_code == 404

    def test_delete_note_no_auth(self, client):
        """DELETE /notes without auth should return 401."""
        response = client.delete("/notes/1")
        assert response.status_code == 401
