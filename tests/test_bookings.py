"""
Tests for the bookings endpoints.

Verifies:
  - Paginated listing works correctly
  - Filters narrow results as expected
  - Individual booking retrieval returns correct data
  - 404 is returned for non-existent bookings
"""


def test_list_bookings(client):
    """GET /bookings should return a paginated list."""
    response = client.get("/bookings")
    assert response.status_code == 200
    data = response.json()
    assert "bookings" in data
    assert "total" in data
    assert "page" in data
    assert data["total"] == 3  # We inserted 3 sample bookings


def test_list_bookings_filter_by_hotel(client):
    """GET /bookings?hotel=Resort Hotel should filter correctly."""
    response = client.get("/bookings?hotel=Resort Hotel")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    for booking in data["bookings"]:
        assert booking["hotel"] == "Resort Hotel"


def test_list_bookings_filter_by_country(client):
    """GET /bookings?country=GBR should return only British bookings."""
    response = client.get("/bookings?country=GBR")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["bookings"][0]["country"] == "GBR"


def test_list_bookings_filter_canceled(client):
    """GET /bookings?is_canceled=1 should return only canceled bookings."""
    response = client.get("/bookings?is_canceled=1")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["bookings"][0]["is_canceled"] == 1


def test_list_bookings_pagination(client):
    """Pagination should limit results correctly."""
    response = client.get("/bookings?per_page=1&page=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data["bookings"]) == 1
    assert data["total"] == 3  # Total unchanged, just one per page


def test_get_booking_by_id(client):
    """GET /bookings/1 should return the correct booking."""
    response = client.get("/bookings/1")
    assert response.status_code == 200
    data = response.json()
    assert data["booking_id"] == 1
    assert data["hotel"] == "Resort Hotel"


def test_get_booking_not_found(client):
    """GET /bookings/99999 should return 404."""
    response = client.get("/bookings/99999")
    assert response.status_code == 404
