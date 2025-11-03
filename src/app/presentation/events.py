from datetime import datetime
from typing import Annotated
from uuid import UUID
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, Query, HTTPException

from src.app.auth import get_current_user
from src.app.models.common import Success
from src.app.models.events import EventID, EventInfo
import src.app.exceptions.events as event_errors
import src.app.logic.events
from src.app.db import get_db

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
    db: Session = Depends(get_db)
) -> EventID:
    """Create the event with provided title and description.

    Title must contain from 3 to 80 symbols.

    Description parameter is optional.
    If provided, it must contain from 3 to 1000 symbols.

    Location must contain from 3 to 200 symbols, it can be an online link or an address.

    Max number of participants is optional. If provided, it must be greater than 0.
    """

    event_id = src.app.logic.events.create_event(title, date, is_offline, location,
                                     user_email, description, max_participants)
    db.commit()
    return EventID(event_id=event_id)


@router.delete("/{event_id}")
async def delete_event(
    event_id: UUID, user_email: Annotated[str, Depends(get_current_user)],
    db: Session = Depends(get_db)
) -> Success:
    """Remove the event with provided event_id.

    Event Organizator role for the provided event_id required.
    """

    try:
        src.app.logic.events.delete_event(event_id, user_email, db)
        db.commit()
        return Success(success=True)
    except event_errors.EventNotFoundError as e:
        db.rollback()
        raise HTTPException(status_code=404, detail=str(e))
    except event_errors.OrginizatorRoleRequiredError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail=str(e))


@router.get("/")
async def get_events_list(
    db: Session = Depends(get_db)
) -> list[EventInfo]:
    """Get the list of available events with their main information.

    For each event, main information includes event ID, title, description, date,
    is_offline flag, location, organizer_email, and max_participants.
    """
    events = src.app.logic.events.get_events_list(db)
    return [EventInfo.model_validate(event) for event in events]


@router.get("/{event_id}")
async def get_event_info(
    event_id: UUID, user_email: Annotated[str, Depends(get_current_user)],
    db: Session = Depends(get_db)
) -> EventInfo:
    """Get the main information about the event with provided event_id.

    Main information includes event ID, title, description, date,
    is_offline flag, location, organizer_email, and max_participants.
    """

    try:
        src.app.logic.events.get_event_info(event_id, db)
        db.commit()
        return Success(success=True)
    except event_errors.EventNotFoundError as e:
        db.rollback()
        raise HTTPException(status_code=404, detail=str(e))
