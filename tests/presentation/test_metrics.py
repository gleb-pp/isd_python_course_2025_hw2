from typing import Any, cast
from unittest.mock import MagicMock, _patch, patch

import pytest
from fastapi.testclient import TestClient

import src.app.domain.exceptions.users as user_errors
from src.app.auth import get_current_user
from src.app.db import get_db
from src.app.infrastructure.db_models.events import EventDB
from src.app.infrastructure.db_models.users import UserDB
from src.app.main import app

client = TestClient(app)

HTTP_200_OK = 200
HTTP_401_UNAUTHORIZED = 401
HTTP_403_FORBIDDEN = 403


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


def setup_mocks(current_user_email: str = "admin@inno.ru") -> MagicMock:
    """Set up common mocks for DB and current user."""
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: current_user_email
    return mock_db


def call_endpoint(
    url: str,
    *,
    mock_get_user: dict[str, Any] | None = None,
    mock_assert_admin: dict[str, Any] | None = None,
    mock_get_events: dict[str, Any] | None = None,
    mock_get_all_users: dict[str, Any] | None = None,
    mock_get_registrations: dict[str, Any] | None = None,
    mock_get_user_bookings: dict[str, Any] | None = None,
) -> tuple:
    """Help to perform GET request with all needed patches."""
    with (
        cast(
            "_patch[Any]",
            patch(
                "src.app.presentation.metrics.user_logic.get_user",
                **(mock_get_user or {}),
            ),
        ) as get_user,
        cast(
            "_patch[Any]",
            patch(
                "src.app.presentation.metrics.user_logic.assert_user_is_admin",
                **(mock_assert_admin or {}),
            ),
        ) as assert_admin,
        cast(
            "_patch[Any]",
            patch(
                "src.app.presentation.metrics.events_logic.get_events_list",
                **(mock_get_events or {}),
            ),
        ) as get_events,
        cast(
            "_patch[Any]",
            patch(
                "src.app.presentation.metrics.user_logic.get_all_users",
                **(mock_get_all_users or {}),
            ),
        ) as get_all_users,
        cast(
            "_patch[Any]",
            patch(
                "src.app.presentation.metrics.metrics_logic.get_event_registrations",
                **(mock_get_registrations or {}),
            ),
        ) as get_regs,
        cast(
            "_patch[Any]",
            patch(
                "src.app.presentation.metrics.metrics_logic.get_user_bookings",
                **(mock_get_user_bookings or {}),
            ),
        ) as get_bookings,
    ):
        response = client.get(url)
    return (
        response,
        get_user,
        assert_admin,
        get_events,
        get_all_users,
        get_regs,
        get_bookings,
    )


def test__get_top_registrations_events__success() -> None:
    """Test to get top registrations events from admin account."""
    mock_db = setup_mocks()

    mock_admin = create_mock_user()
    mock_events = [
        create_mock_event(id=1, title="EventDB 1"),
        create_mock_event(id=2, title="EventDB 2"),
        create_mock_event(id=3, title="EventDB 3"),
    ]
    user_bookings = [10, 5, 8]

    response, get_user, assert_admin, get_events, _, get_registrations, _ = (
        call_endpoint(
            "/admin/metrics/top_registrations?events_number=2",
            mock_get_user={"return_value": mock_admin},
            mock_assert_admin={},
            mock_get_events={"return_value": mock_events},
            mock_get_registrations={"side_effect": user_bookings},
        )
    )

    get_user.assert_called_once_with("admin@inno.ru", mock_db)
    assert_admin.assert_called_once_with(mock_admin)
    get_events.assert_called_once_with(mock_db)
    assert get_registrations.call_count == len(mock_events)
    assert response.status_code == HTTP_200_OK
    assert response.json() == {
        "events": [
            {"event_id": 1, "registrations": 10},
            {"event_id": 3, "registrations": 8},
        ]
    }


def test__get_top_registrations_events__random_user() -> None:
    """Attempt to get top registrations events from random email."""
    mock_db = setup_mocks()

    response, get_user, assert_admin, get_events, _, get_registrations, _ = (
        call_endpoint(
            "/admin/metrics/top_registrations?events_number=2",
            mock_get_user={
                "side_effect": user_errors.UserNotFoundError("admin@inno.ru")
            },
            mock_assert_admin={},
            mock_get_events={},
            mock_get_registrations={},
        )
    )

    get_user.assert_called_once_with("admin@inno.ru", mock_db)
    assert_admin.assert_not_called()
    get_events.assert_not_called()
    get_registrations.assert_not_called()
    assert response.status_code == HTTP_401_UNAUTHORIZED


