"""
SQLAlchemy ORM models representing the database tables.

Three tables:
  - Booking: imported from the Kaggle Hotel Booking Demand CSV (read-only via API)
  - Incident: user-generated operational issue reports (full CRUD)
  - ManagerNote: user-generated internal notes on bookings (full CRUD)
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Text, DateTime, ForeignKey, CheckConstraint
)
from sqlalchemy.orm import relationship
from app.database import Base


class Booking(Base):
    """
    Represents a single hotel booking record imported from the dataset.
    The schema mirrors the CSV columns. This table is read-only via the API —
    data is populated by the import script.
    """
    __tablename__ = "bookings"

    booking_id = Column(Integer, primary_key=True, autoincrement=True)
    hotel = Column(String, nullable=False, index=True)
    is_canceled = Column(Integer, nullable=False, default=0)
    lead_time = Column(Integer)
    arrival_date_year = Column(Integer)
    arrival_date_month = Column(String, index=True)
    arrival_date_week_number = Column(Integer)
    arrival_date_day_of_month = Column(Integer)
    stays_in_weekend_nights = Column(Integer)
    stays_in_week_nights = Column(Integer)
    adults = Column(Integer)
    children = Column(Integer)
    babies = Column(Integer)
    meal = Column(String)
    country = Column(String, index=True)
    market_segment = Column(String, index=True)
    distribution_channel = Column(String)
    is_repeated_guest = Column(Integer)
    previous_cancellations = Column(Integer)
    previous_bookings_not_canceled = Column(Integer)
    reserved_room_type = Column(String)
    assigned_room_type = Column(String)
    booking_changes = Column(Integer)
    deposit_type = Column(String)
    agent = Column(String)
    company = Column(String)
    days_in_waiting_list = Column(Integer)
    customer_type = Column(String)
    adr = Column(Float)
    required_car_parking_spaces = Column(Integer)
    total_of_special_requests = Column(Integer)
    reservation_status = Column(String)
    reservation_status_date = Column(String)

    # Relationships — a booking can have many incidents and notes
    incidents = relationship("Incident", back_populates="booking", cascade="all, delete-orphan")
    notes = relationship("ManagerNote", back_populates="booking", cascade="all, delete-orphan")


class Incident(Base):
    """
    Operational incident report linked to a booking.
    Staff use this to record issues such as room mismatches,
    guest complaints, overbookings, or maintenance problems.
    This is the main CRUD resource for the coursework.
    """
    __tablename__ = "incidents"

    incident_id = Column(Integer, primary_key=True, autoincrement=True)
    booking_id = Column(Integer, ForeignKey("bookings.booking_id"), nullable=False, index=True)
    incident_type = Column(String, nullable=False)
    severity = Column(Integer, nullable=False)
    description = Column(Text, nullable=False)
    reported_by = Column(String, nullable=False)
    status = Column(String, nullable=False, default="open")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Database-level constraints for data integrity
    __table_args__ = (
        CheckConstraint("severity >= 1 AND severity <= 5", name="check_severity_range"),
        CheckConstraint(
            "status IN ('open', 'investigating', 'resolved')",
            name="check_status_values"
        ),
        CheckConstraint(
            "incident_type IN ('room_mismatch', 'complaint', 'overbooking', 'maintenance', 'no_show', 'other')",
            name="check_incident_type_values"
        ),
    )

    booking = relationship("Booking", back_populates="incidents")


class ManagerNote(Base):
    """
    Internal note attached to a booking by hotel management.
    Supports the secondary CRUD resource requirement, showing
    relational design between bookings, incidents, and notes.
    """
    __tablename__ = "manager_notes"

    note_id = Column(Integer, primary_key=True, autoincrement=True)
    booking_id = Column(Integer, ForeignKey("bookings.booking_id"), nullable=False, index=True)
    note_text = Column(Text, nullable=False)
    author = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    booking = relationship("Booking", back_populates="notes")
