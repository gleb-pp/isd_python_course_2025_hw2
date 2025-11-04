from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

import src.app.exceptions.users as user_errors
from src.app.auth import get_current_user
from src.app.db import get_db
from src.app.main import app
from src.app.repo.events import Event
from src.app.repo.users import User

client = TestClient(app)

HTTP_200_OK = 200
HTTP_401_UNAUTHORIZED = 401
HTTP_403_FORBIDDEN = 403


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


def test__get_top_registrations_events__success() -> None:
    """Test to get top registrations events from admin account."""
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: "admin@inno.ru"

    mock_admin = create_mock_user()
    mock_events = [
        create_mock_event(id=1, title="Event 1"),
        create_mock_event(id=2, title="Event 2"),
        create_mock_event(id=3, title="Event 3"),
    ]
    user_bookings = [10, 5, 8]

    with (
        patch(
            "src.app.presentation.metrics.user_logic.get_user", return_value=mock_admin
        ) as mock_get_user,
        patch(
            "src.app.presentation.metrics.user_logic.assert_user_is_admin"
        ) as mock_assert_admin,
        patch(
            "src.app.presentation.metrics.events_logic.get_events_list",
            return_value=mock_events,
        ) as mock_get_events,
        patch(
            "src.app.presentation.metrics.metrics_logic.get_event_registrations",
            side_effect=user_bookings,
        ) as mock_get_registrations,
    ):
        response = client.get("/admin/metrics/top_registrations?events_number=2")

    mock_get_user.assert_called_once_with("admin@inno.ru", mock_db)
    mock_assert_admin.assert_called_once_with(mock_admin)
    mock_get_events.assert_called_once_with(mock_db)
    assert mock_get_registrations.call_count == len(mock_events)
    assert response.status_code == HTTP_200_OK
    assert response.json() == {
        "events": [
            {"event_id": 1, "registrations": 10},
            {"event_id": 3, "registrations": 8},
        ]
    }


def test__get_top_registrations_events__random_user() -> None:
    """Attempt to get top registrations events from random email."""
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: "admin@inno.ru"

    with (
        patch(
            "src.app.presentation.metrics.user_logic.get_user",
            side_effect=user_errors.UserNotFoundError("admin@inno.ru"),
        ) as mock_get_user,
        patch(
            "src.app.presentation.metrics.user_logic.assert_user_is_admin"
        ) as mock_assert_admin,
        patch(
            "src.app.presentation.metrics.events_logic.get_events_list"
        ) as mock_get_events,
    ):
        response = client.get("/admin/metrics/top_registrations?events_number=2")

    mock_get_user.assert_called_once_with("admin@inno.ru", mock_db)
    mock_assert_admin.assert_not_called()
    mock_get_events.assert_not_called()
    assert response.status_code == HTTP_401_UNAUTHORIZED


def test__get_top_registrations_events__non_admin() -> None:
    """Attempt to get top registrations events from non-admin account."""
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: "user@inno.ru"

    mock_user = create_mock_user()

    with (
        patch(
            "src.app.presentation.metrics.user_logic.get_user", return_value=mock_user
        ) as mock_get_user,
        patch(
            "src.app.presentation.metrics.user_logic.assert_user_is_admin",
            side_effect=user_errors.AdminRoleRequiredError("user@inno.ru"),
        ) as mock_assert_admin,
        patch(
            "src.app.presentation.metrics.events_logic.get_events_list"
        ) as mock_get_events,
    ):
        response = client.get("/admin/metrics/top_registrations?events_number=2")

    mock_get_user.assert_called_once_with("user@inno.ru", mock_db)
    mock_assert_admin.assert_called_once_with(mock_user)
    mock_get_events.assert_not_called()
    assert response.status_code == HTTP_403_FORBIDDEN


def test__get_average_registrations__success() -> None:
    """Test to get average registrations from admin account."""
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: "admin@inno.ru"

    mock_admin = create_mock_user()
    mock_events = [
        create_mock_event(id=1),
        create_mock_event(id=2),
        create_mock_event(id=3),
    ]
    user_bookings = [10, 5, 8]

    with (
        patch(
            "src.app.presentation.metrics.user_logic.get_user", return_value=mock_admin
        ) as mock_get_user,
        patch(
            "src.app.presentation.metrics.user_logic.assert_user_is_admin"
        ) as mock_assert_admin,
        patch(
            "src.app.presentation.metrics.events_logic.get_events_list",
            return_value=mock_events,
        ) as mock_get_events,
        patch(
            "src.app.presentation.metrics.metrics_logic.get_event_registrations",
            side_effect=user_bookings,
        ) as mock_get_registrations,
    ):
        response = client.get("/admin/metrics/average_registrations")

    mock_get_user.assert_called_once_with("admin@inno.ru", mock_db)
    mock_assert_admin.assert_called_once_with(mock_admin)
    mock_get_events.assert_called_once_with(mock_db)
    assert mock_get_registrations.call_count == len(mock_events)
    assert response.status_code == HTTP_200_OK
    assert response.json() == {
        "average_registrations": sum(user_bookings) / len(user_bookings)
    }


