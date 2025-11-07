from sqlalchemy.orm import Session

from src.app.infrastructure.adapters.events_adapter import EventsAdapter
from src.app.infrastructure.adapters.users_adapter import UsersAdapter
from src.app.services.models.common import Success
from src.app.services.models.events import EventBase, EventID, EventInfo


class EventService:
    """Service layer for the Events."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.events = EventsAdapter(db)
        self.users = UsersAdapter(db)

    def create_event(self, event_base: EventBase, user_email: str) -> EventID:
        """Create a new event."""
        user = self.users.get_user(user_email)
        event = self.events.create_event(event_base, user.email)
        self.db.commit()
        return EventID.model_validate(event)

    def delete_event(self, event_id: int, user_email: str) -> Success:
        """Delete the event."""
        user = self.users.get_user(user_email)
        event = self.events.get_event(event_id)
        self.events.assert_user_is_organizer(event, user)
        self.events.delete_event(event)
        self.db.commit()
        return Success(success=True)

    def get_events_list(self) -> list[EventInfo]:
        """Get the list of all events."""
        events = self.events.get_events_list()
        return [EventInfo.model_validate(event) for event in events]

    def get_event_info(self, event_id: int) -> EventInfo:
        """Get the info about the event."""
        event = self.events.get_event(event_id)
        return EventInfo.model_validate(event)
