from datetime import UTC, datetime
from random import randint
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

import src.app.exceptions.events as event_errors
import src.app.exceptions.users as user_errors
from src.app.auth import get_current_user
from src.app.db import get_db
from src.app.main import app
from src.app.models.events import EventBase
from src.app.repo.events import Event
from src.app.repo.users import User

client = TestClient(app)

HTTP_200_OK = 200
HTTP_409_CONFLICT = 409
HTTP_401_UNAUTHORIZED = 401
HTTP_404_NOT_FOUND = 404
HTTP_403_FORBIDDEN = 403


def create_mock_event_base(**kwargs: object) -> MagicMock:
    """Create a mock EventBase object for testing."""
    mock_event_base = MagicMock(spec=EventBase)
    for key, value in kwargs.items():
        setattr(mock_event_base, key, value)
    return mock_event_base


def create_mock_event(**kwargs: object) -> MagicMock:
    """Create a mock Event object for testing."""
    mock_event = MagicMock(spec=Event)
    for key, value in kwargs.items():
        setattr(mock_event, key, value)
    return mock_event


def create_mock_user(**kwargs: object) -> MagicMock:
    """Create a mock User object for testing."""
    mock_user = MagicMock(spec=User)
    for key, value in kwargs.items():
        setattr(mock_user, key, value)
    return mock_user


def test__create_event() -> None:
    """Test successful event creation."""
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"
    json_data = {
        "title": "Midterm",
        "description": "Midterm Assignment",
        "date": datetime(2024, 1, 1, 12, 0, tzinfo=UTC).isoformat(),
        "is_offline": True,
        "location": "Room 108",
        "max_participants": randint(10, 50),
    }

    with (
        patch(
            "src.app.presentation.events.events_logic.create_event"
        ) as mock_create_event,
    ):
        response = client.post("/events/", json=json_data)

    mock_create_event.assert_called_once()
    called_args, _ = mock_create_event.call_args
    assert called_args[0].title == "Midterm"
    assert called_args[0].description == "Midterm Assignment"
    assert called_args[0].date == datetime(2024, 1, 1, 12, 0, tzinfo=UTC)
    assert called_args[0].is_offline is True
    assert called_args[0].location == "Room 108"
    assert called_args[0].max_participants == json_data["max_participants"]
    assert called_args[1] == "g.popov@inno.ru"
    assert called_args[2] is mock_db

    mock_db.commit.assert_called_once()
    assert response.status_code == HTTP_200_OK
    assert response.json() == {"id": 1}


def test__delete_event__success() -> None:
    """Test successful event deletion."""
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

    mock_user = create_mock_user()
    mock_event = create_mock_event()

    with (
        patch(
            "src.app.presentation.events.user_logic.get_user", return_value=mock_user
        ) as mock_get_user,
        patch(
            "src.app.presentation.events.events_logic.get_event",
            return_value=mock_event,
        ) as mock_get_event,
        patch(
            "src.app.presentation.events.events_logic.assert_user_is_organizer"
        ) as mock_assert_organizer,
        patch(
            "src.app.presentation.events.events_logic.delete_event"
        ) as mock_delete_event,
    ):
        response = client.delete("/events/1")

    mock_get_user.assert_called_once_with("g.popov@inno.ru", mock_db)
    mock_get_event.assert_called_once_with(1, mock_db)
    mock_assert_organizer.assert_called_once_with(mock_event, mock_user)
    mock_delete_event.assert_called_once_with(mock_event, mock_db)
    mock_db.commit.assert_called_once()
    mock_db.rollback.assert_not_called()
    assert response.status_code == HTTP_200_OK
    assert response.json() == {"success": True}


def test__delete_event__invalid_user() -> None:
    """Attempt to delete event from random email."""
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

    with (
        patch(
            "src.app.presentation.events.user_logic.get_user",
            side_effect=user_errors.UserNotFoundError("g.popov@inno.ru"),
        ) as mock_get_user,
        patch("src.app.presentation.events.events_logic.get_event") as mock_get_event,
        patch(
            "src.app.presentation.events.events_logic.assert_user_is_organizer"
        ) as mock_assert_organizer,
        patch(
            "src.app.presentation.events.events_logic.delete_event"
        ) as mock_delete_event,
    ):
        response = client.delete("/events/1")

    mock_get_user.assert_called_once_with("g.popov@inno.ru", mock_db)
    mock_get_event.assert_not_called()
    mock_assert_organizer.assert_not_called()
    mock_delete_event.assert_not_called()
    mock_db.commit.assert_not_called()
    mock_db.rollback.assert_called_once()
    assert response.status_code == HTTP_401_UNAUTHORIZED