def test__get_average_registrations__no_events() -> None:
    """Test to get average registrations when there are no events."""
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: "admin@inno.ru"

    mock_admin = create_mock_user()

    with (
        patch(
            "src.app.presentation.metrics.user_logic.get_user", return_value=mock_admin
        ) as mock_get_user,
        patch(
            "src.app.presentation.metrics.user_logic.assert_user_is_admin"
        ) as mock_assert_admin,
        patch(
            "src.app.presentation.metrics.events_logic.get_events_list", return_value=[]
        ) as mock_get_events,
    ):
        response = client.get("/admin/metrics/average_registrations")

    mock_get_user.assert_called_once_with("admin@inno.ru", mock_db)
    mock_assert_admin.assert_called_once_with(mock_admin)
    mock_get_events.assert_called_once_with(mock_db)
    assert response.status_code == HTTP_200_OK
    assert response.json() == {"average_registrations": 0.0}


def test__get_average_registrations__random_user() -> None:
    """Attempt to get average registrations from random email."""
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: "admin@inno.ru"

    with (
        patch(
            "src.app.presentation.metrics.user_logic.get_user",
            side_effect=user_errors.UserNotFoundError("admin@inno.ru"),
        ) as mock_get_user,
        patch(
            "src.app.presentation.metrics.user_logic.assert_user_is_admin"
        ) as mock_assert_admin,
        patch(
            "src.app.presentation.metrics.events_logic.get_events_list"
        ) as mock_get_events,
    ):
        response = client.get("/admin/metrics/average_registrations")

    mock_get_user.assert_called_once_with("admin@inno.ru", mock_db)
    mock_assert_admin.assert_not_called()
    mock_get_events.assert_not_called()
    assert response.status_code == HTTP_401_UNAUTHORIZED


def test__get_average_registrations__non_admin() -> None:
    """Attempt to get average registrations from non-admin account."""
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: "admin@inno.ru"

    mock_admin = create_mock_user()

    with (
        patch(
            "src.app.presentation.metrics.user_logic.get_user", return_value=mock_admin
        ) as mock_get_user,
        patch(
            "src.app.presentation.metrics.user_logic.assert_user_is_admin",
            side_effect=user_errors.AdminRoleRequiredError("user@inno.ru"),
        ) as mock_assert_admin,
        patch(
            "src.app.presentation.metrics.events_logic.get_events_list"
        ) as mock_get_events,
    ):
        response = client.get("/admin/metrics/average_registrations")

    mock_get_user.assert_called_once_with("admin@inno.ru", mock_db)
    mock_assert_admin.assert_called_once_with(mock_admin)
    mock_get_events.assert_not_called()
    assert response.status_code == HTTP_403_FORBIDDEN


def test__get_average_bookings_per_user__success() -> None:
    """Test to get average bookings per user from admin account."""
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: "admin@inno.ru"

    mock_admin = create_mock_user()
    mock_users = [
        create_mock_user(email="user1@inno.ru"),
        create_mock_user(email="user2@inno.ru"),
        create_mock_user(email="user3@inno.ru"),
    ]
    user_bookings = [3, 2, 5]

    with (
        patch(
            "src.app.presentation.metrics.user_logic.get_user", return_value=mock_admin
        ) as mock_get_user,
        patch(
            "src.app.presentation.metrics.user_logic.assert_user_is_admin"
        ) as mock_assert_admin,
        patch(
            "src.app.presentation.metrics.user_logic.get_all_users",
            return_value=mock_users,
        ) as mock_get_all_users,
        patch(
            "src.app.presentation.metrics.metrics_logic.get_user_bookings",
            side_effect=user_bookings,
        ) as mock_get_user_bookings,
    ):
        response = client.get("/admin/metrics/average_bookings_per_user")

    mock_get_user.assert_called_once_with("admin@inno.ru", mock_db)
    mock_assert_admin.assert_called_once_with(mock_admin)
    mock_get_all_users.assert_called_once_with(mock_db)
    assert mock_get_user_bookings.call_count == len(user_bookings)
    assert response.status_code == HTTP_200_OK
    assert response.json() == {
        "average_bookings_per_user": sum(user_bookings) / len(user_bookings)
    }


