from datetime import UTC, datetime
from random import randint
from unittest.mock import MagicMock, patch

import pytest

import src.app.domain.exceptions.events as event_errors
import src.app.domain.exceptions.users as user_errors
from src.app.db import get_db
from src.app.infrastructure.adapters.events_adapter import EventsAdapter
from src.app.infrastructure.adapters.users_adapter import UsersAdapter
from src.app.infrastructure.db_models.events import EventDB
from src.app.infrastructure.db_models.users import UserDB
from src.app.main import app
from src.app.services.events import EventService
from src.app.services.models.common import Success
from src.app.services.models.events import EventBase, EventID, EventInfo


def create_mock_event_base(**kwargs: object) -> MagicMock:
    """Create a mock EventBase object for testing."""
    mock_event_base = MagicMock(spec=EventBase)
    for key, value in kwargs.items():
        setattr(mock_event_base, key, value)
    return mock_event_base


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


class TestEventService:
    """Test class for EventService."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.mock_db = MagicMock()
        app.dependency_overrides[get_db] = lambda: self.mock_db
        self.event_service = EventService(self.mock_db)

    def test__create_event__success(self) -> None:
        """Test successful event creation."""
        mock_user = create_mock_user(email="g.popov@inno.ru")
        mock_event = create_mock_event(id=1)
        event_base = EventBase(
            title="Midterm",
            description="Midterm Assignment",
            date=datetime(2024, 1, 1, 12, 0, tzinfo=UTC),
            is_offline=True,
            location="Room 108",
            max_participants=randint(10, 50),
        )

        with (
            patch.object(
                UsersAdapter, "get_user", return_value=mock_user
            ) as mock_create_user,
            patch.object(
                EventsAdapter, "create_event", return_value=mock_event
            ) as mock_create_event,
        ):
            result = self.event_service.create_event(event_base, "g.popov@inno.ru")

        mock_create_user.assert_called_once_with("g.popov@inno.ru")
        mock_create_event.assert_called_once_with(event_base, "g.popov@inno.ru")
        self.mock_db.commit.assert_called_once()
        assert isinstance(result, EventID)
        assert result.id == 1

    def test__create_event__random_user(self) -> None:
        """Test event creation from a random user."""
        event_base = EventBase(
            title="Midterm",
            description="Midterm Assignment",
            date=datetime(2024, 1, 1, 12, 0, tzinfo=UTC),
            is_offline=True,
            location="Room 108",
            max_participants=randint(10, 50),
        )

        with (
            patch.object(
                UsersAdapter,
                "get_user",
                side_effect=user_errors.UserNotFoundError("g.popov@inno.ru"),
            ) as mock_create_user,
            patch.object(EventsAdapter, "create_event") as mock_create_event,
        ):
            with pytest.raises(user_errors.UserNotFoundError):
                self.event_service.create_event(event_base, "g.popov@inno.ru")

        mock_create_user.assert_called_once_with("g.popov@inno.ru")
        mock_create_event.assert_not_called()
        self.mock_db.commit.assert_not_called()

    def test__delete_event__success(self) -> None:
        """Test successful event deletion."""
        mock_user = create_mock_user(email="g.popov@inno.ru")
        mock_event = create_mock_event(id=1)

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
            patch.object(EventsAdapter, "delete_event") as mock_delete_event,
        ):
            result = self.event_service.delete_event(1, "g.popov@inno.ru")

        mock_get_user.assert_called_once_with("g.popov@inno.ru")
        mock_get_event.assert_called_once_with(1)
        mock_assert_organizer.assert_called_once_with(mock_event, mock_user)
        mock_delete_event.assert_called_once_with(mock_event)
        self.mock_db.commit.assert_called_once()
        assert isinstance(result, Success)

    def test__delete_event__invalid_user(self) -> None:
        """Attempt to delete event from random email."""
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
            patch.object(EventsAdapter, "delete_event") as mock_delete_event,
        ):
            with pytest.raises(user_errors.UserNotFoundError):
                self.event_service.delete_event(1, "g.popov@inno.ru")

        mock_get_user.assert_called_once_with("g.popov@inno.ru")
        mock_get_event.assert_not_called()
        mock_assert_organizer.assert_not_called()
        mock_delete_event.assert_not_called()
        self.mock_db.commit.assert_not_called()

    def test__delete_event__no_event(self) -> None:
        """Attempt to delete event that does not exist."""
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
            patch.object(EventsAdapter, "delete_event") as mock_delete_event,
        ):
            with pytest.raises(event_errors.EventNotFoundError):
                self.event_service.delete_event(1, "g.popov@inno.ru")

        mock_get_user.assert_called_once_with("g.popov@inno.ru")
        mock_get_event.assert_called_once_with(1)
        mock_assert_organizer.assert_not_called()
        mock_delete_event.assert_not_called()
        self.mock_db.commit.assert_not_called()

    def test__delete_event__not_organizer(self) -> None:
        """Attempt to delete event by non-organizer."""
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
            patch.object(EventsAdapter, "delete_event") as mock_delete_event,
        ):
            with pytest.raises(event_errors.OrginizatorRoleRequiredError):
                self.event_service.delete_event(1, "g.popov@inno.ru")

        mock_get_user.assert_called_once_with("g.popov@inno.ru")
        mock_get_event.assert_called_once_with(1)
        mock_assert_organizer.assert_called_once_with(mock_event, mock_user)
        mock_delete_event.assert_not_called()
        self.mock_db.commit.assert_not_called()

    def test__get_events_list(self) -> None:
        """Test to get the list of events."""
        mock_events = [
            create_mock_event(
                id=1,
                title="Test",
                description="Test",
                date=datetime(2024, 1, 1, 12, 0, tzinfo=UTC),
                is_offline=True,
                location="Innopolis",
                organizer_email="g.popov@inno.ru",
                max_participants=60,
            ),
            create_mock_event(
                id=2,
                title="Test",
                description="Test",
                date=datetime(2024, 1, 1, 12, 0, tzinfo=UTC),
                is_offline=True,
                location="Innopolis",
                organizer_email="g.popov@inno.ru",
                max_participants=60,
            ),
        ]

        with patch.object(
            EventsAdapter, "get_events_list", return_value=mock_events
        ) as mock_get_events_list:
            result = self.event_service.get_events_list()

        mock_get_events_list.assert_called_once_with()
        assert isinstance(result, list)
        assert all(isinstance(event, EventInfo) for event in result)
        assert len(result) == len(mock_events)

        assert result[0].id == 1
        assert result[0].title == "Test"
        assert result[0].description == "Test"
        assert result[0].date == datetime(2024, 1, 1, 12, 0, tzinfo=UTC)
        assert result[0].is_offline == True
        assert result[0].location == "Innopolis"
        assert result[0].organizer_email == "g.popov@inno.ru"
        assert result[0].max_participants == 60

        assert result[1].id == 2
        assert result[1].title == "Test"
        assert result[1].description == "Test"
        assert result[1].date == datetime(2024, 1, 1, 12, 0, tzinfo=UTC)
        assert result[1].is_offline == True
        assert result[1].location == "Innopolis"
        assert result[1].organizer_email == "g.popov@inno.ru"
        assert result[1].max_participants == 60

    def test__get_event_info__success(self) -> None:
        """Test to get the event info."""
        mock_event = create_mock_event(
            id=1,
            title="Test",
            description="Test",
            date=datetime(2024, 1, 1, 12, 0, tzinfo=UTC),
            is_offline=True,
            location="Innopolis",
            organizer_email="g.popov@inno.ru",
            max_participants=60,
        )

        with patch.object(
            EventsAdapter, "get_event", return_value=mock_event
        ) as mock_get_event:
            result = self.event_service.get_event_info(1)

        mock_get_event.assert_called_once_with(1)
        assert isinstance(result, EventInfo)
        assert result.id == 1
        assert result.title == "Test"
        assert result.description == "Test"
        assert result.date == datetime(2024, 1, 1, 12, 0, tzinfo=UTC)
        assert result.is_offline == True
        assert result.location == "Innopolis"
        assert result.organizer_email == "g.popov@inno.ru"
        assert result.max_participants == 60

    def test__get_event_info__no_event(self) -> None:
        """Test to get the event info."""
        with (
            patch.object(
                EventsAdapter,
                "get_event",
                side_effect=event_errors.EventNotFoundError(1),
            ) as mock_get_event,
            pytest.raises(event_errors.EventNotFoundError),
        ):
            self.event_service.get_event_info(1)

        mock_get_event.assert_called_once_with(1)
