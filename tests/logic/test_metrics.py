from unittest.mock import MagicMock

import pytest

from src.app.infrastructure.db_models.events import EventDB
from src.app.infrastructure.db_models.users import UserDB
from src.app.logic.metrics import get_event_registrations, get_user_bookings


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


@pytest.mark.parametrize(("reg_count"), [(5), (0)])
def test__get_event_registrations(reg_count: int) -> None:
    """Check correct count is returned for event with registrations."""
    mock_db = MagicMock()
    event = create_mock_event(id=1)

    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter_by.return_value
    mock_filter.count.return_value = reg_count

    registrations_count = get_event_registrations(event, mock_db)

    mock_db.query().filter_by.assert_called_once_with(event_id=event.id)
    assert registrations_count == reg_count


@pytest.mark.parametrize(("book_count"), [(5), (0)])
def test__get_user_bookings__with_bookings(book_count: int) -> None:
    """Check correct count is returned for user with bookings."""
    mock_db = MagicMock()
    user = create_mock_user(email="g.popov@inno.ru")

    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter_by.return_value
    mock_filter.count.return_value = book_count

    bookings_count = get_user_bookings(user, mock_db)

    mock_db.query().filter_by.assert_called_once_with(user_email=user.email)
    assert bookings_count == book_count
