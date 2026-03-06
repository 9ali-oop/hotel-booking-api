"""
Pydantic schemas for request validation and response serialization.

FastAPI uses these to:
  1. Validate incoming JSON request bodies automatically
  2. Serialize outgoing responses to JSON
  3. Generate the interactive Swagger documentation

Each resource (Booking, Incident, ManagerNote) has separate schemas
for creation, update, and response — following REST best practices.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


# ─── Enums for constrained fields ────────────────────────────────────

class IncidentType(str, Enum):
    room_mismatch = "room_mismatch"
    complaint = "complaint"
    overbooking = "overbooking"
    maintenance = "maintenance"
    no_show = "no_show"
    other = "other"


class IncidentStatus(str, Enum):
    open = "open"
    investigating = "investigating"
    resolved = "resolved"


# ─── Booking Schemas ─────────────────────────────────────────────────

class BookingResponse(BaseModel):
    """Schema for booking data returned by the API."""
    model_config = ConfigDict(from_attributes=True)

    booking_id: int
    hotel: str
    is_canceled: int
    lead_time: int
    arrival_date_year: int
    arrival_date_month: str
    arrival_date_week_number: int
    arrival_date_day_of_month: int
    stays_in_weekend_nights: int
    stays_in_week_nights: int
    adults: int
    children: Optional[int] = None
    babies: Optional[int] = None
    meal: Optional[str] = None
    country: Optional[str] = None
    market_segment: Optional[str] = None
    distribution_channel: Optional[str] = None
    is_repeated_guest: int
    previous_cancellations: int
    previous_bookings_not_canceled: int
    reserved_room_type: Optional[str] = None
    assigned_room_type: Optional[str] = None
    booking_changes: int
    deposit_type: Optional[str] = None
    agent: Optional[str] = None
    company: Optional[str] = None
    days_in_waiting_list: int
    customer_type: Optional[str] = None
    adr: float
    required_car_parking_spaces: int
    total_of_special_requests: int
    reservation_status: Optional[str] = None
    reservation_status_date: Optional[str] = None


class BookingListResponse(BaseModel):
    """Paginated response wrapper for booking lists."""
    total: int
    page: int
    per_page: int
    bookings: List[BookingResponse]


# ─── Incident Schemas ────────────────────────────────────────────────

class IncidentCreate(BaseModel):
    """Schema for creating a new incident. Validates all required fields."""
    booking_id: int = Field(..., description="ID of the related booking")
    incident_type: IncidentType = Field(..., description="Category of the incident")
    severity: int = Field(..., ge=1, le=5, description="Severity level from 1 (low) to 5 (critical)")
    description: str = Field(..., min_length=5, max_length=1000, description="Details of the incident")
    reported_by: str = Field(..., min_length=1, max_length=100, description="Name of the person reporting")


class IncidentUpdate(BaseModel):
    """Schema for full update of an incident (PUT)."""
    incident_type: IncidentType
    severity: int = Field(..., ge=1, le=5)
    description: str = Field(..., min_length=5, max_length=1000)
    reported_by: str = Field(..., min_length=1, max_length=100)
    status: IncidentStatus


class IncidentPatch(BaseModel):
    """Schema for partial update of an incident (PATCH). All fields optional."""
    incident_type: Optional[IncidentType] = None
    severity: Optional[int] = Field(None, ge=1, le=5)
    description: Optional[str] = Field(None, min_length=5, max_length=1000)
    reported_by: Optional[str] = Field(None, min_length=1, max_length=100)
    status: Optional[IncidentStatus] = None


class IncidentResponse(BaseModel):
    """Schema for incident data returned by the API."""
    model_config = ConfigDict(from_attributes=True)

    incident_id: int
    booking_id: int
    incident_type: str
    severity: int
    description: str
    reported_by: str
    status: str
    created_at: datetime
    updated_at: datetime


# ─── Manager Note Schemas ────────────────────────────────────────────

class NoteCreate(BaseModel):
    """Schema for creating a new manager note."""
    booking_id: int = Field(..., description="ID of the related booking")
    note_text: str = Field(..., min_length=1, max_length=2000, description="Content of the note")
    author: str = Field(..., min_length=1, max_length=100, description="Author of the note")


class NoteResponse(BaseModel):
    """Schema for note data returned by the API."""
    model_config = ConfigDict(from_attributes=True)

    note_id: int
    booking_id: int
    note_text: str
    author: str
    created_at: datetime


# ─── Analytics Schemas ───────────────────────────────────────────────

class CancellationStats(BaseModel):
    """Response schema for cancellation rate analytics."""
    hotel: Optional[str] = None
    total_bookings: int
    cancellations: int
    cancellation_rate: float


class MonthlyDemand(BaseModel):
    """Response schema for monthly booking demand."""
    month: str
    year: int
    booking_count: int


class MarketSegmentStats(BaseModel):
    """Response schema for market segment performance."""
    market_segment: str
    total_bookings: int
    cancellations: int
    cancellation_rate: float
    average_adr: float


# ─── Insight Schemas ─────────────────────────────────────────────────

class HighRiskBooking(BaseModel):
    """Response schema for high-risk booking identification."""
    model_config = ConfigDict(from_attributes=True)

    booking_id: int
    hotel: str
    lead_time: int
    previous_cancellations: int
    deposit_type: Optional[str]
    market_segment: Optional[str]
    risk_score: float
    risk_band: str
    risk_factors: List[str]


class OperationalHotspot(BaseModel):
    """Response schema for operational hotspot analysis."""
    hotel: str
    month: str
    incident_count: int
    avg_severity: float


# ─── Generic Message ─────────────────────────────────────────────────

class MessageResponse(BaseModel):
    """Generic response for delete operations etc."""
    message: str