def test__get_top_registrations_events__non_admin() -> None:
    """Attempt to get top registrations events from non-admin account."""
    mock_db = setup_mocks("user@inno.ru")
    mock_user = create_mock_user()

    (
        response,
        mock_get_user,
        mock_assert_admin,
        mock_get_events,
        _,
        mock_get_registrations,
        _,
    ) = call_endpoint(
        "/admin/metrics/top_registrations?events_number=2",
        mock_get_user={"return_value": mock_user},
        mock_assert_admin={
            "side_effect": user_errors.AdminRoleRequiredError("user@inno.ru")
        },
        mock_get_events={},
        mock_get_registrations={},
    )

    mock_get_user.assert_called_once_with("user@inno.ru", mock_db)
    mock_assert_admin.assert_called_once_with(mock_user)
    mock_get_events.assert_not_called()
    mock_get_registrations.assert_not_called()
    assert response.status_code == HTTP_403_FORBIDDEN


def test__get_average_registrations__success() -> None:
    """Test to get average registrations from admin account."""
    mock_db = setup_mocks()
    mock_admin = create_mock_user()
    mock_events = [create_mock_event(id=i) for i in range(3)]
    user_bookings = [10, 5, 8]

    (
        response,
        mock_get_user,
        mock_assert_admin,
        mock_get_events,
        _,
        mock_get_registrations,
        _,
    ) = call_endpoint(
        "/admin/metrics/average_registrations",
        mock_get_user={"return_value": mock_admin},
        mock_assert_admin={},
        mock_get_events={"return_value": mock_events},
        mock_get_registrations={"side_effect": user_bookings},
    )

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
    mock_db = setup_mocks()
    mock_admin = create_mock_user()

    (
        response,
        mock_get_user,
        mock_assert_admin,
        mock_get_events,
        _,
        mock_get_registrations,
        _,
    ) = call_endpoint(
        "/admin/metrics/average_registrations",
        mock_get_user={"return_value": mock_admin},
        mock_assert_admin={},
        mock_get_events={"return_value": []},
        mock_get_registrations={},
    )

    mock_get_user.assert_called_once_with("admin@inno.ru", mock_db)
    mock_assert_admin.assert_called_once_with(mock_admin)
    mock_get_events.assert_called_once_with(mock_db)
    mock_get_registrations.assert_not_called()
    assert response.status_code == HTTP_200_OK
    assert response.json() == {"average_registrations": 0.0}


def test__get_average_registrations__random_user() -> None:
    """Attempt to get average registrations from random email."""
    mock_db = setup_mocks()

    (
        response,
        mock_get_user,
        mock_assert_admin,
        mock_get_events,
        _,
        mock_get_registrations,
        _,
    ) = call_endpoint(
        "/admin/metrics/average_registrations",
        mock_get_user={"side_effect": user_errors.UserNotFoundError("admin@inno.ru")},
        mock_assert_admin={},
        mock_get_events={},
        mock_get_registrations={},
    )

    mock_get_user.assert_called_once_with("admin@inno.ru", mock_db)
    mock_assert_admin.assert_not_called()
    mock_get_events.assert_not_called()
    mock_get_registrations.assert_not_called()
    assert response.status_code == HTTP_401_UNAUTHORIZED


def test__get_average_registrations__non_admin() -> None:
    """Attempt to get average registrations from non-admin account."""
    mock_db = setup_mocks("user@inno.ru")
    mock_admin = create_mock_user()

    (
        response,
        mock_get_user,
        mock_assert_admin,
        mock_get_events,
        _,
        mock_get_registrations,
        _,
    ) = call_endpoint(
        "/admin/metrics/average_registrations",
        mock_get_user={"return_value": mock_admin},
        mock_assert_admin={
            "side_effect": user_errors.AdminRoleRequiredError("user@inno.ru")
        },
        mock_get_events={},
        mock_get_registrations={},
    )

    mock_get_user.assert_called_once_with("user@inno.ru", mock_db)
    mock_assert_admin.assert_called_once_with(mock_admin)
    mock_get_events.assert_not_called()
    mock_get_registrations.assert_not_called()
    assert response.status_code == HTTP_403_FORBIDDEN


def test__get_average_bookings_per_user__success() -> None:
    """Test to get average bookings per user from admin account."""
    mock_db = setup_mocks()
    mock_admin = create_mock_user()
    mock_users = [create_mock_user(email=f"user{i}@inno.ru") for i in range(3)]
    user_bookings = [3, 2, 5]

    (
        response,
        mock_get_user,
        mock_assert_admin,
        _,
        mock_get_all_users,
        _,
        mock_get_user_bookings,
    ) = call_endpoint(
        "/admin/metrics/average_bookings_per_user",
        mock_get_user={"return_value": mock_admin},
        mock_assert_admin={},
        mock_get_all_users={"return_value": mock_users},
        mock_get_user_bookings={"side_effect": user_bookings},
    )

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
    mock_db = setup_mocks()
    mock_admin = create_mock_user()

    (
        response,
        mock_get_user,
        mock_assert_admin,
        _,
        mock_get_all_users,
        _,
        mock_get_user_bookings,
    ) = call_endpoint(
        "/admin/metrics/average_bookings_per_user",
        mock_get_user={"return_value": mock_admin},
        mock_assert_admin={},
        mock_get_all_users={"return_value": []},
        mock_get_user_bookings={},
    )

    mock_get_user.assert_called_once_with("admin@inno.ru", mock_db)
    mock_assert_admin.assert_called_once_with(mock_admin)
    mock_get_all_users.assert_called_once_with(mock_db)
    mock_get_user_bookings.assert_not_called()
    assert response.status_code == HTTP_200_OK
    assert response.json() == {"average_bookings_per_user": 0.0}


