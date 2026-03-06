"""
Risk scoring service for identifying high-risk bookings.

Uses a rule-based heuristic derived from domain analysis of the
hotel booking dataset. Each risk factor contributes a weighted
score based on observed patterns in the data:

  - Long lead times correlate with higher cancellation rates
  - Previous cancellations are a strong predictor of future ones
  - No-deposit bookings have lower commitment
  - Online TA bookings show higher cancellation rates
  - First-time guests cancel more than repeat guests
  - Zero booking changes suggest less engagement

A production system might use a trained ML classifier, but the
heuristic approach is transparent, interpretable, and easy to
explain in a viva context.
"""

from typing import List, Tuple


def calculate_risk_score(
    lead_time: int,
    previous_cancellations: int,
    deposit_type: str,
    market_segment: str,
    is_repeated_guest: int,
    booking_changes: int,
) -> Tuple[float, str, List[str]]:
    """
    Calculate a cancellation risk score for a booking.

    Returns:
        Tuple of (risk_score: float 0-1, risk_band: str, risk_factors: list of strings)

    The risk_band classifies the score into actionable categories:
      - "low"    (0.0 - 0.29): Minimal cancellation concern
      - "medium" (0.30 - 0.59): Monitor and consider confirmation outreach
      - "high"   (0.60 - 1.0):  Proactive intervention recommended
    """
    score = 0.0
    factors = []

    # Factor 1: Lead time — bookings made far in advance cancel more
    if lead_time > 300:
        score += 0.25
        factors.append("very_high_lead_time")
    elif lead_time > 200:
        score += 0.15
        factors.append("high_lead_time")

    # Factor 2: Previous cancellations — strongest single predictor
    if previous_cancellations >= 3:
        score += 0.30
        factors.append("multiple_previous_cancellations")
    elif previous_cancellations >= 1:
        score += 0.20
        factors.append("previous_cancellation_history")

    # Factor 3: Deposit type — no deposit means lower commitment
    if deposit_type == "No Deposit":
        score += 0.15
        factors.append("no_deposit")

    # Factor 4: Market segment — Online TAs have higher cancellation rates
    if market_segment == "Online TA":
        score += 0.10
        factors.append("online_ta_segment")

    # Factor 5: Repeat guest — first-time guests cancel more
    if is_repeated_guest == 0:
        score += 0.10
        factors.append("first_time_guest")

    # Factor 6: Booking changes — zero changes may indicate less engagement
    if booking_changes == 0:
        score += 0.10
        factors.append("no_booking_changes")

    # Cap the score at 1.0
    score = min(score, 1.0)

    # Classify into risk bands for actionable interpretation
    if score >= 0.60:
        band = "high"
    elif score >= 0.30:
        band = "medium"
    else:
        band = "low"

    return round(score, 2), band, factors
