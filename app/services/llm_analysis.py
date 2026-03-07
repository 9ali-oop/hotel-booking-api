"""
LLM-powered analysis service.

Integrates with OpenAI's GPT API to generate natural language risk
assessments and actionable recommendations for hotel bookings.

This is a "Creative application of Generative AI" — using an LLM
not just as a development tool, but as a runtime feature of the API
itself. The LLM analyses structured booking data and risk scores to
produce human-readable insights that hotel managers can act on.

Design decisions:
  - Uses OpenAI's Chat Completions API (industry standard)
  - Falls back gracefully if no API key is configured
  - Structured system prompt ensures consistent, professional output
  - Temperature set to 0.3 for deterministic, factual responses
  - Token limit keeps responses concise and cost-effective
  - The prompt includes the risk scoring factors so the LLM can
    explain WHY a booking is risky, not just that it is

Author: Ali
Module: COMP3011 Web Services and Web Data
"""

import os
import json
import logging
from typing import Optional

logger = logging.getLogger("hotel_api.llm")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")

# System prompt that frames the LLM's role and output expectations
SYSTEM_PROMPT = """You are a senior hotel revenue management analyst. Given structured booking data and a computed risk score, provide a concise, professional risk assessment.

Your response MUST follow this exact structure:
1. **Risk Summary** (1-2 sentences): Overall risk level and key concern.
2. **Key Risk Factors** (2-4 bullet points): Specific factors contributing to the risk, referencing the data.
3. **Recommended Actions** (2-3 bullet points): Practical steps hotel staff should take.
4. **Revenue Impact** (1 sentence): Estimated impact if the booking cancels.

Keep the total response under 200 words. Be specific — reference actual values from the booking data. Use professional hospitality industry language."""


def build_analysis_prompt(booking_data: dict, risk_score: float,
                          risk_band: str, risk_factors: list) -> str:
    """Build the user prompt with all booking context."""
    return f"""Analyse this hotel booking and provide a risk assessment:

BOOKING DATA:
- Hotel: {booking_data.get('hotel', 'Unknown')}
- Lead Time: {booking_data.get('lead_time', 0)} days
- Arrival: {booking_data.get('arrival_date_month', '')} {booking_data.get('arrival_date_year', '')}
- Nights: {booking_data.get('stays_in_weekend_nights', 0)} weekend + {booking_data.get('stays_in_week_nights', 0)} weekday
- Guests: {booking_data.get('adults', 0)} adults, {booking_data.get('children', 0) or 0} children
- Market Segment: {booking_data.get('market_segment', 'Unknown')}
- Customer Type: {booking_data.get('customer_type', 'Unknown')}
- Deposit: {booking_data.get('deposit_type', 'Unknown')}
- ADR (Avg Daily Rate): £{booking_data.get('adr', 0):.2f}
- Special Requests: {booking_data.get('total_of_special_requests', 0)}
- Previous Cancellations: {booking_data.get('previous_cancellations', 0)}
- Repeated Guest: {'Yes' if booking_data.get('is_repeated_guest', 0) else 'No'}
- Booking Changes: {booking_data.get('booking_changes', 0)}

RISK ANALYSIS:
- Computed Risk Score: {risk_score} / 1.0
- Risk Band: {risk_band.upper()}
- Contributing Factors: {', '.join(risk_factors) if risk_factors else 'None identified'}

Provide your professional risk assessment following the required structure."""


