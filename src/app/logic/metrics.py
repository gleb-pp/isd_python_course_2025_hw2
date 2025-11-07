from sqlalchemy.orm import Session

from src.app.infrastructure.db_models.bookings import BookingDB
from src.app.infrastructure.db_models.events import EventDB
from src.app.infrastructure.db_models.users import UserDB


def get_event_registrations(event: EventDB, db: Session) -> int:
    """Get the number of bookings for the event."""
    return db.query(BookingDB).filter_by(event_id=event.id).count()


def get_user_bookings(user: UserDB, db: Session) -> float:
    """Get the number of bookings for the provided user."""
    return db.query(BookingDB).filter_by(user_email=user.email).count()
