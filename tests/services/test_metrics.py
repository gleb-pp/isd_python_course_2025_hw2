from unittest.mock import MagicMock, patch

import pytest

import src.app.domain.exceptions.users as user_errors
from src.app.auth import get_current_user
from src.app.db import get_db
from src.app.infrastructure.adapters.events_adapter import EventsAdapter
from src.app.infrastructure.adapters.metrics_adapter import MetricsAdapter
from src.app.infrastructure.adapters.users_adapter import UsersAdapter
from src.app.infrastructure.db_models.events import EventDB
from src.app.infrastructure.db_models.users import UserDB
from src.app.main import app
from src.app.services.metrics import MetricsService
from src.app.services.models.metrics import (
    AverageBookingsPerUser,
    AverageRegistrations,
    OfflineEventsRatio,
    TopRegistrationsMetric,
)


def create_mock_event(**kwargs: object) -> MagicMock:
    """Create a mock Event object for testing."""
    mock_event = MagicMock(spec=EventDB)
    for key, value in kwargs.items():
        setattr(mock_event, key, value)
    return mock_event


def create_mock_user(**kwargs: object) -> MagicMock:
    """Create a mock User object for testing."""
    mock_user = MagicMock(spec=UserDB)
    for key, value in kwargs.items():
        setattr(mock_user, key, value)
    return mock_user


