from sqlalchemy.orm import Session

import src.app.domain.exceptions.events as event_errors
from src.app.infrastructure.db_models.events import EventDB
from src.app.infrastructure.db_models.users import UserDB
from src.app.services.models.events import EventBase


def create_event(
    event_base: EventBase,
    organizer_email: str,
    db: Session,
) -> EventDB:
    """Create a new event in the database and return its ID."""
    event = EventDB(
        title=event_base.title,
        description=event_base.description,
        date=event_base.date,
        is_offline=event_base.is_offline,
        location=event_base.location,
        organizer_email=organizer_email,
        max_participants=event_base.max_participants,
    )
    db.add(event)
    db.flush()
    return event


def get_event(event_id: int, db: Session) -> EventDB:
    """Check whether an event with provided event_id exists in the system."""
    event = db.query(EventDB).filter_by(id=event_id).first()
    if event is None:
        raise event_errors.EventNotFoundError(event_id)
    return event


def assert_user_is_organizer(event: EventDB, user: UserDB) -> None:
    """Check whether the user with provided email is event organizer."""
    if event.organizer_email != user.email:
        raise event_errors.OrginizatorRoleRequiredError(event.id, user.email)


def delete_event(event: EventDB, db: Session) -> None:
    """Delete an event from the database."""
    db.delete(event)


def get_events_list(db: Session) -> list[EventDB]:
    """Retrieve a list of all events from the database."""
    return db.query(EventDB).all()
