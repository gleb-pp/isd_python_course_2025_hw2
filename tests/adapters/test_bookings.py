from unittest.mock import MagicMock, patch

import pytest

import src.app.domain.exceptions.bookings as booking_errors
from src.app.infrastructure.adapters.bookings_adapter import BookingsAdapter
from src.app.infrastructure.db_models.bookings import BookingDB
from src.app.infrastructure.db_models.events import EventDB
from src.app.infrastructure.db_models.users import UserDB


def create_mock_user(**kwargs: object) -> MagicMock:
    """Create a mock UserDB object for testing."""
    mock_user = MagicMock(spec=UserDB)
    for key, value in kwargs.items():
        setattr(mock_user, key, value)
    return mock_user


def create_mock_event(**kwargs: object) -> MagicMock:
    """Create a mock EventDB object for testing."""
    mock_event = MagicMock(spec=EventDB)
    for key, value in kwargs.items():
        setattr(mock_event, key, value)
    return mock_event


def create_mock_booking(**kwargs: object) -> MagicMock:
    """Create a mock BookingDB object for testing."""
    mock_booking = MagicMock(spec=BookingDB)
    for key, value in kwargs.items():
        setattr(mock_booking, key, value)
    return mock_booking


class TestBookingsAdapter:
    """Test class for BookingsAdapter."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.mock_db = MagicMock()
        self.bookings_adapter = BookingsAdapter(self.mock_db)

    def test__create_booking__new_booking(self) -> None:
        """Check new booking is created when user is not registered."""
        self.mock_db.query().filter_by().first.return_value = None

        event = create_mock_event(id=1)
        user = create_mock_user(email="g.popov@inno.ru")

        with patch(
            "src.app.infrastructure.adapters.bookings_adapter.BookingDB"
        ) as mock_booking_cls:
            mock_booking = create_mock_booking(event_id=event.id, user_email=user.email)
            mock_booking_cls.return_value = mock_booking
            self.bookings_adapter.create_booking(event, user)

        self.mock_db.add.assert_called_once_with(mock_booking)

    def test__create_booking__already_exists(self) -> None:
        """Check no new booking is created when user is already registered."""
        existing_booking = create_mock_booking()
        self.mock_db.query().filter_by().first.return_value = existing_booking

        event = create_mock_event(id=1)
        user = create_mock_user(email="g.popov@inno.ru")

        self.bookings_adapter.create_booking(event, user)

        self.mock_db.add.assert_not_called()

    def test__assert_seats_available__unlimited_seats(self) -> None:
        """Check no error when event has no participant limit."""
        event = create_mock_event(id=1, max_participants=None)

        self.bookings_adapter.assert_seats_available(event)

    def test__assert_seats_available__seats_available(self) -> None:
        """Check no error when there are available seats."""
        event = create_mock_event(id=1, max_participants=10)
        self.mock_db.query().filter_by().count.return_value = 5
        self.bookings_adapter.assert_seats_available(event)

    def test__assert_seats_available__event_full(self) -> None:
        """Check EventFullError is raised when event is full."""
        event = create_mock_event(id=1, max_participants=10)
        self.mock_db.query().filter_by().count.return_value = 10

        with pytest.raises(booking_errors.EventFullError):
            self.bookings_adapter.assert_seats_available(event)

    def test__delete_booking__exists(self) -> None:
        """Check booking is deleted when it exists."""
        booking = create_mock_booking()
        self.mock_db.query().filter_by().first.return_value = booking

        event = create_mock_event(id=1)
        user = create_mock_user(email="g.popov@inno.ru")

        self.bookings_adapter.delete_booking(event, user)

        self.mock_db.delete.assert_called_once_with(booking)

    def test__delete_booking__not_exists(self) -> None:
        """Check no deletion when booking doesn't exist."""
        self.mock_db.query().filter_by().first.return_value = None

        event = create_mock_event(id=1)
        user = create_mock_user(email="g.popov@inno.ru")

        self.bookings_adapter.delete_booking(event, user)

        self.mock_db.delete.assert_not_called()

    def test__get_event_participants(self) -> None:
        """Check list of participant emails is returned."""
        event = create_mock_event(id=1)

        mock_bookings = [
            create_mock_booking(user_email="g.popov@inno.ru"),
            create_mock_booking(user_email="a.popov@inno.ru"),
            create_mock_booking(user_email="t.farizunov@inno.ru"),
        ]
        self.mock_db.query().filter_by().all.return_value = mock_bookings

        participants = self.bookings_adapter.get_event_participants(event)

        expected_emails = ["g.popov@inno.ru", "a.popov@inno.ru", "t.farizunov@inno.ru"]
        assert participants == expected_emails

    def test__get_event_participants__empty(self) -> None:
        """Check empty list is returned when no participants."""
        event = create_mock_event(id=1)
        self.mock_db.query().filter_by().all.return_value = []

        participants = self.bookings_adapter.get_event_participants(event)

        assert participants == []

    def test__get_all_bookings(self) -> None:
        """Check all bookings are returned."""
        mock_bookings = [
            create_mock_booking(id=1),
            create_mock_booking(id=2),
            create_mock_booking(id=3),
        ]
        self.mock_db.query().all.return_value = mock_bookings

        bookings = self.bookings_adapter.get_all_bookings()

        self.mock_db.query().all.assert_called_once()
        assert bookings == mock_bookings

    def test__get_all_bookings__empty(self) -> None:
        """Check empty list is returned when no bookings."""
        self.mock_db.query().all.return_value = []

        bookings = self.bookings_adapter.get_all_bookings()

        self.mock_db.query().all.assert_called_once()
        assert bookings == []
