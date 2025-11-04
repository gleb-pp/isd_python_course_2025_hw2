from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import src.app.exceptions.events as event_errors
import src.app.exceptions.users as user_errors
import src.app.logic.events as events_logic
import src.app.logic.users as user_logic
from src.app.auth import get_current_user
from src.app.db import get_db
from src.app.models.common import Success
from src.app.models.events import EventBase, EventID, EventInfo

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
    event = events_logic.create_event(event_base, user_email, db)
    db.commit()
    return EventID.model_validate(event)


@router.delete("/{event_id}")
async def delete_event(
    event_id: int,
    user_email: Annotated[str, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Success:
    """Remove the event with provided event_id.

    Event Organizator role for the provided event_id required.
    """
    try:
        user = user_logic.get_user(user_email, db)
        event = events_logic.get_event(event_id, db)
        events_logic.assert_user_is_organizer(event, user)
        events_logic.delete_event(event, db)
        db.commit()
        return Success(success=True)
    except user_errors.UserNotFoundError as e:
        db.rollback()
        raise HTTPException(status_code=401, detail=str(e)) from e
    except event_errors.EventNotFoundError as e:
        db.rollback()
        raise HTTPException(status_code=404, detail=str(e)) from e
    except event_errors.OrginizatorRoleRequiredError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail=str(e)) from e


@router.get("/")
async def get_events_list(db: Annotated[Session, Depends(get_db)]) -> list[EventInfo]:
    """Get the list of available events with their main information.

    For each event, main information includes event ID, title, description, date,
    is_offline flag, location, organizer_email, and max_participants.
    """
    events = events_logic.get_events_list(db)
    return [EventInfo.model_validate(event) for event in events]


@router.get("/{event_id}")
async def get_event_info(
    event_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> EventInfo:
    """Get the main information about the event with provided event_id.

    Main information includes event ID, title, description, date,
    is_offline flag, location, organizer_email, and max_participants.
    """
    try:
        event = events_logic.get_event(event_id, db)
        return EventInfo.model_validate(event)
    except event_errors.EventNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