def test__get_average_bookings_per_user__no_users() -> None:
    """Test to get average bookings per user when there are no users."""
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: "admin@inno.ru"

    mock_admin = create_mock_user()

    with (
        patch(
            "src.app.presentation.metrics.user_logic.get_user", return_value=mock_admin
        ) as mock_get_user,
        patch(
            "src.app.presentation.metrics.user_logic.assert_user_is_admin"
        ) as mock_assert_admin,
        patch(
            "src.app.presentation.metrics.user_logic.get_all_users", return_value=[]
        ) as mock_get_all_users,
    ):
        response = client.get("/admin/metrics/average_bookings_per_user")

    mock_get_user.assert_called_once_with("admin@inno.ru", mock_db)
    mock_assert_admin.assert_called_once_with(mock_admin)
    mock_get_all_users.assert_called_once_with(mock_db)
    assert response.status_code == HTTP_200_OK
    assert response.json() == {"average_bookings_per_user": 0.0}


def test__get_average_bookings_per_user__random_user() -> None:
    """Attempt to get average bookings per user from random email."""
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: "admin@inno.ru"

    with (
        patch(
            "src.app.presentation.metrics.user_logic.get_user",
            side_effect=user_errors.UserNotFoundError("admin@inno.ru"),
        ) as mock_get_user,
        patch(
            "src.app.presentation.metrics.user_logic.assert_user_is_admin"
        ) as mock_assert_admin,
        patch(
            "src.app.presentation.metrics.user_logic.get_all_users"
        ) as mock_get_all_users,
    ):
        response = client.get("/admin/metrics/average_bookings_per_user")

    mock_get_user.assert_called_once_with("admin@inno.ru", mock_db)
    mock_assert_admin.assert_not_called()
    mock_get_all_users.assert_not_called()
    assert response.status_code == HTTP_401_UNAUTHORIZED


def test__get_average_bookings_per_user__non_admin() -> None:
    """Attempt to get average bookings per user from non-admin account."""
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: "admin@inno.ru"

    mock_admin = create_mock_user()

    with (
        patch(
            "src.app.presentation.metrics.user_logic.get_user", return_value=mock_admin
        ) as mock_get_user,
        patch(
            "src.app.presentation.metrics.user_logic.assert_user_is_admin",
            side_effect=user_errors.AdminRoleRequiredError("user@inno.ru"),
        ) as mock_assert_admin,
        patch(
            "src.app.presentation.metrics.user_logic.get_all_users"
        ) as mock_get_all_users,
    ):
        response = client.get("/admin/metrics/average_bookings_per_user")

    mock_get_user.assert_called_once_with("admin@inno.ru", mock_db)
    mock_assert_admin.assert_called_once_with(mock_admin)
    mock_get_all_users.assert_not_called()
    assert response.status_code == HTTP_403_FORBIDDEN


def test__get_offline_events_ratio__success() -> None:
    """Test to get offline events ratio from admin account."""
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: "admin@inno.ru"

    mock_admin = create_mock_user()
    mock_events = [
        create_mock_event(id=1, is_offline=True),
        create_mock_event(id=2, is_offline=False),
        create_mock_event(id=3, is_offline=True),
        create_mock_event(id=4, is_offline=False),
    ]

    with (
        patch(
            "src.app.presentation.metrics.user_logic.get_user", return_value=mock_admin
        ) as mock_get_user,
        patch(
            "src.app.presentation.metrics.user_logic.assert_user_is_admin"
        ) as mock_assert_admin,
        patch(
            "src.app.presentation.metrics.events_logic.get_events_list",
            return_value=mock_events,
        ) as mock_get_events,
    ):
        response = client.get("/admin/metrics/offline_ratio")

    mock_get_user.assert_called_once_with("admin@inno.ru", mock_db)
    mock_assert_admin.assert_called_once_with(mock_admin)
    mock_get_events.assert_called_once_with(mock_db)
    assert response.status_code == HTTP_200_OK
    assert response.json() == {"offline_events_ratio": 0.5}


