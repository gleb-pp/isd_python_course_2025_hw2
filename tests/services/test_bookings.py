from unittest.mock import MagicMock, patch

import src.app.domain.exceptions.bookings as booking_errors
import src.app.domain.exceptions.events as event_errors
import src.app.domain.exceptions.users as user_errors
from src.app.auth import get_current_user
from src.app.db import get_db
from src.app.infrastructure.db_models.events import EventDB
from src.app.infrastructure.db_models.users import UserDB
from src.app.main import app
from src.app.services.bookings import BookingService
from src.app.infrastructure.adapters.events_adapter import EventsAdapter
from src.app.infrastructure.adapters.users_adapter import UsersAdapter
from src.app.infrastructure.adapters.bookings_adapter import BookingsAdapter
from src.app.services.models.common import Success
from src.app.services.models.bookings import EventParticipants
import pytest


def create_mock_event(**kwargs: object) -> MagicMock:
    """Create a mock EventDB object for testing."""
    mock_event = MagicMock(spec=EventDB)
    for key, value in kwargs.items():
        setattr(mock_event, key, value)
    return mock_event


def create_mock_user(**kwargs: object) -> MagicMock:
    """Create a mock UserDB object for testing."""
    mock_user = MagicMock(spec=UserDB)
    for key, value in kwargs.items():
        setattr(mock_user, key, value)
    return mock_user


