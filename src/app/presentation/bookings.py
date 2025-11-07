from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import src.app.domain.exceptions.bookings as booking_errors
import src.app.domain.exceptions.events as event_errors
import src.app.domain.exceptions.users as user_errors
from src.app.auth import get_current_user
from src.app.db import get_db
from src.app.services.bookings import BookingService
from src.app.services.models.bookings import EventParticipants
from src.app.services.models.common import Success

router = APIRouter(
    prefix="/bookings",
    tags=["Bookings"],
)


@router.post("/{event_id}")
async def create_booking(
    event_id: int,
    user_email: Annotated[str, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Success:
    """Register the user with provided email to the event with provided event_id.

    Registration is only possible for events with available seats.
    """
    service = BookingService(db)
    try:
        return service.create_booking(event_id, user_email)
    except user_errors.UserNotFoundError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e
    except event_errors.EventNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except booking_errors.EventFullError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e


@router.delete("/{event_id}")
async def delete_booking(
    event_id: int,
    user_email: Annotated[str, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Success:
    """Unregister the user with provided email from the event with provided event_id."""
    service = BookingService(db)
    try:
        return service.delete_booking(event_id, user_email)
    except user_errors.UserNotFoundError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e
    except event_errors.EventNotFoundError as e:
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
    service = BookingService(db)
    try:
        return service.get_event_participants(event_id, user_email)
    except user_errors.UserNotFoundError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e
    except event_errors.EventNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except event_errors.OrginizatorRoleRequiredError as e:
        raise HTTPException(status_code=403, detail=str(e)) from e
