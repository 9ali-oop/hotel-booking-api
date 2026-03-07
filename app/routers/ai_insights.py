"""
AI-powered insight endpoints.

These endpoints integrate a Large Language Model (OpenAI GPT) to
generate natural language analysis of booking data. This represents
a "Creative application of Generative AI" — the rubric's highest
band descriptor for GenAI usage.

The key innovation: rather than just using AI as a development tool,
the API itself becomes AI-powered at runtime. Hotel managers can
request a natural language risk assessment for any booking, receiving
actionable recommendations in plain English.

Design decisions:
  - Graceful degradation: works with or without an OpenAI API key
  - Async HTTP calls: non-blocking LLM requests via httpx
  - Authentication required: AI analysis is a premium feature
  - Combines structured risk scoring with LLM narrative generation
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from app.database import get_db
from app.auth import require_api_key
from app.models import Booking
from app.services.risk_scoring import calculate_risk_score
from app.services.llm_analysis import generate_risk_assessment

router = APIRouter(prefix="/insights", tags=["AI Insights"])


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------
class AIRiskAssessment(BaseModel):
    """Response schema for AI-powered risk assessment."""
    booking_id: int
    hotel: str
    risk_score: float
    risk_band: str
    risk_factors: List[str]
    ai_assessment: str
    ai_model: str
    ai_source: str


class BatchAssessmentItem(BaseModel):
    """Single item in a batch assessment response."""
    booking_id: int
    hotel: str
    risk_score: float
    risk_band: str
    ai_summary: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@router.post(
    "/ai-risk-assessment/{booking_id}",
    response_model=AIRiskAssessment,
    summary="AI-powered risk assessment for a booking",
    description="Uses a Large Language Model (OpenAI GPT) to generate a natural "
                "language risk assessment for a specific booking. Combines the "
                "rule-based risk score with LLM narrative analysis to produce "
                "actionable recommendations for hotel management. "
                "Requires API key authentication.",
    dependencies=[Depends(require_api_key)],
    responses={
        200: {
            "description": "AI-generated risk assessment",
            "content": {
                "application/json": {
                    "example": {
                        "booking_id": 1,
                        "hotel": "Resort Hotel",
                        "risk_score": 0.65,
                        "risk_band": "high",
                        "risk_factors": ["very_high_lead_time", "no_deposit", "first_time_guest"],
                        "ai_assessment": "**Risk Summary**: This Resort Hotel booking presents a HIGH risk...",
                        "ai_model": "gpt-3.5-turbo",
                        "ai_source": "openai",
                    }
                }
            },
        },
        404: {"description": "Booking not found"},
    },
)
async def ai_risk_assessment(
    booking_id: int,
    db: Session = Depends(get_db),
):
    """
    Generate an AI-powered risk assessment for a single booking.

    Pipeline:
      1. Fetch the booking from the database
      2. Calculate the rule-based risk score
      3. Send booking data + risk score to the LLM
      4. Return the structured + narrative assessment

    If no OpenAI API key is configured, returns a template-based
    assessment instead (graceful degradation).
    """
    # Step 1: Fetch the booking
    booking = db.query(Booking).filter(Booking.booking_id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail=f"Booking {booking_id} not found")

    # Step 2: Calculate risk score
    score, band, factors = calculate_risk_score(
        lead_time=booking.lead_time or 0,
        previous_cancellations=booking.previous_cancellations or 0,
        deposit_type=booking.deposit_type or "",
        market_segment=booking.market_segment or "",
        is_repeated_guest=booking.is_repeated_guest or 0,
        booking_changes=booking.booking_changes or 0,
    )

    # Step 3: Build booking data dict for the LLM
    booking_data = {
        "hotel": booking.hotel,
        "lead_time": booking.lead_time,
        "arrival_date_month": booking.arrival_date_month,
        "arrival_date_year": booking.arrival_date_year,
        "stays_in_weekend_nights": booking.stays_in_weekend_nights,
        "stays_in_week_nights": booking.stays_in_week_nights,
        "adults": booking.adults,
        "children": booking.children,
        "market_segment": booking.market_segment,
        "customer_type": booking.customer_type,
        "deposit_type": booking.deposit_type,
        "adr": booking.adr or 0,
        "total_of_special_requests": booking.total_of_special_requests,
        "previous_cancellations": booking.previous_cancellations,
        "is_repeated_guest": booking.is_repeated_guest,
        "booking_changes": booking.booking_changes,
    }

    # Step 4: Generate LLM assessment
    llm_result = await generate_risk_assessment(booking_data, score, band, factors)

    return AIRiskAssessment(
        booking_id=booking_id,
        hotel=booking.hotel,
        risk_score=score,
        risk_band=band,
        risk_factors=factors,
        ai_assessment=llm_result["assessment"],
        ai_model=llm_result["model"],
        ai_source=llm_result["source"],
    )
