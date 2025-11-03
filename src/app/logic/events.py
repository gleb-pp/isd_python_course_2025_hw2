from datetime import datetime

from sqlalchemy.orm import Session

import src.app.exceptions.events as event_errors
from src.app.repo.events import Event


def create_event(
    title: str,
    date: datetime,
    location: str,
    organizer_email: str,
    description: str | None,
    max_participants: int | None,
    db: Session,
    is_offline: bool = True,
) -> int:
    """Create a new event in the database and return its ID."""
    event = Event(
        title=title,
        description=description,
        date=date,
        is_offline=is_offline,
        location=location,
        organizer_email=organizer_email,
        max_participants=max_participants,
    )
    db.add(event)
    db.flush()
    return event.id


def delete_event(event_id: int, organizer_email: str, db: Session) -> None:
    """Delete an event from the database if the organizer_email matches."""
    event = db.query(Event).filter_by(id=event_id).first()
    if event is None:
        raise event_errors.EventNotFoundError(event_id)
    if event.organizer_email != organizer_email:
        raise event_errors.OrginizatorRoleRequiredError(event_id, organizer_email)

    db.delete(event)


def get_events_list(db: Session) -> list[Event]:
    """Retrieve a list of all events from the database."""
    return db.query(Event).all()


def get_event_info(event_id: int, db: Session) -> Event:
    """Retrieve detailed information about a specific event by its ID."""
    event = db.query(Event).filter_by(id=event_id).first()
    if event is None:
        raise event_errors.EventNotFoundError(event_id)
    return event
