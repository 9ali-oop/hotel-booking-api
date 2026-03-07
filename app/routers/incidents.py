"""
Incident endpoints — full CRUD for operational incident reports.

This is the primary user-generated resource. Hotel staff create incidents
to record operational issues (room mismatches, complaints, overbookings,
maintenance problems, no-shows) linked to specific booking records.

Supports: POST, GET (list + single), PUT (full update),
          PATCH (partial update), DELETE
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.database import get_db
from app.auth import require_api_key
from app.models import Incident, Booking
from app.schemas import (
    IncidentCreate, IncidentUpdate, IncidentPatch,
    IncidentResponse, MessageResponse
)

router = APIRouter(prefix="/incidents", tags=["Incidents"])


@router.post(
    "",
    response_model=IncidentResponse,
    status_code=201,
    summary="Create a new incident",
    description="Record a new operational incident linked to a booking. "
                "Validates that the booking exists and that severity is between 1-5. "
                "Requires API key authentication via X-API-Key header.",
    dependencies=[Depends(require_api_key)],
)
def create_incident(data: IncidentCreate, db: Session = Depends(get_db)):
    """Create a new incident report linked to a booking."""

    # Validate that the booking exists
    booking = db.query(Booking).filter(Booking.booking_id == data.booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=404,
            detail=f"Booking {data.booking_id} not found. Incident must be linked to an existing booking."
        )

    incident = Incident(
        booking_id=data.booking_id,
        incident_type=data.incident_type.value,
        severity=data.severity,
        description=data.description,
        reported_by=data.reported_by,
        status="open",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident


@router.get(
    "",
    response_model=List[IncidentResponse],
    summary="List incidents with filters",
    description="Retrieve incident reports. Optionally filter by booking ID, "
                "severity level, status, or incident type."
)
def list_incidents(
    booking_id: Optional[int] = Query(None, description="Filter by booking ID"),
    severity: Optional[int] = Query(None, ge=1, le=5, description="Filter by severity level"),
    status: Optional[str] = Query(None, description="Filter by status (open, investigating, resolved)"),
    incident_type: Optional[str] = Query(None, description="Filter by incident type"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List incidents with optional filters and pagination."""
    query = db.query(Incident)

    if booking_id is not None:
        query = query.filter(Incident.booking_id == booking_id)
    if severity is not None:
        query = query.filter(Incident.severity == severity)
    if status:
        query = query.filter(Incident.status == status)
    if incident_type:
        query = query.filter(Incident.incident_type == incident_type)

    incidents = query.order_by(Incident.created_at.desc()) \
                     .offset((page - 1) * per_page) \
                     .limit(per_page) \
                     .all()
    return incidents


@router.get(
    "/{incident_id}",
    response_model=IncidentResponse,
    summary="Get a single incident by ID"
)
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    """Retrieve a specific incident by its ID."""
    incident = db.query(Incident).filter(Incident.incident_id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")
    return incident


@router.put(
    "/{incident_id}",
    response_model=IncidentResponse,
    summary="Full update of an incident (PUT)",
    description="Replace all fields of an existing incident. All fields are required. "
                "Requires API key authentication.",
    dependencies=[Depends(require_api_key)],
)
def update_incident(incident_id: int, data: IncidentUpdate, db: Session = Depends(get_db)):
    """Full update (replace) of an incident."""
    incident = db.query(Incident).filter(Incident.incident_id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")

    incident.incident_type = data.incident_type.value
    incident.severity = data.severity
    incident.description = data.description
    incident.reported_by = data.reported_by
    incident.status = data.status.value
    incident.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(incident)
    return incident


@router.patch(
    "/{incident_id}",
    response_model=IncidentResponse,
    summary="Partial update of an incident (PATCH)",
    description="Update one or more fields of an existing incident. "
                "Only provided fields will be updated. "
                "Requires API key authentication.",
    dependencies=[Depends(require_api_key)],
)
def patch_incident(incident_id: int, data: IncidentPatch, db: Session = Depends(get_db)):
    """Partial update of an incident — only provided fields are changed."""
    incident = db.query(Incident).filter(Incident.incident_id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(value, "value"):  # Handle enum values
            value = value.value
        setattr(incident, field, value)

    incident.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(incident)
    return incident


@router.delete(
    "/{incident_id}",
    response_model=MessageResponse,
    summary="Delete an incident",
    description="Permanently remove an incident report. Requires API key authentication.",
    dependencies=[Depends(require_api_key)],
)
def delete_incident(incident_id: int, db: Session = Depends(get_db)):
    """Delete an incident by its ID."""
    incident = db.query(Incident).filter(Incident.incident_id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")

    db.delete(incident)
    db.commit()
    return MessageResponse(message=f"Incident {incident_id} deleted successfully")
