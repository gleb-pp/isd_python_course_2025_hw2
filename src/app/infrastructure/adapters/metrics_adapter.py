from sqlalchemy.orm import Session

from src.app.infrastructure.db_models.bookings import BookingDB
from src.app.infrastructure.db_models.events import EventDB
from src.app.infrastructure.db_models.users import UserDB


class MetricsAdapter:
    """Adapter for working with metrics."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_event_registrations(self, event: EventDB) -> int:
        """Get the number of bookings for the event."""
        return self.db.query(BookingDB).filter_by(event_id=event.id).count()

    def get_user_bookings(self, user: UserDB) -> float:
        """Get the number of bookings for the provided user."""
        return self.db.query(BookingDB).filter_by(user_email=user.email).count()
