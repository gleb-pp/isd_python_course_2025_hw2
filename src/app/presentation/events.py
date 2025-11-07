from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import src.app.domain.exceptions.events as event_errors
import src.app.domain.exceptions.users as user_errors
from src.app.auth import get_current_user
from src.app.db import get_db
from src.app.services.events import EventService
from src.app.services.models.common import Success
from src.app.services.models.events import EventBase, EventID, EventInfo

router = APIRouter(
    prefix="/events",
    tags=["Events"],
)


@router.post("/")
async def create_event(
    event_base: EventBase,
    db: Annotated[Session, Depends(get_db)],
    user_email: Annotated[str, Depends(get_current_user)],
) -> EventID:
    """Create the event with provided title and description.

    Title must contain from 3 to 80 symbols.

    Description parameter is optional.
    If provided, it must contain from 3 to 1000 symbols.

    Location must contain from 3 to 200 symbols, it can be an online link or an address.

    Max number of participants is optional. If provided, it must be greater than 0.
    """
    service = EventService(db)
    try:
        return service.create_event(event_base, user_email)
    except user_errors.UserNotFoundError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e
    except event_errors.EventNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.delete("/{event_id}")
async def delete_event(
    event_id: int,
    user_email: Annotated[str, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Success:
    """Remove the event with provided event_id.

    Event Organizator role for the provided event_id required.
    """
    service = EventService(db)
    try:
        return service.delete_event(event_id, user_email)
    except user_errors.UserNotFoundError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e
    except event_errors.EventNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except event_errors.OrginizatorRoleRequiredError as e:
        raise HTTPException(status_code=403, detail=str(e)) from e


@router.get("/")
async def get_events_list(
    db: Annotated[Session, Depends(get_db)],
) -> list[EventInfo]:
    """Get the list of available events with their main information.

    For each event, main information includes event ID, title, description, date,
    is_offline flag, location, organizer_email, and max_participants.
    """
    service = EventService(db)
    return service.get_events_list()


@router.get("/{event_id}")
async def get_event_info(
    event_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> EventInfo:
    """Get the main information about the event with provided event_id.

    Main information includes event ID, title, description, date,
    is_offline flag, location, organizer_email, and max_participants.
    """
    service = EventService(db)
    try:
        return service.get_event_info(event_id)
    except event_errors.EventNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
