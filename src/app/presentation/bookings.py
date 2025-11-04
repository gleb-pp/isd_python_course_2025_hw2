from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import src.app.exceptions.bookings as booking_errors
import src.app.exceptions.events as event_errors
import src.app.exceptions.users as user_errors
import src.app.logic.bookings as bookings_logic
import src.app.logic.events as events_logic
import src.app.logic.users as user_logic
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
        user = user_logic.get_user(user_email, db)
        event = events_logic.get_event(event_id, db)
        bookings_logic.assert_seats_available(event, db)
        bookings_logic.create_booking(event, user, db)
        db.commit()
        return Success(success=True)
    except user_errors.UserNotFoundError as e:
        db.rollback()
        raise HTTPException(status_code=401, detail=str(e)) from e
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
        user = user_logic.get_user(user_email, db)
        event = events_logic.get_event(event_id, db)
        bookings_logic.delete_booking(event, user, db)
        db.commit()
        return Success(success=True)
    except user_errors.UserNotFoundError as e:
        db.rollback()
        raise HTTPException(status_code=401, detail=str(e)) from e
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
        user = user_logic.get_user(user_email, db)
        event = events_logic.get_event(event_id, db)
        events_logic.assert_user_is_organizer(event, user)
        participants_emails = bookings_logic.get_event_participants(event, db)
        return EventParticipants.model_validate(participants_emails)
    except user_errors.UserNotFoundError as e:
        db.rollback()
        raise HTTPException(status_code=401, detail=str(e)) from e
    except event_errors.EventNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except event_errors.OrginizatorRoleRequiredError as e:
        raise HTTPException(status_code=403, detail=str(e)) from e
