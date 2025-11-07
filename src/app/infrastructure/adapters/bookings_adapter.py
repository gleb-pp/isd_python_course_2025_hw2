from sqlalchemy.orm import Session

import src.app.domain.exceptions.bookings as booking_errors
from src.app.infrastructure.db_models.bookings import BookingDB
from src.app.infrastructure.db_models.events import EventDB
from src.app.infrastructure.db_models.users import UserDB


class BookingsAdapter:
    """Adapter for working with bookings."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create_booking(self, event: EventDB, user: UserDB) -> None:
        """Register the user with provided email to the event with provided event_id."""
        existing_booking = (
            self.db.query(BookingDB)
            .filter_by(event_id=event.id, user_email=user.email)
            .first()
        )
        if existing_booking:
            return

        new_booking = BookingDB(event_id=event.id, user_email=user.email)
        self.db.add(new_booking)

    def assert_seats_available(self, event: EventDB) -> None:
        """Check if there are any available seats left in the event."""
        if event.max_participants is not None:
            current_participants = (
                self.db.query(BookingDB).filter_by(event_id=event.id).count()
            )
            if current_participants >= event.max_participants:
                raise booking_errors.EventFullError(event.id)

    def delete_booking(self, event: EventDB, user: UserDB) -> None:
        """Unregister the user from the event."""
        booking = (
            self.db.query(BookingDB)
            .filter_by(event_id=event.id, user_email=user.email)
            .first()
        )
        if booking:
            self.db.delete(booking)

    def get_event_participants(self, event: EventDB) -> list[str]:
        """Get the list of event's participants."""
        bookings = self.db.query(BookingDB).filter_by(event_id=event.id).all()
        return [booking.user_email for booking in bookings]

    def get_all_bookings(self) -> list[BookingDB]:
        """Get the list of all bookings for all the events."""
        return self.db.query(BookingDB).all()
