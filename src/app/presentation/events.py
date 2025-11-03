from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from src.app.auth import get_current_user
from src.app.models.common import Success
from src.app.models.events import EventID, EventInfo

router = APIRouter(
    prefix="/events",
    tags=["Events"],
)


@router.post("/")
async def create_event(
    title: Annotated[str, Query(..., min_length=3, max_length=80)],
    date: Annotated[datetime, Query(...)],
    is_offline: Annotated[bool, Query(...)],
    location: Annotated[str, Query(..., min_length=3, max_length=200)],
    user_email: Annotated[str, Depends(get_current_user)],
    description: Annotated[str | None, Query(min_length=3, max_length=1000)] = None,
    max_participants: Annotated[int | None, Query(gt=0)] = None,
) -> EventID:
    """Create the event with provided title and description.

    Title must contain from 3 to 80 symbols.

    Description parameter is optional.
    If provided, it must contain from 3 to 1000 symbols.

    Location must contain from 3 to 200 symbols, it can be an online link or an address.

    Max number of participants is optional. If provided, it must be greater than 0.
    """


@router.delete("/{event_id}")
async def delete_event(
    event_id: UUID, user_email: Annotated[str, Depends(get_current_user)]
) -> Success:
    """Remove the event with provided event_id.

    Event Organizator role for the provided event_id required.
    """


@router.get("/")
async def get_events_list(
    user_email: Annotated[str, Depends(get_current_user)],
) -> list[EventInfo]:
    """Get the list of available events with their main information.

    For each event, main information includes event ID, title, description, date,
    is_offline flag, location, organizator_email, max_participants,
    and number of participants registered.
    """


@router.get("/{event_id}")
async def get_event_info(
    event_id: UUID, user_email: Annotated[str, Depends(get_current_user)]
) -> EventInfo:
    """Get the main information about the event with provided event_id.

    Main information includes event ID, title, description, date,
    is_offline flag, location, organizator_email, max_participants,
    and number of participants registered.
    """
