from unittest.mock import MagicMock

import pytest

from src.app.infrastructure.adapters.metrics_adapter import MetricsAdapter
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


class TestMetricsAdapter:
    """Test class for MetricsAdapter."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.mock_db = MagicMock()
        self.metrics_adapter = MetricsAdapter(self.mock_db)

    @pytest.mark.parametrize(("reg_count"), [(5), (0)])
    def test__get_event_registrations(self, reg_count: int) -> None:
        """Check correct count is returned for event with registrations."""
        event = create_mock_event(id=1)

        mock_query = self.mock_db.query.return_value
        mock_filter = mock_query.filter_by.return_value
        mock_filter.count.return_value = reg_count

        registrations_count = self.metrics_adapter.get_event_registrations(event)

        self.mock_db.query().filter_by.assert_called_once_with(event_id=event.id)
        assert registrations_count == reg_count

    @pytest.mark.parametrize(("book_count"), [(5), (0)])
    def test__get_user_bookings__with_bookings(self, book_count: int) -> None:
        """Check correct count is returned for user with bookings."""
        user = create_mock_user(email="g.popov@inno.ru")

        mock_query = self.mock_db.query.return_value
        mock_filter = mock_query.filter_by.return_value
        mock_filter.count.return_value = book_count

        bookings_count = self.metrics_adapter.get_user_bookings(user)

        self.mock_db.query().filter_by.assert_called_once_with(user_email=user.email)
        assert bookings_count == book_count
