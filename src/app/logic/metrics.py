from sqlalchemy.orm import Session

from src.app.repo.bookings import Booking
from src.app.repo.events import Event
from src.app.repo.users import User


def get_event_registrations(event: Event, db: Session) -> int:
    """Get the number of bookings for the event."""
    return db.query(Booking).filter_by(event_id=event.id).count()


def get_user_bookings(user: User, db: Session) -> float:
    """Get the number of bookings for the provided user."""
    return db.query(Booking).filter_by(user_email=user.email).count()