def test__get_offline_events_ratio__all_offline() -> None:
    """Test to get offline events ratio when all events are offline."""
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: "admin@inno.ru"

    mock_admin = create_mock_user()
    mock_events = [
        create_mock_event(id=1, is_offline=True),
        create_mock_event(id=2, is_offline=True),
    ]

    with (
        patch(
            "src.app.presentation.metrics.user_logic.get_user", return_value=mock_admin
        ) as mock_get_user,
        patch(
            "src.app.presentation.metrics.user_logic.assert_user_is_admin"
        ) as mock_assert_admin,
        patch(
            "src.app.presentation.metrics.events_logic.get_events_list",
            return_value=mock_events,
        ) as mock_get_events,
    ):
        response = client.get("/admin/metrics/offline_ratio")

    mock_get_user.assert_called_once_with("admin@inno.ru", mock_db)
    mock_assert_admin.assert_called_once_with(mock_admin)
    mock_get_events.assert_called_once_with(mock_db)
    assert response.status_code == HTTP_200_OK
    assert response.json() == {"offline_events_ratio": 1.0}


def test__get_offline_events_ratio__all_online() -> None:
    """Test to get offline events ratio when all events are online."""
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: "admin@inno.ru"

    mock_admin = create_mock_user()
    mock_events = [
        create_mock_event(id=1, is_offline=False),
        create_mock_event(id=2, is_offline=False),
    ]

    with (
        patch(
            "src.app.presentation.metrics.user_logic.get_user", return_value=mock_admin
        ) as mock_get_user,
        patch(
            "src.app.presentation.metrics.user_logic.assert_user_is_admin"
        ) as mock_assert_admin,
        patch(
            "src.app.presentation.metrics.events_logic.get_events_list",
            return_value=mock_events,
        ) as mock_get_events,
    ):
        response = client.get("/admin/metrics/offline_ratio")

    mock_get_user.assert_called_once_with("admin@inno.ru", mock_db)
    mock_assert_admin.assert_called_once_with(mock_admin)
    mock_get_events.assert_called_once_with(mock_db)
    assert response.status_code == HTTP_200_OK
    assert response.json() == {"offline_events_ratio": 0.0}


def test__get_offline_events_ratio__no_events() -> None:
    """Test to get offline events ratio when there are no events."""
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: "admin@inno.ru"

    mock_admin = create_mock_user()

    with (
        patch(
            "src.app.presentation.metrics.user_logic.get_user", return_value=mock_admin
        ) as mock_get_user,
        patch(
            "src.app.presentation.metrics.user_logic.assert_user_is_admin"
        ) as mock_assert_admin,
        patch(
            "src.app.presentation.metrics.events_logic.get_events_list", return_value=[]
        ) as mock_get_events,
    ):
        response = client.get("/admin/metrics/offline_ratio")

    mock_get_user.assert_called_once_with("admin@inno.ru", mock_db)
    mock_assert_admin.assert_called_once_with(mock_admin)
    mock_get_events.assert_called_once_with(mock_db)
    assert response.status_code == HTTP_200_OK
    assert response.json() == {"offline_events_ratio": 0.0}


def test__get_offline_events_ratio__random_user() -> None:
    """Attempt to get offline events ratio from random email."""
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: "admin@inno.ru"

    with (
        patch(
            "src.app.presentation.metrics.user_logic.get_user",
            side_effect=user_errors.UserNotFoundError("admin@inno.ru"),
        ) as mock_get_user,
        patch(
            "src.app.presentation.metrics.user_logic.assert_user_is_admin"
        ) as mock_assert_admin,
        patch(
            "src.app.presentation.metrics.events_logic.get_events_list"
        ) as mock_get_events,
    ):
        response = client.get("/admin/metrics/offline_ratio")

    mock_get_user.assert_called_once_with("admin@inno.ru", mock_db)
    mock_assert_admin.assert_not_called()
    mock_get_events.assert_not_called()
    assert response.status_code == HTTP_401_UNAUTHORIZED


def test__get_offline_events_ratio__non_admin() -> None:
    """Attempt to get offline events ratio from non-admin account."""
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: "user@inno.ru"

    mock_user = create_mock_user()

    with (
        patch(
            "src.app.presentation.metrics.user_logic.get_user", return_value=mock_user
        ) as mock_get_user,
        patch(
            "src.app.presentation.metrics.user_logic.assert_user_is_admin",
            side_effect=user_errors.AdminRoleRequiredError("user@inno.ru"),
        ) as mock_assert_admin,
        patch(
            "src.app.presentation.metrics.events_logic.get_events_list"
        ) as mock_get_events,
    ):
        response = client.get("/admin/metrics/offline_ratio")

    mock_get_user.assert_called_once_with("user@inno.ru", mock_db)
    mock_assert_admin.assert_called_once_with(mock_user)
    mock_get_events.assert_not_called()
    assert response.status_code == HTTP_403_FORBIDDEN
