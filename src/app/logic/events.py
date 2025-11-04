from datetime import datetime

from sqlalchemy.orm import Session

import src.app.exceptions.events as event_errors
from src.app.repo.events import Event
from src.app.repo.users import User


def create_event(
    title: str,
    date: datetime,
    location: str,
    organizer_email: str,
    description: str | None,
    max_participants: int | None,
    db: Session,
    is_offline: bool = True,
) -> Event:
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
    return event


def get_event(event_id: int, db: Session) -> Event:
    """Check whether an event with provided event_id exists in the system."""
    event = db.query(Event).filter_by(id=event_id).first()
    if event is None:
        raise event_errors.EventNotFoundError(event_id)
    return event


def assert_user_is_organizer(event: Event, user: User, db: Session) -> None:
    """Check whether the user with provided email is event organizer."""
    if event.organizer_email != user.email:
        raise event_errors.OrginizatorRoleRequiredError(event.id, user.email)


def delete_event(event: Event, db: Session) -> None:
    """Delete an event from the database."""
    db.delete(event)


def get_events_list(db: Session) -> list[Event]:
    """Retrieve a list of all events from the database."""
    return db.query(Event).all()
