import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

import src.app.exceptions.events as event_errors
from src.app.logic.events import (
    create_event,
    get_event,
    assert_user_is_organizer,
    delete_event,
    get_events_list
)
from src.app.repo.users import User
from src.app.repo.events import Event
from src.app.models.events import EventBase


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


def test__create_event__valid() -> None:
    """Check the valid event creation."""
    mock_db = MagicMock()
    event_base = EventBase(
        title="Midterm",
        description="Midterm Assignment",
        date=datetime(2024, 1, 1, 12, 0),
        is_offline=True,
        location="Room 108",
        max_participants=60
    )
    
    mock_event = create_mock_event(
        id=1,
        title=event_base.title,
        description=event_base.description,
        date=event_base.date,
        is_offline=event_base.is_offline,
        location=event_base.location,
        organizer_email="g.popov@inno.ru",
        max_participants=event_base.max_participants
    )

    with patch("src.app.logic.events.Event", return_value=mock_event):
        event = create_event(event_base, "g.popov@inno.ru", mock_db)

    mock_db.add.assert_called_once_with(mock_event)
    mock_db.flush.assert_called_once()
    assert event == mock_event


def test__get_event__exists() -> None:
    """Check existing event is returned."""
    mock_db = MagicMock()
    event_id = 1
    mock_event = create_mock_event(id=event_id, title="Midterm")
    mock_db.query().filter_by().first.return_value = mock_event

    event = get_event(event_id, mock_db)
    assert event == mock_event


def test__get_event__not_found() -> None:
    """Check that EventNotFoundError is raised if event missing."""
    mock_db = MagicMock()
    event_id = 1
    mock_db.query().filter_by().first.return_value = None

    with pytest.raises(event_errors.EventNotFoundError):
        get_event(event_id, mock_db)


def test__assert_user_is_organizer__success() -> None:
    """Check organizer user passes."""
    event = create_mock_event(id=1, organizer_email="g.popov@inno.ru")
    user = create_mock_user(email="g.popov@inno.ru")
    assert_user_is_organizer(event, user)


def test__assert_user_is_organizer__fail() -> None:
    """Check non-organizer user raises OrginizatorRoleRequiredError."""
    event = create_mock_event(id=1, organizer_email="g.popov@inno.ru")
    user = create_mock_user(email="a.popov@inno.ru")

    with pytest.raises(event_errors.OrginizatorRoleRequiredError):
        assert_user_is_organizer(event, user)


def test__delete_event__called() -> None:
    """Check delete_event calls db.delete."""
    mock_db = MagicMock()
    event = create_mock_event(id=1, title="Midterm")
    
    delete_event(event, mock_db)
    mock_db.delete.assert_called_once_with(event)


def test__get_events_list() -> None:
    """Check all events are returned."""
    mock_db = MagicMock()
    mock_events = [
        create_mock_event(id=1, title="Event 1"),
        create_mock_event(id=2, title="Event 2")
    ]
    mock_db.query().all.return_value = mock_events
    events = get_events_list(mock_db)
    mock_db.query().all.assert_called_once()
    assert events == mock_events
