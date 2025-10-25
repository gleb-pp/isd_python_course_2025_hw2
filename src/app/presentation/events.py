from typing import Annotated
from uuid import UUID

from auth import get_current_user
from classes.common import Success
from classes.events import EventFullInfo, EventID, EventMainInfo
from fastapi import APIRouter, Depends, Query

router = APIRouter()


@router.post("/events", tags=["Events"])
async def create_event(
    title: Annotated[
        str,
        Query(
            ...,
            min_length=3,
            max_length=80,
            description="Event must contain 3-80 symbols",
        ),
    ],
    description: Annotated[
        str | None,
        Query(
            None,
            min_length=3,
            max_length=1000,
            description="Event description must contain 3–1000 symbols",
        ),
    ],
) -> EventID:
    """Create the event with provided title and description.

    Title must contain from 3 to 80 symbols.

    Description parameter is optional.

    If description is passed, it must contain from 3 to 1000 symbols.
    """


@router.delete("/events/{event_id}", tags=["Events"])
async def delete_event(
    event_id: UUID, user_email: Annotated[str, Depends(get_current_user)]
) -> Success:
    """Remove the event with provided event_id.

    Event Organizator role for the provided event_id required.
    """


@router.get("/events", tags=["Events"])
async def get_events(
    event_id: UUID, user_email: Annotated[str, Depends(get_current_user)]
) -> list[EventMainInfo]:
    """Get the list of available events with their main information.

    For each event, main information includes event ID,
    title, description, date, organizator_email, max_number_of_participants,
    and number of participants registered.
    """


@router.get("/events/{event_id}/info", tags=["Events"])
async def event_info(
    event_id: UUID, user_email: Annotated[str, Depends(get_current_user)]
) -> EventMainInfo:
    """Get the main information about the event with provided event_id.

    Main information includes event ID, title, description, date, organizator_email,
    max_number_of_participants, and number of participants registered.
    """


@router.get("/events/{event_id}/details", tags=["Events"])
async def event_details(
    event_id: UUID, user_email: Annotated[str, Depends(get_current_user)]
) -> EventFullInfo:
    """Get detailed information about the event with provided event_id.

    Detailed information includes event ID, title, description,
    date, organizator_email, max_number_of_participants,
    number of participants registered, and the list of participants' emails.

    Event Organizator role for the provided event_id required.
    """


@router.patch("/events/{event_id}/join", tags=["Events"])
async def join_event(
    event_id: UUID, user_email: Annotated[str, Depends(get_current_user)]
) -> Success:
    """Register the user with provided email to the event with provided event_id.

    Registration is only possible for events with available seats.
    """


@router.patch("/events/{event_id}/leave", tags=["Events"])
async def leave_event(
    event_id: UUID, user_email: Annotated[str, Depends(get_current_user)]
) -> Success:
    """Unregister the user with provided email from the event with provided event_id."""