def test__delete_event__no_event() -> None:
    """Attempt to delete event that does not exist."""
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

    with (
        patch("src.app.presentation.events.user_logic.get_user") as mock_get_user,
        patch(
            "src.app.presentation.events.events_logic.get_event",
            side_effect=event_errors.EventNotFoundError(1),
        ) as mock_get_event,
        patch(
            "src.app.presentation.events.events_logic.assert_user_is_organizer"
        ) as mock_assert_organizer,
        patch(
            "src.app.presentation.events.events_logic.delete_event"
        ) as mock_delete_event,
    ):
        response = client.delete("/events/1")

    mock_get_user.assert_called_once_with("g.popov@inno.ru", mock_db)
    mock_get_event.assert_called_once_with(1, mock_db)
    mock_assert_organizer.assert_not_called()
    mock_delete_event.assert_not_called()
    mock_db.commit.assert_not_called()
    mock_db.rollback.assert_called_once()
    assert response.status_code == HTTP_404_NOT_FOUND


def test__delete_event__not_organizer() -> None:
    """Attempt to delete event by non-organizer."""
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

    mock_user = create_mock_user()
    mock_event = create_mock_event()

    with (
        patch(
            "src.app.presentation.events.user_logic.get_user", return_value=mock_user
        ) as mock_get_user,
        patch(
            "src.app.presentation.events.events_logic.get_event",
            return_value=mock_event,
        ) as mock_get_event,
        patch(
            "src.app.presentation.events.events_logic.assert_user_is_organizer",
            side_effect=event_errors.OrginizatorRoleRequiredError(1, "g.popov@inno.ru"),
        ) as mock_assert_organizer,
        patch(
            "src.app.presentation.events.events_logic.delete_event"
        ) as mock_delete_event,
    ):
        response = client.delete("/events/1")

    mock_get_user.assert_called_once_with("g.popov@inno.ru", mock_db)
    mock_get_event.assert_called_once_with(1, mock_db)
    mock_assert_organizer.assert_called_once_with(mock_event, mock_user)
    mock_delete_event.assert_not_called()
    mock_db.commit.assert_not_called()
    mock_db.rollback.assert_called_once()
    assert response.status_code == HTTP_403_FORBIDDEN


def test__get_events_list() -> None:
    """Test to get the list of events."""
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

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

    with patch(
        "src.app.presentation.events.events_logic.get_events_list",
        return_value=mock_events,
    ) as mock_get_events_list:
        response = client.get("/events/")

    mock_get_events_list.assert_called_once_with(mock_db)
    assert response.status_code == HTTP_200_OK
    assert response.json() == [
        {
            "id": 1,
            "title": "Test",
            "description": "Test",
            "date": "2024-01-01T12:00:00Z",
            "is_offline": True,
            "location": "Innopolis",
            "organizer_email": "g.popov@inno.ru",
            "max_participants": 60,
        },
        {
            "id": 2,
            "title": "Test",
            "description": "Test",
            "date": "2024-01-01T12:00:00Z",
            "is_offline": True,
            "location": "Innopolis",
            "organizer_email": "g.popov@inno.ru",
            "max_participants": 60,
        },
    ]


def test__get_event_info__success() -> None:
    """Test to get the event info."""
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

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

    with patch(
        "src.app.presentation.events.events_logic.get_event", return_value=mock_event
    ) as mock_get_event:
        response = client.get("/events/1")

    mock_get_event.assert_called_once_with(1, mock_db)
    assert response.status_code == HTTP_200_OK
    assert response.json() == {
        "id": 1,
        "title": "Test",
        "description": "Test",
        "date": "2024-01-01T12:00:00Z",
        "is_offline": True,
        "location": "Innopolis",
        "organizer_email": "g.popov@inno.ru",
        "max_participants": 60,
    }


def test__get_event_info__no_event() -> None:
    """Test to get the event info."""
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

    with patch(
        "src.app.presentation.events.events_logic.get_event",
        side_effect=event_errors.EventNotFoundError(1),
    ) as mock_get_event:
        response = client.get("/events/1")

    mock_get_event.assert_called_once_with(1, mock_db)
    assert response.status_code == HTTP_404_NOT_FOUND
