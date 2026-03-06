"""
Tests for the analytics and insights endpoints.

Verifies that aggregation queries return correct structure and values.
"""


class TestAnalytics:
    """Test analytics endpoints."""

    def test_cancellation_rate_overall(self, client):
        """GET /analytics/cancellation-rate should return stats."""
        response = client.get("/analytics/cancellation-rate")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        # First entry is overall stats
        overall = data[0]
        assert "total_bookings" in overall
        assert "cancellations" in overall
        assert "cancellation_rate" in overall

    def test_cancellation_rate_by_hotel(self, client):
        """GET /analytics/cancellation-rate?hotel=City Hotel should filter."""
        response = client.get("/analytics/cancellation-rate?hotel=City Hotel")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["hotel"] == "City Hotel"

    def test_monthly_demand(self, client):
        """GET /analytics/monthly-demand should return monthly counts."""
        response = client.get("/analytics/monthly-demand")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        for item in data:
            assert "month" in item
            assert "year" in item
            assert "booking_count" in item

    def test_market_segment_performance(self, client):
        """GET /analytics/market-segment-performance should return segments."""
        response = client.get("/analytics/market-segment-performance")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        for item in data:
            assert "market_segment" in item
            assert "total_bookings" in item
            assert "cancellation_rate" in item
            assert "average_adr" in item


class TestInsights:
    """Test insight endpoints."""

    def test_high_risk_bookings(self, client):
        """GET /insights/high-risk-bookings should return scored bookings."""
        response = client.get("/insights/high-risk-bookings?min_risk=0.0")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Booking 1 has lead_time=342, no deposit, first-time — should have high score
        if data:
            assert "risk_score" in data[0]
            assert "risk_band" in data[0]
            assert "risk_factors" in data[0]
            assert data[0]["risk_score"] >= 0
            assert data[0]["risk_score"] <= 1
            assert data[0]["risk_band"] in ("low", "medium", "high")

    def test_high_risk_bookings_with_threshold(self, client):
        """Higher threshold should return fewer results."""
        low = client.get("/insights/high-risk-bookings?min_risk=0.1").json()
        high = client.get("/insights/high-risk-bookings?min_risk=0.8").json()
        assert len(high) <= len(low)

    def test_operational_hotspots(self, client):
        """GET /insights/operational-hotspots should return hotspot data."""
        response = client.get("/insights/operational-hotspots")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # May be empty if no incidents linked to bookings yet


class TestRootEndpoint:
    """Test the root endpoint."""

    def test_root(self, client):
        """GET / should return API info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Hotel Booking Intelligence API" in data["message"]
        assert "endpoints" in data
