"""
Manager Notes endpoints — CRUD for internal booking notes.

This is the secondary user-generated resource. Managers attach
internal notes to bookings for operational context. The simpler
schema (compared to incidents) demonstrates that the API supports
multiple related CRUD resources with proper foreign key relationships.

Supports: POST, GET (list + single), DELETE
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.database import get_db
from app.models import ManagerNote, Booking
from app.schemas import NoteCreate, NoteResponse, MessageResponse

router = APIRouter(prefix="/notes", tags=["Manager Notes"])


@router.post(
    "",
    response_model=NoteResponse,
    status_code=201,
    summary="Create a new manager note",
    description="Attach an internal note to a booking. "
                "Validates that the referenced booking exists."
)
def create_note(data: NoteCreate, db: Session = Depends(get_db)):
    """Create a new manager note linked to a booking."""

    # Validate that the booking exists
    booking = db.query(Booking).filter(Booking.booking_id == data.booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=404,
            detail=f"Booking {data.booking_id} not found. Note must be linked to an existing booking."
        )

    note = ManagerNote(
        booking_id=data.booking_id,
        note_text=data.note_text,
        author=data.author,
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@router.get(
    "",
    response_model=List[NoteResponse],
    summary="List manager notes",
    description="Retrieve manager notes. Optionally filter by booking ID or author."
)
def list_notes(
    booking_id: Optional[int] = Query(None, description="Filter by booking ID"),
    author: Optional[str] = Query(None, description="Filter by note author"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List manager notes with optional filters."""
    query = db.query(ManagerNote)

    if booking_id is not None:
        query = query.filter(ManagerNote.booking_id == booking_id)
    if author:
        query = query.filter(ManagerNote.author == author)

    notes = query.order_by(ManagerNote.created_at.desc()) \
                 .offset((page - 1) * per_page) \
                 .limit(per_page) \
                 .all()
    return notes


@router.get(
    "/{note_id}",
    response_model=NoteResponse,
    summary="Get a single note by ID"
)
def get_note(note_id: int, db: Session = Depends(get_db)):
    """Retrieve a specific manager note by its ID."""
    note = db.query(ManagerNote).filter(ManagerNote.note_id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail=f"Note {note_id} not found")
    return note


@router.delete(
    "/{note_id}",
    response_model=MessageResponse,
    summary="Delete a manager note"
)
def delete_note(note_id: int, db: Session = Depends(get_db)):
    """Delete a manager note by its ID."""
    note = db.query(ManagerNote).filter(ManagerNote.note_id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail=f"Note {note_id} not found")

    db.delete(note)
    db.commit()
    return MessageResponse(message=f"Note {note_id} deleted successfully")
