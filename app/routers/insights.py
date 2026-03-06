"""
Insight endpoints — intelligent analysis that goes beyond simple aggregation.

These endpoints demonstrate higher-level API capabilities:
  - High-risk booking identification using a rule-based scoring heuristic
  - Operational hotspot detection combining incident and booking data

These are the "wow factor" endpoints for the viva.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from app.database import get_db
from app.models import Booking, Incident
from app.schemas import HighRiskBooking, OperationalHotspot
from app.services.risk_scoring import calculate_risk_score

router = APIRouter(prefix="/insights", tags=["Insights"])


@router.get(
    "/high-risk-bookings",
    response_model=List[HighRiskBooking],
    summary="Identify high-risk bookings",
    description="Uses a rule-based scoring heuristic to identify bookings with "
                "a high probability of cancellation. Factors include lead time, "
                "previous cancellations, deposit type, market segment, guest history, "
                "and booking changes. Returns bookings sorted by risk score (descending)."
)
def high_risk_bookings(
    min_risk: float = Query(0.5, ge=0, le=1, description="Minimum risk score threshold"),
    hotel: Optional[str] = Query(None, description="Filter by hotel name"),
    limit: int = Query(50, ge=1, le=500, description="Maximum results to return"),
    db: Session = Depends(get_db),
):
    """
    Identify bookings with high cancellation risk.

    The risk scoring algorithm considers six factors:
      1. Lead time (>200 days = higher risk)
      2. Previous cancellations (strongest predictor)
      3. Deposit type (no deposit = higher risk)
      4. Market segment (Online TA = higher risk)
      5. Guest type (first-time = higher risk)
      6. Booking changes (zero changes = higher risk)
    """
    # Query non-canceled bookings only (we're predicting future risk)
    query = db.query(Booking).filter(Booking.is_canceled == 0)

    if hotel:
        query = query.filter(Booking.hotel == hotel)

    # Process bookings and score them
    scored_bookings = []

    # Fetch in batches to avoid loading all 119K records at once
    batch_size = 5000
    offset = 0

    while True:
        batch = query.offset(offset).limit(batch_size).all()
        if not batch:
            break

        for booking in batch:
            score, band, factors = calculate_risk_score(
                lead_time=booking.lead_time or 0,
                previous_cancellations=booking.previous_cancellations or 0,
                deposit_type=booking.deposit_type or "",
                market_segment=booking.market_segment or "",
                is_repeated_guest=booking.is_repeated_guest or 0,
                booking_changes=booking.booking_changes or 0,
            )

            if score >= min_risk:
                scored_bookings.append(HighRiskBooking(
                    booking_id=booking.booking_id,
                    hotel=booking.hotel,
                    lead_time=booking.lead_time or 0,
                    previous_cancellations=booking.previous_cancellations or 0,
                    deposit_type=booking.deposit_type,
                    market_segment=booking.market_segment,
                    risk_score=score,
                    risk_band=band,
                    risk_factors=factors,
                ))

        offset += batch_size

    # Sort by risk score descending and apply limit
    scored_bookings.sort(key=lambda x: x.risk_score, reverse=True)
    return scored_bookings[:limit]


@router.get(
    "/operational-hotspots",
    response_model=List[OperationalHotspot],
    summary="Identify operational hotspots",
    description="Analyses incident reports alongside booking data to find "
                "which hotels and time periods experience the most operational issues. "
                "Helps management allocate resources proactively."
)
def operational_hotspots(db: Session = Depends(get_db)):
    """
    Find periods and hotels with the highest concentration of incidents.
    Groups by hotel and arrival month, showing incident count and average severity.
    """
    # Join incidents with bookings to get hotel and month context
    rows = db.query(
        Booking.hotel,
        Booking.arrival_date_month,
        func.count(Incident.incident_id).label("incident_count"),
        func.avg(Incident.severity).label("avg_severity"),
    ).join(
        Incident, Incident.booking_id == Booking.booking_id
    ).group_by(
        Booking.hotel, Booking.arrival_date_month
    ).order_by(
        func.count(Incident.incident_id).desc()
    ).all()

    return [
        OperationalHotspot(
            hotel=row.hotel,
            month=row.arrival_date_month,
            incident_count=row.incident_count,
            avg_severity=round(row.avg_severity, 2),
        )
        for row in rows
    ]
