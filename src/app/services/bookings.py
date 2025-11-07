from sqlalchemy.orm import Session

from src.app.infrastructure.adapters.bookings_adapter import BookingsAdapter
from src.app.infrastructure.adapters.events_adapter import EventsAdapter
from src.app.infrastructure.adapters.users_adapter import UsersAdapter
from src.app.services.models.bookings import EventParticipants
from src.app.services.models.common import Success


class BookingService:
    """Service layer for the Bookings."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.bookings = BookingsAdapter(db)
        self.events = EventsAdapter(db)
        self.users = UsersAdapter(db)

    def create_booking(self, event_id: int, user_email: str) -> Success:
        """Register a user for an event."""
        user = self.users.get_user(user_email)
        event = self.events.get_event(event_id)
        self.bookings.assert_seats_available(event)
        self.bookings.create_booking(event, user)
        self.db.commit()
        return Success(success=True)

    def delete_booking(self, event_id: int, user_email: str) -> Success:
        """Delete the user booking."""
        user = self.users.get_user(user_email)
        event = self.events.get_event(event_id)
        self.bookings.delete_booking(event, user)
        self.db.commit()
        return Success(success=True)

    def get_event_participants(
        self, event_id: int, user_email: str
    ) -> EventParticipants:
        """Get the list of event's participants."""
        user = self.users.get_user(user_email)
        event = self.events.get_event(event_id)
        self.events.assert_user_is_organizer(event, user)
        participants_emails = self.bookings.get_event_participants(event)
        return EventParticipants(participants_emails=participants_emails)