class TestBookingService:
    """Test class for BookingService."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.mock_db = MagicMock()
        app.dependency_overrides[get_db] = lambda: self.mock_db
        self.booking_service = BookingService(self.mock_db)

    def test__create_booking__success(self) -> None:
        """Test successful booking creation."""
        app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

        mock_user = create_mock_user()
        mock_event = create_mock_event()

        with (
            patch.object(
                UsersAdapter, "get_user", return_value=mock_user
            ) as mock_get_user,
            patch.object(
                EventsAdapter,
                "get_event",
                return_value=mock_event,
            ) as mock_get_event,
            patch.object(
                BookingsAdapter, "assert_seats_available"
            ) as mock_assert_seats_available,
            patch.object(BookingsAdapter, "create_booking") as mock_create_booking,
        ):
            result = self.booking_service.create_booking(1, "g.popov@inno.ru")

        mock_get_user.assert_called_once_with("g.popov@inno.ru")
        mock_get_event.assert_called_once_with(1)
        mock_assert_seats_available.assert_called_once_with(mock_event)
        mock_create_booking.assert_called_once_with(mock_event, mock_user)
        self.mock_db.commit.assert_called_once()
        assert isinstance(result, Success)

    def test__create_booking__random_user(self) -> None:
        """Attempt to create a booking from random email."""
        app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

        with (
            patch.object(
                UsersAdapter,
                "get_user",
                side_effect=user_errors.UserNotFoundError("g.popov@inno.ru"),
            ) as mock_get_user,
            patch.object(EventsAdapter, "get_event") as mock_get_event,
            patch.object(
                BookingsAdapter, "assert_seats_available"
            ) as mock_assert_seats_available,
            patch.object(BookingsAdapter, "create_booking") as mock_create_booking,
        ):
            with pytest.raises(user_errors.UserNotFoundError):
                self.booking_service.create_booking(1, "g.popov@inno.ru")

        mock_get_user.assert_called_once_with("g.popov@inno.ru")
        mock_get_event.assert_not_called()
        mock_assert_seats_available.assert_not_called()
        mock_create_booking.assert_not_called()
        self.mock_db.commit.assert_not_called()

    def test__create_booking__no_event(self) -> None:
        """Attempt to create a booking for a non-existing event."""
        app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

        with (
            patch.object(UsersAdapter, "get_user") as mock_get_user,
            patch.object(
                EventsAdapter,
                "get_event",
                side_effect=event_errors.EventNotFoundError(1),
            ) as mock_get_event,
            patch.object(
                BookingsAdapter, "assert_seats_available"
            ) as mock_assert_seats_available,
            patch.object(BookingsAdapter, "create_booking") as mock_create_booking,
        ):
            with pytest.raises(event_errors.EventNotFoundError):
                self.booking_service.create_booking(1, "g.popov@inno.ru")

        mock_get_user.assert_called_once_with("g.popov@inno.ru")
        mock_get_event.assert_called_once_with(1)
        mock_assert_seats_available.assert_not_called()
        mock_create_booking.assert_not_called()
        self.mock_db.commit.assert_not_called()

    def test__create_booking__no_seats(self) -> None:
        """Attempt to create a booking for a full event."""
        app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

        mock_event = create_mock_event()

        with (
            patch.object(UsersAdapter, "get_user") as mock_get_user,
            patch.object(
                EventsAdapter,
                "get_event",
                return_value=mock_event,
            ) as mock_get_event,
            patch.object(
                BookingsAdapter,
                "assert_seats_available",
                side_effect=booking_errors.EventFullError(1),
            ) as mock_assert_seats_available,
            patch.object(BookingsAdapter, "create_booking") as mock_create_booking,
        ):
            with pytest.raises(booking_errors.EventFullError):
                self.booking_service.create_booking(1, "g.popov@inno.ru")

        mock_get_user.assert_called_once_with("g.popov@inno.ru")
        mock_get_event.assert_called_once_with(1)
        mock_assert_seats_available.assert_called_once_with(mock_event)
        mock_create_booking.assert_not_called()
        self.mock_db.commit.assert_not_called()

    def test__delete_booking__success(self) -> None:
        """Test successful booking deletion."""
        app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

        mock_user = create_mock_user()
        mock_event = create_mock_event()

        with (
            patch.object(
                UsersAdapter, "get_user", return_value=mock_user
            ) as mock_get_user,
            patch.object(
                EventsAdapter,
                "get_event",
                return_value=mock_event,
            ) as mock_get_event,
            patch.object(BookingsAdapter, "delete_booking") as mock_delete_booking,
        ):
            result = self.booking_service.delete_booking(1, "g.popov@inno.ru")

        mock_get_user.assert_called_once_with("g.popov@inno.ru")
        mock_get_event.assert_called_once_with(1)
        mock_delete_booking.assert_called_once_with(mock_event, mock_user)
        self.mock_db.commit.assert_called_once()
        assert isinstance(result, Success)

    def test__delete_booking__random_user(self) -> None:
        """Attempt to delete a booking from random email."""
        app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

        with (
            patch.object(
                UsersAdapter,
                "get_user",
                side_effect=user_errors.UserNotFoundError("g.popov@inno.ru"),
            ) as mock_get_user,
            patch.object(EventsAdapter, "get_event") as mock_get_event,
            patch.object(BookingsAdapter, "delete_booking") as mock_delete_booking,
        ):
            with pytest.raises(user_errors.UserNotFoundError):
                self.booking_service.delete_booking(1, "g.popov@inno.ru")

        mock_get_user.assert_called_once_with("g.popov@inno.ru")
        mock_get_event.assert_not_called()
        mock_delete_booking.assert_not_called()
        self.mock_db.commit.assert_not_called()

    def test__delete_booking__no_event(self) -> None:
        """Attempt to delete a booking for a non-existing event."""
        app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

        with (
            patch.object(UsersAdapter, "get_user") as mock_get_user,
            patch.object(
                EventsAdapter,
                "get_event",
                side_effect=event_errors.EventNotFoundError(1),
            ) as mock_get_event,
            patch.object(BookingsAdapter, "delete_booking") as mock_delete_booking,
        ):
            with pytest.raises(event_errors.EventNotFoundError):
                self.booking_service.delete_booking(1, "g.popov@inno.ru")

        mock_get_user.assert_called_once_with("g.popov@inno.ru")
        mock_get_event.assert_called_once_with(1)
        mock_delete_booking.assert_not_called()
        self.mock_db.commit.assert_not_called()

    def test__get_event_participants__success(self) -> None:
        """Test to get the list of event's participants."""
        app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

        mock_user = create_mock_user()
        mock_event = create_mock_event()
        participants = ["g.popov@inno.ru", "a.popov@inno.ru"]

        with (
            patch.object(
                UsersAdapter, "get_user", return_value=mock_user
            ) as mock_get_user,
            patch.object(
                EventsAdapter,
                "get_event",
                return_value=mock_event,
            ) as mock_get_event,
            patch.object(
                EventsAdapter, "assert_user_is_organizer"
            ) as mock_assert_organizer,
            patch.object(
                BookingsAdapter,
                "get_event_participants",
                return_value=participants,
            ) as mock_get_event_participants,
        ):
            result = self.booking_service.get_event_participants(1, "g.popov@inno.ru")

        mock_get_user.assert_called_once_with("g.popov@inno.ru")
        mock_get_event.assert_called_once_with(1)
        mock_assert_organizer.assert_called_once_with(mock_event, mock_user)
        mock_get_event_participants.assert_called_once_with(mock_event)
        assert isinstance(result, EventParticipants)
        assert result.participants_emails == participants

    def test__get_event_participants__random_user(self) -> None:
        """Attempt to get the list of event's participants from a random email."""
        app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

        with (
            patch.object(
                UsersAdapter,
                "get_user",
                side_effect=user_errors.UserNotFoundError("g.popov@inno.ru"),
            ) as mock_get_user,
            patch.object(EventsAdapter, "get_event") as mock_get_event,
            patch.object(
                EventsAdapter, "assert_user_is_organizer"
            ) as mock_assert_organizer,
            patch.object(
                BookingsAdapter, "get_event_participants"
            ) as mock_get_event_participants,
        ):
            with pytest.raises(user_errors.UserNotFoundError):
                self.booking_service.get_event_participants(1, "g.popov@inno.ru")

        mock_get_user.assert_called_once_with("g.popov@inno.ru")
        mock_get_event.assert_not_called()
        mock_assert_organizer.assert_not_called()
        mock_get_event_participants.assert_not_called()

    def test__get_event_participants__no_event(self) -> None:
        """Test to get the list of event's participants."""
        app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

        with (
            patch.object(UsersAdapter, "get_user") as mock_get_user,
            patch.object(
                EventsAdapter,
                "get_event",
                side_effect=event_errors.EventNotFoundError(1),
            ) as mock_get_event,
            patch.object(
                EventsAdapter, "assert_user_is_organizer"
            ) as mock_assert_organizer,
            patch.object(
                BookingsAdapter, "get_event_participants"
            ) as mock_get_event_participants,
        ):
            with pytest.raises(event_errors.EventNotFoundError):
                self.booking_service.get_event_participants(1, "g.popov@inno.ru")

        mock_get_user.assert_called_once_with("g.popov@inno.ru")
        mock_get_event.assert_called_once_with(1)
        mock_assert_organizer.assert_not_called()
        mock_get_event_participants.assert_not_called()

    def test__get_event_participants__not_oranizatior(self) -> None:
        """Test to get the list of event's participants from non-organizer."""
        app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

        mock_user = create_mock_user()
        mock_event = create_mock_event()

        with (
            patch.object(
                UsersAdapter, "get_user", return_value=mock_user
            ) as mock_get_user,
            patch.object(
                EventsAdapter,
                "get_event",
                return_value=mock_event,
            ) as mock_get_event,
            patch.object(
                EventsAdapter,
                "assert_user_is_organizer",
                side_effect=event_errors.OrginizatorRoleRequiredError(
                    1, "g.popov@inno.ru"
                ),
            ) as mock_assert_organizer,
            patch.object(
                BookingsAdapter, "get_event_participants"
            ) as mock_get_event_participants,
        ):
            with pytest.raises(event_errors.OrginizatorRoleRequiredError):
                self.booking_service.get_event_participants(1, "g.popov@inno.ru")

        mock_get_user.assert_called_once_with("g.popov@inno.ru")
        mock_get_event.assert_called_once_with(1)
        mock_assert_organizer.assert_called_once_with(mock_event, mock_user)
        mock_get_event_participants.assert_not_called()