async def generate_risk_assessment(
    booking_data: dict,
    risk_score: float,
    risk_band: str,
    risk_factors: list,
) -> dict:
    """
    Call the OpenAI API to generate a natural language risk assessment.

    Returns a dict with:
      - assessment: str (the LLM-generated text)
      - model: str (which model was used)
      - tokens_used: int (total tokens consumed)

    Falls back to a template-based response if the API is unavailable.
    """
    user_prompt = build_analysis_prompt(booking_data, risk_score, risk_band, risk_factors)

    # If no API key, fall back to template-based response
    if not OPENAI_API_KEY:
        logger.info("No OPENAI_API_KEY set — using template-based assessment")
        return _template_fallback(booking_data, risk_score, risk_band, risk_factors)

    try:
        import httpx

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": OPENAI_MODEL,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                    "temperature": 0.3,
                    "max_tokens": 400,
                },
            )

            if response.status_code != 200:
                logger.warning("OpenAI API error %s: %s", response.status_code, response.text)
                return _template_fallback(booking_data, risk_score, risk_band, risk_factors)

            result = response.json()
            assessment_text = result["choices"][0]["message"]["content"]
            tokens_used = result.get("usage", {}).get("total_tokens", 0)

            return {
                "assessment": assessment_text,
                "model": OPENAI_MODEL,
                "tokens_used": tokens_used,
                "source": "openai",
            }

    except Exception as exc:
        logger.warning("LLM call failed: %s — using template fallback", exc)
        return _template_fallback(booking_data, risk_score, risk_band, risk_factors)


def _template_fallback(
    booking_data: dict, risk_score: float, risk_band: str, risk_factors: list
) -> dict:
    """
    Generate a structured assessment without an LLM API call.

    This ensures the endpoint always returns useful content, even when
    the OpenAI API key is not configured or the service is unavailable.
    This graceful degradation is a production best practice.
    """
    hotel = booking_data.get("hotel", "the hotel")
    lead_time = booking_data.get("lead_time", 0)
    adr = booking_data.get("adr", 0)
    nights = (booking_data.get("stays_in_weekend_nights", 0) or 0) + \
             (booking_data.get("stays_in_week_nights", 0) or 0)
    total_revenue = adr * max(nights, 1)

    factor_descriptions = {
        "very_high_lead_time": f"Very high lead time ({lead_time} days) significantly increases cancellation probability",
        "high_lead_time": f"High lead time ({lead_time} days) increases cancellation probability",
        "multiple_previous_cancellations": f"Multiple previous cancellations ({booking_data.get('previous_cancellations', 0)}) — strongest risk indicator",
        "previous_cancellation_history": "Previous cancellation history suggests pattern behaviour",
        "no_deposit": "No deposit means lower financial commitment to the booking",
        "online_ta_segment": "Online Travel Agency bookings have higher cancellation rates industry-wide",
        "first_time_guest": "First-time guest with no loyalty history",
        "no_booking_changes": "Zero booking modifications may indicate lower engagement",
    }

    factor_lines = []
    for f in risk_factors:
        desc = factor_descriptions.get(f, f.replace("_", " ").title())
        factor_lines.append(f"- {desc}")

    if risk_band == "high":
        summary = f"This {hotel} booking presents a HIGH cancellation risk (score: {risk_score}/1.0). Immediate attention recommended."
        actions = [
            "- Send a personalised confirmation email within 48 hours",
            "- Consider requiring a deposit or guarantee",
            "- Flag for revenue manager review and prepare waitlist backup",
        ]
    elif risk_band == "medium":
        summary = f"This {hotel} booking has a MODERATE cancellation risk (score: {risk_score}/1.0). Monitoring advised."
        actions = [
            "- Schedule an automated confirmation reminder 7 days before arrival",
            "- Monitor for booking changes as indicators of intent",
            "- Consider flexible overbooking strategy for this period",
        ]
    else:
        summary = f"This {hotel} booking has a LOW cancellation risk (score: {risk_score}/1.0). Standard processing appropriate."
        actions = [
            "- Process through standard booking workflow",
            "- Send standard pre-arrival communication",
        ]

    assessment = f"""**Risk Summary**: {summary}

**Key Risk Factors**:
{chr(10).join(factor_lines) if factor_lines else '- No significant risk factors identified'}

**Recommended Actions**:
{chr(10).join(actions)}

**Revenue Impact**: If cancelled, estimated revenue loss of £{total_revenue:.2f} ({nights} night{'s' if nights != 1 else ''} at £{adr:.2f} ADR)."""

    return {
        "assessment": assessment,
        "model": "template-based (no LLM API key configured)",
        "tokens_used": 0,
        "source": "template",
    }
