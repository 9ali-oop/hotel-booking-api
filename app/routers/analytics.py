"""
Analytics endpoints — aggregated insights from the booking dataset.

These endpoints go beyond basic CRUD by providing computed statistics
that demonstrate the API's analytical capabilities. Each endpoint
runs SQL aggregation queries through SQLAlchemy.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List

from app.database import get_db
from app.models import Booking
from app.schemas import CancellationStats, MonthlyDemand, MarketSegmentStats

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get(
    "/cancellation-rate",
    response_model=List[CancellationStats],
    summary="Cancellation rate statistics",
    description="Returns overall and per-hotel cancellation rates. "
                "Optionally filter by a specific hotel."
)
def cancellation_rate(
    hotel: Optional[str] = Query(None, description="Filter by hotel name"),
    db: Session = Depends(get_db),
):
    """
    Calculate cancellation rates, either overall or per hotel.
    If a hotel is specified, returns stats for that hotel only.
    Otherwise returns overall + per-hotel breakdown.
    """
    results = []

    if hotel:
        # Stats for a specific hotel
        row = db.query(
            func.count(Booking.booking_id).label("total"),
            func.sum(Booking.is_canceled).label("canceled"),
        ).filter(Booking.hotel == hotel).first()

        total = row.total or 0
        canceled = int(row.canceled or 0)
        results.append(CancellationStats(
            hotel=hotel,
            total_bookings=total,
            cancellations=canceled,
            cancellation_rate=round(canceled / total, 4) if total > 0 else 0,
        ))
    else:
        # Overall stats
        overall = db.query(
            func.count(Booking.booking_id).label("total"),
            func.sum(Booking.is_canceled).label("canceled"),
        ).first()

        total = overall.total or 0
        canceled = int(overall.canceled or 0)
        results.append(CancellationStats(
            hotel=None,
            total_bookings=total,
            cancellations=canceled,
            cancellation_rate=round(canceled / total, 4) if total > 0 else 0,
        ))

        # Per-hotel breakdown
        hotel_stats = db.query(
            Booking.hotel,
            func.count(Booking.booking_id).label("total"),
            func.sum(Booking.is_canceled).label("canceled"),
        ).group_by(Booking.hotel).all()

        for row in hotel_stats:
            h_total = row.total or 0
            h_canceled = int(row.canceled or 0)
            results.append(CancellationStats(
                hotel=row.hotel,
                total_bookings=h_total,
                cancellations=h_canceled,
                cancellation_rate=round(h_canceled / h_total, 4) if h_total > 0 else 0,
            ))

    return results


@router.get(
    "/monthly-demand",
    response_model=List[MonthlyDemand],
    summary="Monthly booking demand",
    description="Returns booking counts grouped by month and year. "
                "Useful for identifying seasonal demand patterns."
)
def monthly_demand(
    hotel: Optional[str] = Query(None, description="Filter by hotel name"),
    year: Optional[int] = Query(None, description="Filter by year"),
    db: Session = Depends(get_db),
):
    """Aggregate booking counts by arrival month and year."""
    query = db.query(
        Booking.arrival_date_month,
        Booking.arrival_date_year,
        func.count(Booking.booking_id).label("count"),
    )

    if hotel:
        query = query.filter(Booking.hotel == hotel)
    if year:
        query = query.filter(Booking.arrival_date_year == year)

    rows = query.group_by(
        Booking.arrival_date_year, Booking.arrival_date_month
    ).order_by(
        Booking.arrival_date_year, Booking.arrival_date_month
    ).all()

    # Define month order for proper sorting
    month_order = {
        "January": 1, "February": 2, "March": 3, "April": 4,
        "May": 5, "June": 6, "July": 7, "August": 8,
        "September": 9, "October": 10, "November": 11, "December": 12,
    }

    results = [
        MonthlyDemand(
            month=row.arrival_date_month,
            year=row.arrival_date_year,
            booking_count=row.count,
        )
        for row in rows
    ]

    # Sort by year then month
    results.sort(key=lambda x: (x.year, month_order.get(x.month, 0)))
    return results


@router.get(
    "/market-segment-performance",
    response_model=List[MarketSegmentStats],
    summary="Market segment performance",
    description="Compares booking volume, cancellation rate, and average daily rate "
                "across market segments (Online TA, Direct, Corporate, etc.)."
)
def market_segment_performance(
    hotel: Optional[str] = Query(None, description="Filter by hotel name"),
    db: Session = Depends(get_db),
):
    """Analyse performance metrics by market segment."""
    query = db.query(
        Booking.market_segment,
        func.count(Booking.booking_id).label("total"),
        func.sum(Booking.is_canceled).label("canceled"),
        func.avg(Booking.adr).label("avg_adr"),
    )

    if hotel:
        query = query.filter(Booking.hotel == hotel)

    rows = query.group_by(Booking.market_segment) \
                .order_by(func.count(Booking.booking_id).desc()) \
                .all()

    return [
        MarketSegmentStats(
            market_segment=row.market_segment or "Unknown",
            total_bookings=row.total,
            cancellations=int(row.canceled or 0),
            cancellation_rate=round(int(row.canceled or 0) / row.total, 4) if row.total > 0 else 0,
            average_adr=round(row.avg_adr or 0, 2),
        )
        for row in rows
    ]