class TestMetricsService:
    """Test class for MetricsService."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.mock_db = MagicMock()
        app.dependency_overrides[get_db] = lambda: self.mock_db
        self.metrics_service = MetricsService(self.mock_db)

    def test__get_top_registrations_events__success(self) -> None:
        """Test to get top registrations events from admin account."""
        app.dependency_overrides[get_current_user] = lambda: "admin@inno.ru"

        mock_admin = create_mock_user()
        mock_events = [
            create_mock_event(id=1),
            create_mock_event(id=2),
            create_mock_event(id=3),
        ]
        user_bookings = [10, 5, 8]

        with (
            patch.object(
                UsersAdapter, "get_user", return_value=mock_admin
            ) as mock_get_user,
            patch.object(UsersAdapter, "assert_user_is_admin") as mock_assert_admin,
            patch.object(
                EventsAdapter,
                "get_events_list",
                return_value=mock_events,
            ) as mock_get_events,
            patch.object(
                MetricsAdapter,
                "get_event_registrations",
                side_effect=user_bookings,
            ) as mock_get_registrations,
        ):
            result = self.metrics_service.get_top_registrations_events(
                "admin@inno.ru", 2
            )

        mock_get_user.assert_called_once_with("admin@inno.ru")
        mock_assert_admin.assert_called_once_with(mock_admin)
        mock_get_events.assert_called_once_with()
        assert mock_get_registrations.call_count == len(mock_events)
        assert isinstance(result, TopRegistrationsMetric)
        assert len(result.events) == 2
        assert result.events[0].event_id == 1
        assert result.events[1].event_id == 3
        assert result.events[0].registrations == 10
        assert result.events[1].registrations == 8

    def test__get_top_registrations_events__random_user(self) -> None:
        """Attempt to get top registrations events from random email."""
        app.dependency_overrides[get_current_user] = lambda: "admin@inno.ru"

        with (
            patch.object(
                UsersAdapter,
                "get_user",
                side_effect=user_errors.UserNotFoundError("admin@inno.ru"),
            ) as mock_get_user,
            patch.object(UsersAdapter, "assert_user_is_admin") as mock_assert_admin,
            patch.object(EventsAdapter, "get_events_list") as mock_get_events,
        ):
            with pytest.raises(user_errors.UserNotFoundError):
                self.metrics_service.get_top_registrations_events("admin@inno.ru", 2)

        mock_get_user.assert_called_once_with("admin@inno.ru")
        mock_assert_admin.assert_not_called()
        mock_get_events.assert_not_called()

    def test__get_top_registrations_events__non_admin(self) -> None:
        """Attempt to get top registrations events from non-admin account."""
        app.dependency_overrides[get_current_user] = lambda: "user@inno.ru"

        mock_user = create_mock_user()

        with (
            patch.object(
                UsersAdapter, "get_user", return_value=mock_user
            ) as mock_get_user,
            patch.object(
                UsersAdapter,
                "assert_user_is_admin",
                side_effect=user_errors.AdminRoleRequiredError("user@inno.ru"),
            ) as mock_assert_admin,
            patch.object(EventsAdapter, "get_events_list") as mock_get_events,
        ):
            with pytest.raises(user_errors.AdminRoleRequiredError):
                self.metrics_service.get_top_registrations_events("user@inno.ru", 2)

        mock_get_user.assert_called_once_with("user@inno.ru")
        mock_assert_admin.assert_called_once_with(mock_user)
        mock_get_events.assert_not_called()

    def test__get_average_registrations__success(self) -> None:
        """Test to get average registrations from admin account."""
        app.dependency_overrides[get_current_user] = lambda: "admin@inno.ru"

        mock_admin = create_mock_user()
        mock_events = [
            create_mock_event(id=1),
            create_mock_event(id=2),
            create_mock_event(id=3),
        ]
        user_bookings = [10, 5, 8]

        with (
            patch.object(
                UsersAdapter, "get_user", return_value=mock_admin
            ) as mock_get_user,
            patch.object(UsersAdapter, "assert_user_is_admin") as mock_assert_admin,
            patch.object(
                EventsAdapter,
                "get_events_list",
                return_value=mock_events,
            ) as mock_get_events,
            patch.object(
                MetricsAdapter,
                "get_event_registrations",
                side_effect=user_bookings,
            ) as mock_get_registrations,
        ):
            result = self.metrics_service.get_average_registrations("admin@inno.ru")

        mock_get_user.assert_called_once_with("admin@inno.ru")
        mock_assert_admin.assert_called_once_with(mock_admin)
        mock_get_events.assert_called_once_with()
        assert mock_get_registrations.call_count == len(mock_events)
        assert isinstance(result, AverageRegistrations)
        assert result.average_registrations == sum(user_bookings) / len(user_bookings)

    def test__get_average_registrations__no_events(self) -> None:
        """Test to get average registrations when there are no events."""
        app.dependency_overrides[get_current_user] = lambda: "admin@inno.ru"

        mock_admin = create_mock_user()

        with (
            patch.object(
                UsersAdapter, "get_user", return_value=mock_admin
            ) as mock_get_user,
            patch.object(UsersAdapter, "assert_user_is_admin") as mock_assert_admin,
            patch.object(
                EventsAdapter, "get_events_list", return_value=[]
            ) as mock_get_events,
        ):
            result = self.metrics_service.get_average_registrations("admin@inno.ru")

        mock_get_user.assert_called_once_with("admin@inno.ru")
        mock_assert_admin.assert_called_once_with(mock_admin)
        mock_get_events.assert_called_once_with()
        assert isinstance(result, AverageRegistrations)
        assert result.average_registrations == 0.0

    def test__get_average_registrations__random_user(self) -> None:
        """Attempt to get average registrations from random email."""
        app.dependency_overrides[get_current_user] = lambda: "admin@inno.ru"

        with (
            patch.object(
                UsersAdapter,
                "get_user",
                side_effect=user_errors.UserNotFoundError("admin@inno.ru"),
            ) as mock_get_user,
            patch.object(UsersAdapter, "assert_user_is_admin") as mock_assert_admin,
            patch.object(EventsAdapter, "get_events_list") as mock_get_events,
        ):
            with pytest.raises(user_errors.UserNotFoundError):
                self.metrics_service.get_average_registrations("admin@inno.ru")

        mock_get_user.assert_called_once_with("admin@inno.ru")
        mock_assert_admin.assert_not_called()
        mock_get_events.assert_not_called()

    def test__get_average_registrations__non_admin(self) -> None:
        """Attempt to get average registrations from non-admin account."""
        app.dependency_overrides[get_current_user] = lambda: "user@inno.ru"

        mock_admin = create_mock_user()

        with (
            patch.object(
                UsersAdapter, "get_user", return_value=mock_admin
            ) as mock_get_user,
            patch.object(
                UsersAdapter,
                "assert_user_is_admin",
                side_effect=user_errors.AdminRoleRequiredError("user@inno.ru"),
            ) as mock_assert_admin,
            patch.object(EventsAdapter, "get_events_list") as mock_get_events,
        ):
            with pytest.raises(user_errors.AdminRoleRequiredError):
                self.metrics_service.get_average_registrations("user@inno.ru")

        mock_get_user.assert_called_once_with("user@inno.ru")
        mock_assert_admin.assert_called_once_with(mock_admin)
        mock_get_events.assert_not_called()

    def test__get_average_bookings_per_user__success(self) -> None:
        """Test to get average bookings per user from admin account."""
        app.dependency_overrides[get_current_user] = lambda: "admin@inno.ru"

        mock_admin = create_mock_user()
        mock_users = [
            create_mock_user(email="user1@inno.ru"),
            create_mock_user(email="user2@inno.ru"),
            create_mock_user(email="user3@inno.ru"),
        ]
        user_bookings = [3, 2, 5]

        with (
            patch.object(
                UsersAdapter, "get_user", return_value=mock_admin
            ) as mock_get_user,
            patch.object(UsersAdapter, "assert_user_is_admin") as mock_assert_admin,
            patch.object(
                UsersAdapter,
                "get_all_users",
                return_value=mock_users,
            ) as mock_get_all_users,
            patch.object(
                MetricsAdapter,
                "get_user_bookings",
                side_effect=user_bookings,
            ) as mock_get_user_bookings,
        ):
            result = self.metrics_service.get_average_bookings_per_user("admin@inno.ru")

        mock_get_user.assert_called_once_with("admin@inno.ru")
        mock_assert_admin.assert_called_once_with(mock_admin)
        mock_get_all_users.assert_called_once_with()
        assert mock_get_user_bookings.call_count == len(user_bookings)
        assert isinstance(result, AverageBookingsPerUser)
        assert result.average_bookings_per_user == sum(user_bookings) / len(
            user_bookings
        )

    def test__get_average_bookings_per_user__no_users(self) -> None:
        """Test to get average bookings per user when there are no users."""
        app.dependency_overrides[get_current_user] = lambda: "admin@inno.ru"

        mock_admin = create_mock_user()

        with (
            patch.object(
                UsersAdapter, "get_user", return_value=mock_admin
            ) as mock_get_user,
            patch.object(UsersAdapter, "assert_user_is_admin") as mock_assert_admin,
            patch.object(
                UsersAdapter, "get_all_users", return_value=[]
            ) as mock_get_all_users,
            patch.object(MetricsAdapter, "get_user_bookings") as mock_get_user_bookings,
        ):
            result = self.metrics_service.get_average_bookings_per_user("admin@inno.ru")

        mock_get_user.assert_called_once_with("admin@inno.ru")
        mock_assert_admin.assert_called_once_with(mock_admin)
        mock_get_all_users.assert_called_once_with()
        mock_get_user_bookings.assert_not_called()
        assert isinstance(result, AverageBookingsPerUser)
        assert result.average_bookings_per_user == 0.0

    def test__get_average_bookings_per_user__random_user(self) -> None:
        """Attempt to get average bookings per user from random email."""
        app.dependency_overrides[get_current_user] = lambda: "admin@inno.ru"

        with (
            patch.object(
                UsersAdapter,
                "get_user",
                side_effect=user_errors.UserNotFoundError("admin@inno.ru"),
            ) as mock_get_user,
            patch.object(UsersAdapter, "assert_user_is_admin") as mock_assert_admin,
            patch.object(UsersAdapter, "get_all_users") as mock_get_all_users,
            patch.object(MetricsAdapter, "get_user_bookings") as mock_get_user_bookings,
        ):
            with pytest.raises(user_errors.UserNotFoundError):
                self.metrics_service.get_average_bookings_per_user("admin@inno.ru")

        mock_get_user.assert_called_once_with("admin@inno.ru")
        mock_assert_admin.assert_not_called()
        mock_get_all_users.assert_not_called()
        mock_get_user_bookings.assert_not_called()

    def test__get_average_bookings_per_user__non_admin(self) -> None:
        """Attempt to get average bookings per user from non-admin account."""
        app.dependency_overrides[get_current_user] = lambda: "user@inno.ru"

        mock_admin = create_mock_user()

        with (
            patch.object(
                UsersAdapter, "get_user", return_value=mock_admin
            ) as mock_get_user,
            patch.object(
                UsersAdapter,
                "assert_user_is_admin",
                side_effect=user_errors.AdminRoleRequiredError("user@inno.ru"),
            ) as mock_assert_admin,
            patch.object(UsersAdapter, "get_all_users") as mock_get_all_users,
            patch.object(MetricsAdapter, "get_user_bookings") as mock_get_user_bookings,
        ):
            with pytest.raises(user_errors.AdminRoleRequiredError):
                self.metrics_service.get_average_bookings_per_user("user@inno.ru")

        mock_get_user.assert_called_once_with("user@inno.ru")
        mock_assert_admin.assert_called_once_with(mock_admin)
        mock_get_all_users.assert_not_called()
        mock_get_user_bookings.assert_not_called()

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
        self, mock_events: list[MagicMock], ratio: float
    ) -> None:
        """Test to get offline events ratio from admin account."""
        app.dependency_overrides[get_current_user] = lambda: "admin@inno.ru"

        mock_admin = create_mock_user()

        with (
            patch.object(
                UsersAdapter, "get_user", return_value=mock_admin
            ) as mock_get_user,
            patch.object(UsersAdapter, "assert_user_is_admin") as mock_assert_admin,
            patch.object(
                EventsAdapter,
                "get_events_list",
                return_value=mock_events,
            ) as mock_get_events,
        ):
            result = self.metrics_service.get_offline_events_ratio("admin@inno.ru")

        mock_get_user.assert_called_once_with("admin@inno.ru")
        mock_assert_admin.assert_called_once_with(mock_admin)
        mock_get_events.assert_called_once_with()
        assert isinstance(result, OfflineEventsRatio)
        assert result.offline_events_ratio == ratio

    def test__get_offline_events_ratio__random_user(self) -> None:
        """Attempt to get offline events ratio from random email."""
        app.dependency_overrides[get_current_user] = lambda: "admin@inno.ru"

        with (
            patch.object(
                UsersAdapter,
                "get_user",
                side_effect=user_errors.UserNotFoundError("admin@inno.ru"),
            ) as mock_get_user,
            patch.object(UsersAdapter, "assert_user_is_admin") as mock_assert_admin,
            patch.object(EventsAdapter, "get_events_list") as mock_get_events,
        ):
            with pytest.raises(user_errors.UserNotFoundError):
                self.metrics_service.get_offline_events_ratio("admin@inno.ru")

        mock_get_user.assert_called_once_with("admin@inno.ru")
        mock_assert_admin.assert_not_called()
        mock_get_events.assert_not_called()

    def test__get_offline_events_ratio__non_admin(self) -> None:
        """Attempt to get offline events ratio from non-admin account."""
        app.dependency_overrides[get_current_user] = lambda: "user@inno.ru"

        mock_user = create_mock_user()

        with (
            patch.object(
                UsersAdapter, "get_user", return_value=mock_user
            ) as mock_get_user,
            patch.object(
                UsersAdapter,
                "assert_user_is_admin",
                side_effect=user_errors.AdminRoleRequiredError("user@inno.ru"),
            ) as mock_assert_admin,
            patch.object(EventsAdapter, "get_events_list") as mock_get_events,
        ):
            with pytest.raises(user_errors.AdminRoleRequiredError):
                self.metrics_service.get_offline_events_ratio("user@inno.ru")

        mock_get_user.assert_called_once_with("user@inno.ru")
        mock_assert_admin.assert_called_once_with(mock_user)
        mock_get_events.assert_not_called()
