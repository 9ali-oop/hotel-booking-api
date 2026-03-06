"""
Booking endpoints — read-only access to the imported hotel booking dataset.

Provides paginated listing with multiple filter options, plus
individual booking retrieval by ID.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models import Booking
from app.schemas import BookingResponse, BookingListResponse

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.get(
    "",
    response_model=BookingListResponse,
    summary="List bookings with filters and pagination",
    description="Retrieve hotel booking records. Supports filtering by hotel, country, "
                "market segment, arrival month/year, cancellation status, and customer type. "
                "Results are paginated with configurable page size."
)
def list_bookings(
    hotel: Optional[str] = Query(None, description="Filter by hotel name (e.g., 'Resort Hotel')"),
    country: Optional[str] = Query(None, description="Filter by country code (e.g., 'PRT')"),
    market_segment: Optional[str] = Query(None, description="Filter by market segment (e.g., 'Online TA')"),
    arrival_month: Optional[str] = Query(None, description="Filter by arrival month (e.g., 'July')"),
    arrival_year: Optional[int] = Query(None, description="Filter by arrival year (e.g., 2016)"),
    is_canceled: Optional[int] = Query(None, ge=0, le=1, description="Filter by cancellation: 0 or 1"),
    customer_type: Optional[str] = Query(None, description="Filter by customer type"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Results per page (max 100)"),
    db: Session = Depends(get_db),
):
    """List bookings with optional filters and pagination."""
    query = db.query(Booking)

    # Apply filters
    if hotel:
        query = query.filter(Booking.hotel == hotel)
    if country:
        query = query.filter(Booking.country == country)
    if market_segment:
        query = query.filter(Booking.market_segment == market_segment)
    if arrival_month:
        query = query.filter(Booking.arrival_date_month == arrival_month)
    if arrival_year:
        query = query.filter(Booking.arrival_date_year == arrival_year)
    if is_canceled is not None:
        query = query.filter(Booking.is_canceled == is_canceled)
    if customer_type:
        query = query.filter(Booking.customer_type == customer_type)

    total = query.count()
    bookings = query.offset((page - 1) * per_page).limit(per_page).all()

    return BookingListResponse(
        total=total,
        page=page,
        per_page=per_page,
        bookings=bookings,
    )


@router.get(
    "/{booking_id}",
    response_model=BookingResponse,
    summary="Get a single booking by ID",
    description="Retrieve the full details of a specific booking record."
)
def get_booking(booking_id: int, db: Session = Depends(get_db)):
    """Retrieve a specific booking by its ID."""
    booking = db.query(Booking).filter(Booking.booking_id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail=f"Booking {booking_id} not found")
    return booking
