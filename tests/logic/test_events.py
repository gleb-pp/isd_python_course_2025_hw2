from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest

import src.app.domain.exceptions.events as event_errors
from src.app.infrastructure.db_models.events import EventDB
from src.app.infrastructure.db_models.users import UserDB
from src.app.infrastructure.adapters.events_adapter import EventsAdapter
from src.app.services.models.events import EventBase


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


class TestEventsAdapter:
    """Test class for EventsAdapter."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.mock_db = MagicMock()
        self.events_adapter = EventsAdapter(self.mock_db)

    def test__create_event__valid(self) -> None:
        """Check the valid event creation."""
        event_base = EventBase(
            title="Midterm",
            description="Midterm Assignment",
            date=datetime(2024, 1, 1, 12, 0, tzinfo=UTC),
            is_offline=True,
            location="Room 108",
            max_participants=60,
        )

        mock_event = create_mock_event(
            id=1,
            title=event_base.title,
            description=event_base.description,
            date=event_base.date,
            is_offline=event_base.is_offline,
            location=event_base.location,
            organizer_email="g.popov@inno.ru",
            max_participants=event_base.max_participants,
        )

        with patch("src.app.infrastructure.adapters.events_adapter.EventDB", return_value=mock_event):
            event = self.events_adapter.create_event(event_base, "g.popov@inno.ru")

        self.mock_db.add.assert_called_once_with(mock_event)
        self.mock_db.flush.assert_called_once()
        assert event == mock_event


    def test__get_event__exists(self) -> None:
        """Check existing event is returned."""
        event_id = 1
        mock_event = create_mock_event(id=event_id, title="Midterm")
        self.mock_db.query().filter_by().first.return_value = mock_event

        event = self.events_adapter.get_event(event_id)
        assert event == mock_event


    def test__get_event__not_found(self) -> None:
        """Check that EventNotFoundError is raised if event missing."""
        event_id = 1
        self.mock_db.query().filter_by().first.return_value = None

        with pytest.raises(event_errors.EventNotFoundError):
            self.events_adapter.get_event(event_id)


    def test__assert_user_is_organizer__success(self) -> None:
        """Check organizer user passes."""
        event = create_mock_event(id=1, organizer_email="g.popov@inno.ru")
        user = create_mock_user(email="g.popov@inno.ru")
        self.events_adapter.assert_user_is_organizer(event, user)


    def test__assert_user_is_organizer__fail(self) -> None:
        """Check non-organizer user raises OrginizatorRoleRequiredError."""
        event = create_mock_event(id=1, organizer_email="g.popov@inno.ru")
        user = create_mock_user(email="a.popov@inno.ru")

        with pytest.raises(event_errors.OrginizatorRoleRequiredError):
            self.events_adapter.assert_user_is_organizer(event, user)


    def test__delete_event__called(self) -> None:
        """Check delete_event calls db.delete."""
        event = create_mock_event(id=1, title="Midterm")

        self.events_adapter.delete_event(event)
        self.mock_db.delete.assert_called_once_with(event)


    def test__get_events_list(self) -> None:
        """Check all events are returned."""
        mock_events = [
            create_mock_event(id=1, title="EventDB 1"),
            create_mock_event(id=2, title="EventDB 2"),
        ]
        self.mock_db.query().all.return_value = mock_events
        events = self.events_adapter.get_events_list()
        self.mock_db.query().all.assert_called_once()
        assert events == mock_events