def test__get_average_bookings_per_user__random_user() -> None:
    """Attempt to get average bookings per user from random email."""
    mock_db = setup_mocks()

    (
        response,
        mock_get_user,
        mock_assert_admin,
        _,
        mock_get_all_users,
        _,
        mock_get_user_bookings,
    ) = call_endpoint(
        "/admin/metrics/average_bookings_per_user",
        mock_get_user={"side_effect": user_errors.UserNotFoundError("admin@inno.ru")},
        mock_assert_admin={},
        mock_get_all_users={},
        mock_get_user_bookings={},
    )

    mock_get_user.assert_called_once_with("admin@inno.ru", mock_db)
    mock_assert_admin.assert_not_called()
    mock_get_all_users.assert_not_called()
    mock_get_user_bookings.assert_not_called()
    assert response.status_code == HTTP_401_UNAUTHORIZED


def test__get_average_bookings_per_user__non_admin() -> None:
    """Attempt to get average bookings per user from non-admin account."""
    mock_db = setup_mocks("user@inno.ru")
    mock_admin = create_mock_user()

    (
        response,
        mock_get_user,
        mock_assert_admin,
        _,
        mock_get_all_users,
        _,
        mock_get_user_bookings,
    ) = call_endpoint(
        "/admin/metrics/average_bookings_per_user",
        mock_get_user={"return_value": mock_admin},
        mock_assert_admin={
            "side_effect": user_errors.AdminRoleRequiredError("user@inno.ru")
        },
        mock_get_all_users={},
        mock_get_user_bookings={},
    )

    mock_get_user.assert_called_once_with("user@inno.ru", mock_db)
    mock_assert_admin.assert_called_once_with(mock_admin)
    mock_get_all_users.assert_not_called()
    mock_get_user_bookings.assert_not_called()
    assert response.status_code == HTTP_403_FORBIDDEN


@pytest.mark.parametrize(
    ("mock_events", "ratio"),
    [
        ([create_mock_event(id=i, is_offline=(i % 2 == 0)) for i in range(4)], 0.5),
        ([create_mock_event(id=i, is_offline=True) for i in range(4)], 1.0),
        ([create_mock_event(id=i, is_offline=False) for i in range(4)], 0.0),
        ([], 0.0),
    ],
)
def test__get_offline_events_ratio__success(
    mock_events: list[MagicMock], ratio: float
) -> None:
    """Test to get offline events ratio from admin account."""
    mock_db = setup_mocks()
    mock_admin = create_mock_user()

    response, mock_get_user, mock_assert_admin, mock_get_events, _, _, _ = (
        call_endpoint(
            "/admin/metrics/offline_ratio",
            mock_get_user={"return_value": mock_admin},
            mock_assert_admin={},
            mock_get_events={"return_value": mock_events},
        )
    )

    mock_get_user.assert_called_once_with("admin@inno.ru", mock_db)
    mock_assert_admin.assert_called_once_with(mock_admin)
    mock_get_events.assert_called_once_with(mock_db)
    assert response.status_code == HTTP_200_OK
    assert response.json() == {"offline_events_ratio": ratio}


def test__get_offline_events_ratio__random_user() -> None:
    """Attempt to get offline events ratio from random email."""
    mock_db = setup_mocks()

    response, mock_get_user, mock_assert_admin, mock_get_events, _, _, _ = (
        call_endpoint(
            "/admin/metrics/offline_ratio",
            mock_get_user={
                "side_effect": user_errors.UserNotFoundError("admin@inno.ru")
            },
            mock_assert_admin={},
            mock_get_events={},
        )
    )

    mock_get_user.assert_called_once_with("admin@inno.ru", mock_db)
    mock_assert_admin.assert_not_called()
    mock_get_events.assert_not_called()
    assert response.status_code == HTTP_401_UNAUTHORIZED


def test__get_offline_events_ratio__non_admin() -> None:
    """Attempt to get offline events ratio from non-admin account."""
    mock_db = setup_mocks("user@inno.ru")
    mock_user = create_mock_user()

    response, mock_get_user, mock_assert_admin, mock_get_events, _, _, _ = (
        call_endpoint(
            "/admin/metrics/offline_ratio",
            mock_get_user={"return_value": mock_user},
            mock_assert_admin={
                "side_effect": user_errors.AdminRoleRequiredError("user@inno.ru")
            },
            mock_get_events={},
        )
    )

    mock_get_user.assert_called_once_with("user@inno.ru", mock_db)
    mock_assert_admin.assert_called_once_with(mock_user)
    mock_get_events.assert_not_called()
    assert response.status_code == HTTP_403_FORBIDDEN
