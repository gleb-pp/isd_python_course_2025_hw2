from sqlalchemy.orm import Session

import src.app.domain.exceptions.events as event_errors
from src.app.infrastructure.db_models.events import EventDB
from src.app.infrastructure.db_models.users import UserDB
from src.app.services.models.events import EventBase


class EventsAdapter:
    """Adapter for working with events."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create_event(self, event_base: EventBase, organizer_email: str) -> EventDB:
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
        self.db.add(event)
        self.db.flush()
        return event

    def get_event(self, event_id: int) -> EventDB:
        """Check whether an event with provided event_id exists in the system."""
        event = self.db.query(EventDB).filter_by(id=event_id).first()
        if event is None:
            raise event_errors.EventNotFoundError(event_id)
        return event

    def delete_event(self, event: EventDB) -> None:
        """Delete an event from the database."""
        self.db.delete(event)

    def get_events_list(self) -> list[EventDB]:
        """Retrieve a list of all events from the database."""
        return self.db.query(EventDB).all()

    @staticmethod
    def assert_user_is_organizer(event: EventDB, user: UserDB) -> None:
        """Check whether the user with provided email is event organizer."""
        if event.organizer_email != user.email:
            raise event_errors.OrginizatorRoleRequiredError(event.id, user.email)
