from unittest.mock import MagicMock, patch

import pytest

import src.app.exceptions.bookings as booking_errors
from src.app.logic.bookings import (
    assert_seats_available,
    create_booking,
    delete_booking,
    get_all_bookings,
    get_event_participants,
)
from src.app.repo.bookings import Booking
from src.app.repo.events import Event
from src.app.repo.users import User


def create_mock_user(**kwargs: object) -> MagicMock:
    """Create a mock User object for testing."""
    mock_user = MagicMock(spec=User)
    for key, value in kwargs.items():
        setattr(mock_user, key, value)
    return mock_user


def create_mock_event(**kwargs: object) -> MagicMock:
    """Create a mock Event object for testing."""
    mock_event = MagicMock(spec=Event)
    for key, value in kwargs.items():
        setattr(mock_event, key, value)
    return mock_event


def create_mock_booking(**kwargs: object) -> MagicMock:
    """Create a mock Booking object for testing."""
    mock_booking = MagicMock(spec=Booking)
    for key, value in kwargs.items():
        setattr(mock_booking, key, value)
    return mock_booking


def test__create_booking__new_booking() -> None:
    """Check new booking is created when user is not registered."""
    mock_db = MagicMock()
    mock_db.query().filter_by().first.return_value = None

    event = create_mock_event(id=1)
    user = create_mock_user(email="g.popov@inno.ru")

    with patch("src.app.logic.bookings.Booking") as mock_booking_cls:
        mock_booking = create_mock_booking(event_id=event.id, user_email=user.email)
        mock_booking_cls.return_value = mock_booking
        create_booking(event, user, mock_db)

    mock_db.add.assert_called_once_with(mock_booking)


def test__create_booking__already_exists() -> None:
    """Check no new booking is created when user is already registered."""
    mock_db = MagicMock()
    existing_booking = create_mock_booking()
    mock_db.query().filter_by().first.return_value = existing_booking

    event = create_mock_event(id=1)
    user = create_mock_user(email="g.popov@inno.ru")

    create_booking(event, user, mock_db)

    mock_db.add.assert_not_called()


def test__assert_seats_available__unlimited_seats() -> None:
    """Check no error when event has no participant limit."""
    mock_db = MagicMock()
    event = create_mock_event(id=1, max_participants=None)

    assert_seats_available(event, mock_db)


def test__assert_seats_available__seats_available() -> None:
    """Check no error when there are available seats."""
    mock_db = MagicMock()
    event = create_mock_event(id=1, max_participants=10)
    mock_db.query().filter_by().count.return_value = 5
    assert_seats_available(event, mock_db)


def test__assert_seats_available__event_full() -> None:
    """Check EventFullError is raised when event is full."""
    mock_db = MagicMock()
    event = create_mock_event(id=1, max_participants=10)
    mock_db.query().filter_by().count.return_value = 10

    with pytest.raises(booking_errors.EventFullError):
        assert_seats_available(event, mock_db)


def test__delete_booking__exists() -> None:
    """Check booking is deleted when it exists."""
    mock_db = MagicMock()
    booking = create_mock_booking()
    mock_db.query().filter_by().first.return_value = booking

    event = create_mock_event(id=1)
    user = create_mock_user(email="g.popov@inno.ru")

    delete_booking(event, user, mock_db)

    mock_db.delete.assert_called_once_with(booking)


def test__delete_booking__not_exists() -> None:
    """Check no deletion when booking doesn't exist."""
    mock_db = MagicMock()
    mock_db.query().filter_by().first.return_value = None

    event = create_mock_event(id=1)
    user = create_mock_user(email="g.popov@inno.ru")

    delete_booking(event, user, mock_db)

    mock_db.delete.assert_not_called()


def test__get_event_participants() -> None:
    """Check list of participant emails is returned."""
    mock_db = MagicMock()
    event = create_mock_event(id=1)

    mock_bookings = [
        create_mock_booking(user_email="g.popov@inno.ru"),
        create_mock_booking(user_email="a.popov@inno.ru"),
        create_mock_booking(user_email="t.farizunov@inno.ru"),
    ]
    mock_db.query().filter_by().all.return_value = mock_bookings

    participants = get_event_participants(event, mock_db)

    expected_emails = ["g.popov@inno.ru", "a.popov@inno.ru", "t.farizunov@inno.ru"]
    assert participants == expected_emails


def test__get_event_participants__empty() -> None:
    """Check empty list is returned when no participants."""
    mock_db = MagicMock()
    event = create_mock_event(id=1)
    mock_db.query().filter_by().all.return_value = []

    participants = get_event_participants(event, mock_db)

    assert participants == []


def test__get_all_bookings() -> None:
    """Check all bookings are returned."""
    mock_db = MagicMock()
    mock_bookings = [
        create_mock_booking(id=1),
        create_mock_booking(id=2),
        create_mock_booking(id=3),
    ]
    mock_db.query().all.return_value = mock_bookings

    bookings = get_all_bookings(mock_db)

    mock_db.query().all.assert_called_once()
    assert bookings == mock_bookings


def test__get_all_bookings__empty() -> None:
    """Check empty list is returned when no bookings."""
    mock_db = MagicMock()
    mock_db.query().all.return_value = []

    bookings = get_all_bookings(mock_db)

    mock_db.query().all.assert_called_once()
    assert bookings == []
