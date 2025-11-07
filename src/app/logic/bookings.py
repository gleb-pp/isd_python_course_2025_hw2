from sqlalchemy.orm import Session

import src.app.domain.exceptions.bookings as booking_errors
from src.app.infrastructure.db_models.bookings import BookingDB
from src.app.infrastructure.db_models.events import EventDB
from src.app.infrastructure.db_models.users import UserDB


def create_booking(event: EventDB, user: UserDB, db: Session) -> None:
    """Register the user with provided email to the event with provided event_id."""
    # check if user is already registered
    existing_booking = (
        db.query(BookingDB).filter_by(event_id=event.id, user_email=user.email).first()
    )
    if existing_booking is not None:
        return

    # create booking
    new_booking = BookingDB(event_id=event.id, user_email=user.email)
    db.add(new_booking)


def assert_seats_available(event: EventDB, db: Session) -> None:
    """Check if there are any available seats left in the event."""
    if event.max_participants is not None:
        current_participants = db.query(BookingDB).filter_by(event_id=event.id).count()
        if current_participants >= event.max_participants:
            raise booking_errors.EventFullError(event.id)


def delete_booking(event: EventDB, user: UserDB, db: Session) -> None:
    """Unregister the user with provided email from the event with provided event_id."""
    # check if booking exists
    booking = (
        db.query(BookingDB).filter_by(event_id=event.id, user_email=user.email).first()
    )
    if booking is not None:
        db.delete(booking)


def get_event_participants(event: EventDB, db: Session) -> list[str]:
    """Get the list of user emails registered for the event with provided event_id."""
    bookings = db.query(BookingDB).filter_by(event_id=event.id).all()
    return [booking.user_email for booking in bookings]


def get_all_bookings(db: Session) -> list[BookingDB]:
    """Get the list of all bookings for all the events."""
    return db.query(BookingDB).all()
