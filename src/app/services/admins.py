from sqlalchemy.orm import Session

from src.app.infrastructure.adapters.bookings_adapter import BookingsAdapter
from src.app.infrastructure.adapters.events_adapter import EventsAdapter
from src.app.infrastructure.adapters.users_adapter import UsersAdapter
from src.app.services.models.bookings import Booking, EventParticipants
from src.app.services.models.common import Success
from src.app.services.models.users import User, UserCreate


class AdminService:
    """Service layer for the Admins."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.bookings = BookingsAdapter(db)
        self.events = EventsAdapter(db)
        self.users = UsersAdapter(db)

    def get_all_users(self, admin_email: str) -> list[User]:
        """Get all the system users."""
        user = self.users.get_user(admin_email)
        self.users.assert_user_is_admin(user)
        users = self.users.get_all_users()
        return [User.model_validate(user) for user in users]

    def create_user(self, new_user: UserCreate, admin_email: str) -> Success:
        """Create a new user in the system."""
        user = self.users.get_user(admin_email)
        self.users.assert_user_is_admin(user)
        self.users.validate_user_email(new_user.email)
        self.users.validate_user_name(new_user.name)
        self.users.validate_password_lenght(new_user.password)
        self.users.create_user(new_user.email, new_user.name, new_user.password)
        self.db.commit()
        return Success(success=True)

    def delete_user(self, deleted_user_email: str, admin_email: str) -> Success:
        """Delete the existing user from the system."""
        user = self.users.get_user(admin_email)
        self.users.assert_user_is_admin(user)
        deleted_user = self.users.get_user(deleted_user_email)
        self.users.delete_user(deleted_user)
        self.db.commit()
        return Success(success=True)

    def delete_event(self, event_id: int, admin_email: str) -> Success:
        """Delete the existing event from the system."""
        user = self.users.get_user(admin_email)
        self.users.assert_user_is_admin(user)
        event = self.events.get_event(event_id)
        self.events.delete_event(event)
        self.db.commit()
        return Success(success=True)

    def create_user_booking(
        self, event_id: int, guest_email: str, admin_email: str
    ) -> Success:
        """Create a booking for user."""
        user = self.users.get_user(admin_email)
        self.users.assert_user_is_admin(user)
        guest = self.users.get_user(guest_email)
        event = self.events.get_event(event_id)
        self.bookings.assert_seats_available(event)
        self.bookings.create_booking(event, guest)
        self.db.commit()
        return Success(success=True)

    def delete_user_booking(
        self, event_id: int, guest_email: str, admin_email: str
    ) -> Success:
        """Create a user's booking."""
        user = self.users.get_user(admin_email)
        self.users.assert_user_is_admin(user)
        guest = self.users.get_user(guest_email)
        event = self.events.get_event(event_id)
        self.bookings.delete_booking(event, guest)
        self.db.commit()
        return Success(success=True)

    def get_event_participants(
        self, event_id: int, admin_email: str
    ) -> EventParticipants:
        """Get the list of event's guests."""
        user = self.users.get_user(admin_email)
        self.users.assert_user_is_admin(user)
        event = self.events.get_event(event_id)
        participants_emails = self.bookings.get_event_participants(event)
        return EventParticipants(participants_emails=participants_emails)

    def get_bookings(self, admin_email: str) -> list[Booking]:
        """Get all the bookings."""
        user = self.users.get_user(admin_email)
        self.users.assert_user_is_admin(user)
        bookings = self.bookings.get_all_bookings()
        return [Booking.model_validate(booking) for booking in bookings]
