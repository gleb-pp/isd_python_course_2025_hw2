from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import src.app.exceptions.bookings as booking_errors
import src.app.exceptions.events as event_errors
import src.app.logic.bookings
from src.app.auth import get_current_user
from src.app.db import get_db
from src.app.models.bookings import EventParticipants
from src.app.models.common import Success

router = APIRouter(
    prefix="/bookings",
    tags=["Bookings"],
)


@router.post("/")
async def create_booking(
    event_id: int,
    user_email: Annotated[str, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Success:
    """Register the user with provided email to the event with provided event_id.

    Registration is only possible for events with available seats.
    """
    try:
        src.app.logic.bookings.create_booking(event_id, user_email, db)
        db.commit()
        return Success(success=True)
    except event_errors.EventNotFoundError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e)) from e
    except booking_errors.EventFullError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail=str(e)) from e


@router.delete("/{event_id}")
async def delete_booking(
    event_id: int,
    user_email: Annotated[str, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Success:
    """Unregister the user with provided email from the event with provided event_id."""
    try:
        src.app.logic.bookings.delete_booking(event_id, user_email, db)
        db.commit()
        return Success(success=True)
    except event_errors.EventNotFoundError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/{event_id}")
async def get_event_participants(
    event_id: int,
    user_email: Annotated[str, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> EventParticipants:
    """Get the list of participants' emails for the event with provided event_id.

    Event Organizator role for the provided event_id required.
    """
    try:
        participants_emails = src.app.logic.bookings.get_event_participants(
            event_id, user_email, db
        )
        return EventParticipants(participants_emails=participants_emails)
    except event_errors.EventNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except event_errors.OrginizatorRoleRequiredError as e:
        raise HTTPException(status_code=403, detail=str(e)) from e
