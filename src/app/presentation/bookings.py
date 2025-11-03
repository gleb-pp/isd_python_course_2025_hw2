from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from src.app.auth import get_current_user
from src.app.models.common import Success
from src.app.models.bookings import EventParticipants

router = APIRouter(
    prefix="/bookings",
    tags=["Bookings"],
)


@router.post("/")
async def create_booking(
    event_id: UUID, user_email: Annotated[str, Depends(get_current_user)]
) -> Success:
    """Register the user with provided email to the event with provided event_id.

    Registration is only possible for events with available seats.
    """


@router.delete("/{event_id}")
async def leave_event(
    event_id: UUID, user_email: Annotated[str, Depends(get_current_user)]
) -> Success:
    """Unregister the user with provided email from the event with provided event_id."""


@router.get("/{event_id}")
async def get_event_bookings(
    event_id: UUID, user_email: Annotated[str, Depends(get_current_user)]
) -> EventParticipants:
    """Get the list of participants' emails for the event with provided event_id.

    Event Organizator role for the provided event_id required.
    """
