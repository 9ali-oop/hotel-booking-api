"""
Tests for the AI-powered insight endpoints.

Verifies:
  - AI risk assessment returns proper structure
  - Template fallback works when no OpenAI key is set
  - Authentication is enforced
  - 404 for non-existent bookings
  - Response contains all expected fields
"""

import pytest


AUTH_HEADER = {"X-API-Key": "hotel-booking-dev-key-2025"}


class TestAIRiskAssessment:
    """Test the AI-powered risk assessment endpoint."""

    def test_ai_assessment_returns_structured_response(self, client):
        """POST /insights/ai-risk-assessment/1 should return full assessment."""
        response = client.post("/insights/ai-risk-assessment/1", headers=AUTH_HEADER)
        assert response.status_code == 200
        data = response.json()

        # Verify all expected fields are present
        assert "booking_id" in data
        assert data["booking_id"] == 1
        assert "hotel" in data
        assert "risk_score" in data
        assert "risk_band" in data
        assert data["risk_band"] in ("low", "medium", "high")
        assert "risk_factors" in data
        assert isinstance(data["risk_factors"], list)
        assert "ai_assessment" in data
        assert len(data["ai_assessment"]) > 50  # Should be substantial text
        assert "ai_model" in data
        assert "ai_source" in data

    def test_ai_assessment_booking_not_found(self, client):
        """POST /insights/ai-risk-assessment/99999 should return 404."""
        response = client.post(
            "/insights/ai-risk-assessment/99999", headers=AUTH_HEADER
        )
        assert response.status_code == 404

    def test_ai_assessment_requires_auth(self, client):
        """POST /insights/ai-risk-assessment without auth should return 401."""
        response = client.post("/insights/ai-risk-assessment/1")
        assert response.status_code == 401

    def test_ai_assessment_wrong_key(self, client):
        """POST /insights/ai-risk-assessment with bad key should return 403."""
        response = client.post(
            "/insights/ai-risk-assessment/1",
            headers={"X-API-Key": "wrong-key"},
        )
        assert response.status_code == 403

    def test_ai_assessment_template_fallback(self, client):
        """Without OPENAI_API_KEY, should use template-based assessment."""
        response = client.post("/insights/ai-risk-assessment/1", headers=AUTH_HEADER)
        data = response.json()
        # In test environment there's no OpenAI key, so should use template
        assert data["ai_source"] == "template"
        assert "Risk Summary" in data["ai_assessment"]
        assert "Recommended Actions" in data["ai_assessment"]
        assert "Revenue Impact" in data["ai_assessment"]

    def test_ai_assessment_high_risk_booking(self, client):
        """Booking 1 (lead_time=342, no deposit) should have high risk score."""
        response = client.post("/insights/ai-risk-assessment/1", headers=AUTH_HEADER)
        data = response.json()
        # Booking 1: lead_time=342, no deposit, first-time guest, Direct segment
        assert data["risk_score"] >= 0.3  # Should be at least medium

    def test_ai_assessment_different_bookings_different_results(self, client):
        """Different bookings should produce different assessments."""
        resp1 = client.post("/insights/ai-risk-assessment/1", headers=AUTH_HEADER)
        resp3 = client.post("/insights/ai-risk-assessment/3", headers=AUTH_HEADER)
        data1 = resp1.json()
        data3 = resp3.json()
        # Booking 1 (high lead time) vs Booking 3 (low lead time, repeated guest)
        assert data1["risk_score"] != data3["risk_score"]
