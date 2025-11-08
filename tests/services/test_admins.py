from secrets import token_hex
from unittest.mock import MagicMock, patch

import pytest

import src.app.domain.exceptions.bookings as booking_errors
import src.app.domain.exceptions.events as event_errors
import src.app.domain.exceptions.users as user_errors
from src.app.auth import get_current_user
from src.app.db import get_db
from src.app.infrastructure.adapters.bookings_adapter import BookingsAdapter
from src.app.infrastructure.adapters.events_adapter import EventsAdapter
from src.app.infrastructure.adapters.users_adapter import UsersAdapter
from src.app.infrastructure.db_models.bookings import BookingDB
from src.app.infrastructure.db_models.events import EventDB
from src.app.infrastructure.db_models.users import UserDB
from src.app.main import app
from src.app.services.admins import AdminService
from src.app.services.models.bookings import Booking, EventParticipants
from src.app.services.models.common import Success
from src.app.services.models.users import User, UserCreate


def create_mock_event(**kwargs: object) -> MagicMock:
    """Create a mock EventDB object for testing."""
    mock_event = MagicMock(spec=EventDB)
    for key, value in kwargs.items():
        setattr(mock_event, key, value)
    return mock_event


def create_mock_booking(**kwargs: object) -> MagicMock:
    """Create a mock BookingDB object for testing."""
    mock_booking = MagicMock(spec=BookingDB)
    for key, value in kwargs.items():
        setattr(mock_booking, key, value)
    return mock_booking


def create_mock_user(**kwargs: object) -> MagicMock:
    """Create a mock UserDB object for testing."""
    mock_user = MagicMock(spec=UserDB)
    for key, value in kwargs.items():
        setattr(mock_user, key, value)
    return mock_user


class TestAdminService:
    """Test class for AdminService."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.mock_db = MagicMock()
        app.dependency_overrides[get_db] = lambda: self.mock_db
        self.admin_service = AdminService(self.mock_db)

    def test__get_all_users__success(self) -> None:
        """Test to get all the system users."""
        app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

        mock_user = create_mock_user()
        user_list = [
            create_mock_user(email="g.popov@inno.ru", name="Gleb"),
            create_mock_user(email="a.popov@inno.ru", name="Arthur"),
        ]

        with (
            patch.object(
                UsersAdapter, "get_user", return_value=mock_user
            ) as mock_get_user,
            patch.object(UsersAdapter, "assert_user_is_admin") as mock_assert_admin,
            patch.object(
                UsersAdapter,
                "get_all_users",
                return_value=user_list,
            ) as mock_get_all_users,
        ):
            result = self.admin_service.get_all_users("g.popov@inno.ru")

        mock_get_user.assert_called_once_with("g.popov@inno.ru")
        mock_assert_admin.assert_called_once_with(mock_user)
        mock_get_all_users.assert_called_once_with()
        assert isinstance(result, list)
        assert all(isinstance(event, User) for event in result)
        assert len(result) == len(user_list)
        assert result[0].email == "g.popov@inno.ru"
        assert result[1].email == "a.popov@inno.ru"
        assert result[0].name == "Gleb"
        assert result[1].name == "Arthur"

    def test__get_all_users__random_user(self) -> None:
        """Attempt to get all the system users from the random email."""
        app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

        with (
            patch.object(
                UsersAdapter,
                "get_user",
                side_effect=user_errors.UserNotFoundError("g.popov@inno.ru"),
            ) as mock_get_user,
            patch.object(UsersAdapter, "assert_user_is_admin") as mock_assert_admin,
            patch.object(UsersAdapter, "get_all_users") as mock_get_all_users,
            pytest.raises(user_errors.UserNotFoundError),
        ):
            self.admin_service.get_all_users("g.popov@inno.ru")

        mock_get_user.assert_called_once_with("g.popov@inno.ru")
        mock_assert_admin.assert_not_called()
        mock_get_all_users.assert_not_called()

    def test__get_all_users__not_admin(self) -> None:
        """Attempt to get all the system users from non-administrator."""
        app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

        mock_user = create_mock_user()

        with (
            patch.object(
                UsersAdapter, "get_user", return_value=mock_user
            ) as mock_get_user,
            patch.object(
                UsersAdapter,
                "assert_user_is_admin",
                side_effect=user_errors.AdminRoleRequiredError("g.popov@inno.ru"),
            ) as mock_assert_admin,
            patch.object(UsersAdapter, "get_all_users") as mock_get_all_users,
            pytest.raises(user_errors.AdminRoleRequiredError),
        ):
            self.admin_service.get_all_users("g.popov@inno.ru")

        mock_get_user.assert_called_once_with("g.popov@inno.ru")
        mock_assert_admin.assert_called_once_with(mock_user)
        mock_get_all_users.assert_not_called()

    def test__create_user__success(self) -> None:
        """Test to create user from admin account."""
        app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

        new_user = UserCreate(
            email="a.popov@inno.ru", name="Arthur", password=token_hex(16)
        )
        mock_user = create_mock_user()

        with (
            patch.object(
                UsersAdapter, "get_user", return_value=mock_user
            ) as mock_get_user,
            patch.object(UsersAdapter, "assert_user_is_admin") as mock_assert_admin,
            patch.object(
                UsersAdapter, "validate_user_email"
            ) as mock_validate_user_email,
            patch.object(UsersAdapter, "validate_user_name") as mock_validate_user_name,
            patch.object(
                UsersAdapter, "validate_password_lenght"
            ) as mock_validate_password_lenght,
            patch.object(
                UsersAdapter, "create_user", return_value=mock_user
            ) as mock_create_user,
        ):
            result = self.admin_service.create_user(new_user, "g.popov@inno.ru")

        mock_get_user.assert_called_once_with("g.popov@inno.ru")
        mock_assert_admin.assert_called_once_with(mock_user)
        mock_validate_user_email.assert_called_once_with(new_user.email)
        mock_validate_user_name.assert_called_once_with(new_user.name)
        mock_validate_password_lenght.assert_called_once_with(new_user.password)
        mock_create_user.assert_called_once_with(
            new_user.email, new_user.name, new_user.password
        )
        self.mock_db.commit.assert_called_once()
        assert isinstance(result, Success)

    def test__create_user__random_user(self) -> None:
        """Attempt to create user from the random email."""
        app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

        new_user = UserCreate(
            email="a.popov@inno.ru", name="Arthur", password=token_hex(16)
        )

        with (
            patch.object(
                UsersAdapter,
                "get_user",
                side_effect=user_errors.UserNotFoundError("g.popov@inno.ru"),
            ) as mock_get_user,
            patch.object(UsersAdapter, "assert_user_is_admin") as mock_assert_admin,
            patch.object(
                UsersAdapter, "validate_user_email"
            ) as mock_validate_user_email,
            patch.object(UsersAdapter, "validate_user_name") as mock_validate_user_name,
            patch.object(
                UsersAdapter, "validate_password_lenght"
            ) as mock_validate_password_lenght,
            patch.object(UsersAdapter, "create_user") as mock_create_user,
            pytest.raises(user_errors.UserNotFoundError),
        ):
            self.admin_service.create_user(new_user, "g.popov@inno.ru")

        mock_get_user.assert_called_once_with("g.popov@inno.ru")
        mock_assert_admin.assert_not_called()
        mock_validate_user_email.assert_not_called()
        mock_validate_user_name.assert_not_called()
        mock_validate_password_lenght.assert_not_called()
        mock_create_user.assert_not_called()
        self.mock_db.commit.assert_not_called()

    def test__create_user__non_admin(self) -> None:
        """Attempt to create user from non-admin."""
        app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

        new_user = UserCreate(
            email="a.popov@inno.ru", name="Arthur", password=token_hex(16)
        )
        mock_user = create_mock_user()

        with (
            patch.object(
                UsersAdapter, "get_user", return_value=mock_user
            ) as mock_get_user,
            patch.object(
                UsersAdapter,
                "assert_user_is_admin",
                side_effect=user_errors.AdminRoleRequiredError("g.popov@inno.ru"),
            ) as mock_assert_admin,
            patch.object(
                UsersAdapter, "validate_user_email"
            ) as mock_validate_user_email,
            patch.object(UsersAdapter, "validate_user_name") as mock_validate_user_name,
            patch.object(
                UsersAdapter, "validate_password_lenght"
            ) as mock_validate_password_lenght,
            patch.object(
                UsersAdapter, "create_user", return_value=mock_user
            ) as mock_create_user,
            pytest.raises(user_errors.AdminRoleRequiredError),
        ):
            self.admin_service.create_user(new_user, "g.popov@inno.ru")

        mock_get_user.assert_called_once_with("g.popov@inno.ru")
        mock_assert_admin.assert_called_once_with(mock_user)
        mock_validate_user_email.assert_not_called()
        mock_validate_user_name.assert_not_called()
        mock_validate_password_lenght.assert_not_called()
        mock_create_user.assert_not_called()
        self.mock_db.commit.assert_not_called()

    def test__create_user__invalid_email(self) -> None:
        """Attempt to create user with invalid email from admin account."""
        app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

        new_user = UserCreate(email="a.popov", name="Arthur", password=token_hex(16))
        mock_user = create_mock_user()

        with (
            patch.object(
                UsersAdapter, "get_user", return_value=mock_user
            ) as mock_get_user,
            patch.object(UsersAdapter, "assert_user_is_admin") as mock_assert_admin,
            patch.object(
                UsersAdapter,
                "validate_user_email",
                side_effect=user_errors.EmailFormatError,
            ) as mock_validate_user_email,
            patch.object(UsersAdapter, "validate_user_name") as mock_validate_user_name,
            patch.object(
                UsersAdapter, "validate_password_lenght"
            ) as mock_validate_password_lenght,
            patch.object(
                UsersAdapter, "create_user", return_value=mock_user
            ) as mock_create_user,
            pytest.raises(user_errors.EmailFormatError),
        ):
            self.admin_service.create_user(new_user, "g.popov@inno.ru")

        mock_get_user.assert_called_once_with("g.popov@inno.ru")
        mock_assert_admin.assert_called_once_with(mock_user)
        mock_validate_user_email.assert_called_once_with(new_user.email)
        mock_validate_user_name.assert_not_called()
        mock_validate_password_lenght.assert_not_called()
        mock_create_user.assert_not_called()
        self.mock_db.commit.assert_not_called()

    def test__create_user__invalid_name(self) -> None:
        """Attempt to create user with invalid name from admin account."""
        app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

        new_user = UserCreate(email="a.popov@inno.ru", name="", password=token_hex(16))
        mock_user = create_mock_user()

        with (
            patch.object(
                UsersAdapter, "get_user", return_value=mock_user
            ) as mock_get_user,
            patch.object(UsersAdapter, "assert_user_is_admin") as mock_assert_admin,
            patch.object(
                UsersAdapter, "validate_user_email"
            ) as mock_validate_user_email,
            patch.object(
                UsersAdapter,
                "validate_user_name",
                side_effect=user_errors.NameFormatError,
            ) as mock_validate_user_name,
            patch.object(
                UsersAdapter, "validate_password_lenght"
            ) as mock_validate_password_lenght,
            patch.object(
                UsersAdapter, "create_user", return_value=mock_user
            ) as mock_create_user,
            pytest.raises(user_errors.NameFormatError),
        ):
            self.admin_service.create_user(new_user, "g.popov@inno.ru")

        mock_get_user.assert_called_once_with("g.popov@inno.ru")
        mock_assert_admin.assert_called_once_with(mock_user)
        mock_validate_user_email.assert_called_once_with(new_user.email)
        mock_validate_user_name.assert_called_once_with(new_user.name)
        mock_validate_password_lenght.assert_not_called()
        mock_create_user.assert_not_called()
        self.mock_db.commit.assert_not_called()

    def test__create_user__weak_password(self) -> None:
        """Attempt to create user with too short password from admin account."""
        app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

        new_user = UserCreate(email="a.popov@inno.ru", name="Arthur", password="")
        mock_user = create_mock_user()

        with (
            patch.object(
                UsersAdapter, "get_user", return_value=mock_user
            ) as mock_get_user,
            patch.object(UsersAdapter, "assert_user_is_admin") as mock_assert_admin,
            patch.object(
                UsersAdapter, "validate_user_email"
            ) as mock_validate_user_email,
            patch.object(UsersAdapter, "validate_user_name") as mock_validate_user_name,
            patch.object(
                UsersAdapter,
                "validate_password_lenght",
                side_effect=user_errors.WeakPasswordError,
            ) as mock_validate_password_lenght,
            patch.object(
                UsersAdapter, "create_user", return_value=mock_user
            ) as mock_create_user,
            pytest.raises(user_errors.WeakPasswordError),
        ):
            self.admin_service.create_user(new_user, "g.popov@inno.ru")

        mock_get_user.assert_called_once_with("g.popov@inno.ru")
        mock_assert_admin.assert_called_once_with(mock_user)
        mock_validate_user_email.assert_called_once_with(new_user.email)
        mock_validate_user_name.assert_called_once_with(new_user.name)
        mock_validate_password_lenght.assert_called_once_with(new_user.password)
        mock_create_user.assert_not_called()
        self.mock_db.commit.assert_not_called()

    def test__create_user__user_exists(self) -> None:
        """Attempt to create a user that already exists from admin account."""
        app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

        new_user = UserCreate(
            email="g.popov@inno.ru", name="Gleb", password=token_hex(16)
        )
        mock_user = create_mock_user()

        with (
            patch.object(
                UsersAdapter, "get_user", return_value=mock_user
            ) as mock_get_user,
            patch.object(UsersAdapter, "assert_user_is_admin") as mock_assert_admin,
            patch.object(
                UsersAdapter, "validate_user_email"
            ) as mock_validate_user_email,
            patch.object(UsersAdapter, "validate_user_name") as mock_validate_user_name,
            patch.object(
                UsersAdapter, "validate_password_lenght"
            ) as mock_validate_password_lenght,
            patch.object(
                UsersAdapter,
                "create_user",
                side_effect=user_errors.UserExistsError(new_user.email),
            ) as mock_create_user,
            pytest.raises(user_errors.UserExistsError),
        ):
            self.admin_service.create_user(new_user, "g.popov@inno.ru")

        mock_get_user.assert_called_once_with("g.popov@inno.ru")
        mock_assert_admin.assert_called_once_with(mock_user)
        mock_validate_user_email.assert_called_once_with(new_user.email)
        mock_validate_user_name.assert_called_once_with(new_user.name)
        mock_validate_password_lenght.assert_called_once_with(new_user.password)
        mock_create_user.assert_called_once_with(
            new_user.email, new_user.name, new_user.password
        )
        self.mock_db.commit.assert_not_called()

    def test__delete_user__success(self) -> None:
        """Test to delete user from admin account."""
        app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

        mock_admin = create_mock_user(email="g.popov@inno.ru")
        mock_user = create_mock_user(email="a.popov@inno.ru")

        with (
            patch.object(
                UsersAdapter,
                "get_user",
                side_effect=[mock_admin, mock_user],
            ) as mock_get_user,
            patch.object(UsersAdapter, "assert_user_is_admin") as mock_assert_admin,
            patch.object(UsersAdapter, "delete_user") as mock_delete_user,
        ):
            result = self.admin_service.delete_user(
                "a.popov@inno.ru", "g.popov@inno.ru"
            )

        assert mock_get_user.call_count == 1 + 1
        mock_get_user.assert_any_call("g.popov@inno.ru")
        mock_get_user.assert_any_call("a.popov@inno.ru")
        mock_assert_admin.assert_called_once_with(mock_admin)
        mock_delete_user.assert_called_once_with(mock_user)
        self.mock_db.commit.assert_called_once()
        assert isinstance(result, Success)

    def test__delete_user__random_user(self) -> None:
        """Attempt to delete user from random email."""
        app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

        with (
            patch.object(
                UsersAdapter,
                "get_user",
                side_effect=user_errors.UserNotFoundError("g.popov@inno.ru"),
            ) as mock_get_user,
            patch.object(UsersAdapter, "assert_user_is_admin") as mock_assert_admin,
            patch.object(UsersAdapter, "delete_user") as mock_delete_user,
            pytest.raises(user_errors.UserNotFoundError),
        ):
            self.admin_service.delete_user("a.popov@inno.ru", "g.popov@inno.ru")

        mock_get_user.assert_called_once_with("g.popov@inno.ru")
        mock_assert_admin.assert_not_called()
        mock_delete_user.assert_not_called()

    def test__delete_user__non_admin(self) -> None:
        """Attempt to delete user from non-admin account."""
        app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

        mock_admin = create_mock_user()

        with (
            patch.object(
                UsersAdapter, "get_user", return_value=mock_admin
            ) as mock_get_user,
            patch.object(
                UsersAdapter,
                "assert_user_is_admin",
                side_effect=user_errors.AdminRoleRequiredError("g.popov@inno.ru"),
            ) as mock_assert_admin,
            patch.object(UsersAdapter, "delete_user") as mock_delete_user,
            pytest.raises(user_errors.AdminRoleRequiredError),
        ):
            self.admin_service.delete_user("a.popov@inno.ru", "g.popov@inno.ru")

        mock_get_user.assert_called_once_with("g.popov@inno.ru")
        mock_assert_admin.assert_called_once_with(mock_admin)
        mock_delete_user.assert_not_called()

    def test__delete_user__not_found(self) -> None:
        """Attempts to delete user that does not exist from admin account."""
        app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

        mock_admin = create_mock_user()

        with (
            patch.object(
                UsersAdapter,
                "get_user",
                side_effect=[
                    mock_admin,
                    user_errors.UserNotFoundError("a.popov@inno.ru"),
                ],
            ) as mock_get_user,
            patch.object(UsersAdapter, "assert_user_is_admin") as mock_assert_admin,
            patch.object(UsersAdapter, "delete_user") as mock_delete_user,
            pytest.raises(user_errors.UserNotFoundError),
        ):
            self.admin_service.delete_user("a.popov@inno.ru", "g.popov@inno.ru")

        assert mock_get_user.call_count == 1 + 1
        mock_get_user.assert_any_call("g.popov@inno.ru")
        mock_get_user.assert_any_call("a.popov@inno.ru")
        mock_assert_admin.assert_called_once_with(mock_admin)
        mock_delete_user.assert_not_called()
        self.mock_db.commit.assert_not_called()

    def test__delete_event__success(self) -> None:
        """Test to delete event from admin account."""
        app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

        mock_admin = create_mock_user()
        mock_event = create_mock_event()

        with (
            patch.object(
                UsersAdapter, "get_user", return_value=mock_admin
            ) as mock_get_user,
            patch.object(UsersAdapter, "assert_user_is_admin") as mock_assert_admin,
            patch.object(
                EventsAdapter,
                "get_event",
                return_value=mock_event,
            ) as mock_get_event,
            patch.object(EventsAdapter, "delete_event") as mock_delete_event,
        ):
            result = self.admin_service.delete_event(1, "g.popov@inno.ru")

        mock_get_user.assert_called_once_with("g.popov@inno.ru")
        mock_assert_admin.assert_called_once_with(mock_admin)
        mock_get_event.assert_called_once_with(1)
        mock_delete_event.assert_called_once_with(mock_event)
        self.mock_db.commit.assert_called_once()
        assert isinstance(result, Success)

    def test__delete_event__random_user(self) -> None:
        """Attempt to delete event from random email."""
        app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

        with (
            patch.object(
                UsersAdapter,
                "get_user",
                side_effect=user_errors.UserNotFoundError("g.popov@inno.ru"),
            ) as mock_get_user,
            patch.object(UsersAdapter, "assert_user_is_admin") as mock_assert_admin,
            patch.object(EventsAdapter, "get_event") as mock_get_event,
            pytest.raises(user_errors.UserNotFoundError),
        ):
            self.admin_service.delete_event(1, "g.popov@inno.ru")

        mock_get_user.assert_called_once_with("g.popov@inno.ru")
        mock_assert_admin.assert_not_called()
        mock_get_event.assert_not_called()
        self.mock_db.commit.assert_not_called()

    def test__delete_event__non_admin(self) -> None:
        """Attempt to delete event from non-admin account."""
        app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

        mock_admin = create_mock_user()

        with (
            patch.object(
                UsersAdapter, "get_user", return_value=mock_admin
            ) as mock_get_user,
            patch.object(
                UsersAdapter,
                "assert_user_is_admin",
                side_effect=user_errors.AdminRoleRequiredError("g.popov@inno.ru"),
            ) as mock_assert_admin,
            patch.object(EventsAdapter, "get_event") as mock_get_event,
            pytest.raises(user_errors.AdminRoleRequiredError),
        ):
            self.admin_service.delete_event(1, "g.popov@inno.ru")

        mock_get_user.assert_called_once_with("g.popov@inno.ru")
        mock_assert_admin.assert_called_once_with(mock_admin)
        mock_get_event.assert_not_called()
        self.mock_db.commit.assert_not_called()

    def test__delete_event__not_found(self) -> None:
        """Attempt to delete non-existent event from admin account."""
        app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

        mock_admin = create_mock_user()

        with (
            patch.object(
                UsersAdapter, "get_user", return_value=mock_admin
            ) as mock_get_user,
            patch.object(UsersAdapter, "assert_user_is_admin") as mock_assert_admin,
            patch.object(
                EventsAdapter,
                "get_event",
                side_effect=event_errors.EventNotFoundError(1),
            ) as mock_get_event,
            pytest.raises(event_errors.EventNotFoundError),
        ):
            self.admin_service.delete_event(1, "g.popov@inno.ru")

        mock_get_user.assert_called_once_with("g.popov@inno.ru")
        mock_assert_admin.assert_called_once_with(mock_admin)
        mock_get_event.assert_called_once_with(1)
        self.mock_db.commit.assert_not_called()

    def test__create_user_booking__success(self) -> None:
        """Test to create booking for another user from admin account."""
        app.dependency_overrides[get_current_user] = lambda: "admin@inno.ru"

        mock_admin = create_mock_user()
        mock_guest = create_mock_user()
        mock_event = create_mock_event()

        with (
            patch.object(
                UsersAdapter,
                "get_user",
                side_effect=[mock_admin, mock_guest],
            ) as mock_get_user,
            patch.object(UsersAdapter, "assert_user_is_admin") as mock_assert_admin,
            patch.object(
                EventsAdapter,
                "get_event",
                return_value=mock_event,
            ) as mock_get_event,
            patch.object(
                BookingsAdapter, "assert_seats_available"
            ) as mock_assert_seats,
            patch.object(BookingsAdapter, "create_booking") as mock_create_booking,
        ):
            result = self.admin_service.create_user_booking(
                5, "guest@inno.ru", "admin@inno.ru"
            )

        assert mock_get_user.call_count == 1 + 1
        mock_get_user.assert_any_call("admin@inno.ru")
        mock_get_user.assert_any_call("guest@inno.ru")
        mock_assert_admin.assert_called_once_with(mock_admin)
        mock_get_event.assert_called_once_with(5)
        mock_assert_seats.assert_called_once_with(mock_event)
        mock_create_booking.assert_called_once_with(mock_event, mock_guest)
        self.mock_db.commit.assert_called_once()
        assert isinstance(result, Success)

    def test__create_user_booking__random_user(self) -> None:
        """Attempt to create booking from random email."""
        app.dependency_overrides[get_current_user] = lambda: "admin@inno.ru"

        with (
            patch.object(
                UsersAdapter,
                "get_user",
                side_effect=user_errors.UserNotFoundError("admin@inno.ru"),
            ) as mock_get_user,
            patch.object(UsersAdapter, "assert_user_is_admin") as mock_assert_admin,
            patch.object(EventsAdapter, "get_event") as mock_get_event,
            patch.object(
                BookingsAdapter, "assert_seats_available"
            ) as mock_assert_seats,
            patch.object(BookingsAdapter, "create_booking") as mock_create_booking,
            pytest.raises(user_errors.UserNotFoundError),
        ):
            self.admin_service.create_user_booking(5, "guest@inno.ru", "admin@inno.ru")

        mock_get_user.assert_called_once_with("admin@inno.ru")
        mock_assert_admin.assert_not_called()
        mock_get_event.assert_not_called()
        mock_assert_seats.assert_not_called()
        mock_create_booking.assert_not_called()

    def test__create_user_booking__non_admin(self) -> None:
        """Attempt to create booking from non-admin account."""
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
            patch.object(EventsAdapter, "get_event") as mock_get_event,
            patch.object(
                BookingsAdapter, "assert_seats_available"
            ) as mock_assert_seats,
            patch.object(BookingsAdapter, "create_booking") as mock_create_booking,
            pytest.raises(user_errors.AdminRoleRequiredError),
        ):
            self.admin_service.create_user_booking(5, "guest@inno.ru", "user@inno.ru")

        mock_get_user.assert_called_once_with("user@inno.ru")
        mock_assert_admin.assert_called_once_with(mock_user)
        mock_get_event.assert_not_called()
        mock_assert_seats.assert_not_called()
        mock_create_booking.assert_not_called()

    def test__create_user_booking__guest_not_found(self) -> None:
        """Attempt to create booking for non-existent guest."""
        app.dependency_overrides[get_current_user] = lambda: "admin@inno.ru"

        mock_admin = create_mock_user()

        with (
            patch.object(
                UsersAdapter,
                "get_user",
                side_effect=[
                    mock_admin,
                    user_errors.UserNotFoundError("guest@inno.ru"),
                ],
            ) as mock_get_user,
            patch.object(UsersAdapter, "assert_user_is_admin") as mock_assert_admin,
            patch.object(EventsAdapter, "get_event") as mock_get_event,
            patch.object(
                BookingsAdapter, "assert_seats_available"
            ) as mock_assert_seats,
            patch.object(BookingsAdapter, "create_booking") as mock_create_booking,
            pytest.raises(user_errors.UserNotFoundError),
        ):
            self.admin_service.create_user_booking(5, "guest@inno.ru", "admin@inno.ru")

        assert mock_get_user.call_count == 1 + 1
        mock_get_user.assert_any_call("guest@inno.ru")
        mock_get_user.assert_any_call("admin@inno.ru")
        mock_assert_admin.assert_called_once_with(mock_admin)
        mock_get_event.assert_not_called()
        mock_assert_seats.assert_not_called()
        mock_create_booking.assert_not_called()
        self.mock_db.commit.assert_not_called()

    def test__create_user_booking__event_not_found(self) -> None:
        """Attempt to create booking for non-existent event."""
        app.dependency_overrides[get_current_user] = lambda: "admin@inno.ru"

        mock_admin = create_mock_user()
        mock_guest = create_mock_user()

        with (
            patch.object(
                UsersAdapter,
                "get_user",
                side_effect=[mock_admin, mock_guest],
            ) as mock_get_user,
            patch.object(UsersAdapter, "assert_user_is_admin") as mock_assert_admin,
            patch.object(
                EventsAdapter,
                "get_event",
                side_effect=event_errors.EventNotFoundError(5),
            ) as mock_get_event,
            patch.object(
                BookingsAdapter, "assert_seats_available"
            ) as mock_assert_seats,
            patch.object(BookingsAdapter, "create_booking") as mock_create_booking,
            pytest.raises(event_errors.EventNotFoundError),
        ):
            self.admin_service.create_user_booking(5, "guest@inno.ru", "admin@inno.ru")

        assert mock_get_user.call_count == 1 + 1
        mock_get_user.assert_any_call("guest@inno.ru")
        mock_get_user.assert_any_call("admin@inno.ru")
        mock_assert_admin.assert_called_once_with(mock_admin)
        mock_get_event.assert_called_once_with(5)
        mock_assert_seats.assert_not_called()
        mock_create_booking.assert_not_called()
        self.mock_db.commit.assert_not_called()

    def test__create_user_booking__event_full(self) -> None:
        """Attempt to create booking when event is full."""
        app.dependency_overrides[get_current_user] = lambda: "admin@inno.ru"

        mock_admin = create_mock_user()
        mock_guest = create_mock_user()
        mock_event = create_mock_event()

        with (
            patch.object(
                UsersAdapter,
                "get_user",
                side_effect=[mock_admin, mock_guest],
            ) as mock_get_user,
            patch.object(UsersAdapter, "assert_user_is_admin") as mock_assert_admin,
            patch.object(
                EventsAdapter,
                "get_event",
                return_value=mock_event,
            ) as mock_get_event,
            patch.object(
                BookingsAdapter,
                "assert_seats_available",
                side_effect=booking_errors.EventFullError(5),
            ) as mock_assert_seats,
            patch.object(BookingsAdapter, "create_booking") as mock_create_booking,
            pytest.raises(booking_errors.EventFullError),
        ):
            self.admin_service.create_user_booking(5, "guest@inno.ru", "admin@inno.ru")

        assert mock_get_user.call_count == 1 + 1
        mock_get_user.assert_any_call("guest@inno.ru")
        mock_get_user.assert_any_call("admin@inno.ru")
        mock_assert_admin.assert_called_once_with(mock_admin)
        mock_get_event.assert_called_once_with(5)
        mock_assert_seats.assert_called_once_with(mock_event)
        mock_create_booking.assert_not_called()
        self.mock_db.commit.assert_not_called()

    def test__delete_user_booking__success(self) -> None:
        """Test to delete user booking from admin account."""
        app.dependency_overrides[get_current_user] = lambda: "admin@inno.ru"

        mock_admin = create_mock_user()
        mock_guest = create_mock_user()
        mock_event = create_mock_event()

        with (
            patch.object(
                UsersAdapter,
                "get_user",
                side_effect=[mock_admin, mock_guest],
            ) as mock_get_user,
            patch.object(UsersAdapter, "assert_user_is_admin") as mock_assert_admin,
            patch.object(
                EventsAdapter,
                "get_event",
                return_value=mock_event,
            ) as mock_get_event,
            patch.object(BookingsAdapter, "delete_booking") as mock_delete_booking,
        ):
            result = self.admin_service.delete_user_booking(
                5, "guest@inno.ru", "admin@inno.ru"
            )

        assert mock_get_user.call_count == 1 + 1
        mock_get_user.assert_any_call("admin@inno.ru")
        mock_get_user.assert_any_call("guest@inno.ru")
        mock_assert_admin.assert_called_once_with(mock_admin)
        mock_get_event.assert_called_once_with(5)
        mock_delete_booking.assert_called_once_with(mock_event, mock_guest)
        self.mock_db.commit.assert_called_once()
        assert isinstance(result, Success)

    def test__delete_user_booking__random_user(self) -> None:
        """Attempt to delete user booking from random email."""
        app.dependency_overrides[get_current_user] = lambda: "admin@inno.ru"

        with (
            patch.object(
                UsersAdapter,
                "get_user",
                side_effect=user_errors.UserNotFoundError("admin@inno.ru"),
            ) as mock_get_user,
            patch.object(UsersAdapter, "assert_user_is_admin") as mock_assert_admin,
            patch.object(EventsAdapter, "get_event") as mock_get_event,
            patch.object(BookingsAdapter, "delete_booking") as mock_delete_booking,
            pytest.raises(user_errors.UserNotFoundError),
        ):
            self.admin_service.delete_user_booking(5, "guest@inno.ru", "admin@inno.ru")

        mock_get_user.assert_called_once_with("admin@inno.ru")
        mock_assert_admin.assert_not_called()
        mock_get_event.assert_not_called()
        mock_delete_booking.assert_not_called()

    def test__delete_user_booking__non_admin(self) -> None:
        """Attempt to delete user booking from non-admin account."""
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
            patch.object(EventsAdapter, "get_event") as mock_get_event,
            patch.object(BookingsAdapter, "delete_booking") as mock_delete_booking,
            pytest.raises(user_errors.AdminRoleRequiredError),
        ):
            self.admin_service.delete_user_booking(5, "guest@inno.ru", "user@inno.ru")

        mock_get_user.assert_called_once_with("user@inno.ru")
        mock_assert_admin.assert_called_once_with(mock_user)
        mock_get_event.assert_not_called()
        mock_delete_booking.assert_not_called()

    def test__delete_user_booking__guest_not_found(self) -> None:
        """Attempt to delete booking for non-existent guest."""
        app.dependency_overrides[get_current_user] = lambda: "admin@inno.ru"

        mock_admin = create_mock_user()

        with (
            patch.object(
                UsersAdapter,
                "get_user",
                side_effect=[
                    mock_admin,
                    user_errors.UserNotFoundError("guest@inno.ru"),
                ],
            ) as mock_get_user,
            patch.object(UsersAdapter, "assert_user_is_admin") as mock_assert_admin,
            patch.object(EventsAdapter, "get_event") as mock_get_event,
            patch.object(BookingsAdapter, "delete_booking") as mock_delete_booking,
            pytest.raises(user_errors.UserNotFoundError),
        ):
            self.admin_service.delete_user_booking(5, "guest@inno.ru", "admin@inno.ru")

        assert mock_get_user.call_count == 1 + 1
        mock_get_user.assert_any_call("admin@inno.ru")
        mock_get_user.assert_any_call("guest@inno.ru")
        mock_assert_admin.assert_called_once_with(mock_admin)
        mock_get_event.assert_not_called()
        mock_delete_booking.assert_not_called()
        self.mock_db.commit.assert_not_called()

    def test__delete_user_booking__event_not_found(self) -> None:
        """Attempt to delete booking for non-existent event."""
        app.dependency_overrides[get_current_user] = lambda: "admin@inno.ru"

        mock_admin = create_mock_user()
        mock_guest = create_mock_user()

        with (
            patch.object(
                UsersAdapter,
                "get_user",
                side_effect=[mock_admin, mock_guest],
            ) as mock_get_user,
            patch.object(UsersAdapter, "assert_user_is_admin") as mock_assert_admin,
            patch.object(
                EventsAdapter,
                "get_event",
                side_effect=event_errors.EventNotFoundError(5),
            ) as mock_get_event,
            patch.object(BookingsAdapter, "delete_booking") as mock_delete_booking,
            pytest.raises(event_errors.EventNotFoundError),
        ):
            self.admin_service.delete_user_booking(5, "guest@inno.ru", "admin@inno.ru")

        assert mock_get_user.call_count == 1 + 1
        mock_get_user.assert_any_call("admin@inno.ru")
        mock_get_user.assert_any_call("guest@inno.ru")
        mock_assert_admin.assert_called_once_with(mock_admin)
        mock_get_event.assert_called_once_with(5)
        mock_delete_booking.assert_not_called()
        self.mock_db.commit.assert_not_called()

    def test__get_event_participants__success(self) -> None:
        """Test to get event participants from admin account."""
        app.dependency_overrides[get_current_user] = lambda: "admin@inno.ru"

        mock_admin = create_mock_user()
        mock_event = create_mock_event()
        participants_emails = ["user1@inno.ru", "user2@inno.ru", "user3@inno.ru"]

        with (
            patch.object(
                UsersAdapter, "get_user", return_value=mock_admin
            ) as mock_get_user,
            patch.object(UsersAdapter, "assert_user_is_admin") as mock_assert_admin,
            patch.object(
                EventsAdapter,
                "get_event",
                return_value=mock_event,
            ) as mock_get_event,
            patch.object(
                BookingsAdapter,
                "get_event_participants",
                return_value=participants_emails,
            ) as mock_get_participants,
        ):
            result = self.admin_service.get_event_participants(5, "admin@inno.ru")

        mock_get_user.assert_called_once_with("admin@inno.ru")
        mock_assert_admin.assert_called_once_with(mock_admin)
        mock_get_event.assert_called_once_with(5)
        mock_get_participants.assert_called_once_with(mock_event)
        assert isinstance(result, EventParticipants)
        assert result.participants_emails == participants_emails

    def test__get_event_participants__random_user(self) -> None:
        """Attempt to get event participants from random email."""
        app.dependency_overrides[get_current_user] = lambda: "admin@inno.ru"

        with (
            patch.object(
                UsersAdapter,
                "get_user",
                side_effect=user_errors.UserNotFoundError("admin@inno.ru"),
            ) as mock_get_user,
            patch.object(UsersAdapter, "assert_user_is_admin") as mock_assert_admin,
            patch.object(EventsAdapter, "get_event") as mock_get_event,
            patch.object(
                BookingsAdapter, "get_event_participants"
            ) as mock_get_participants,
            pytest.raises(user_errors.UserNotFoundError),
        ):
            self.admin_service.get_event_participants(5, "admin@inno.ru")

        mock_get_user.assert_called_once_with("admin@inno.ru")
        mock_assert_admin.assert_not_called()
        mock_get_event.assert_not_called()
        mock_get_participants.assert_not_called()

    def test__get_event_participants__non_admin(self) -> None:
        """Attempt to get event participants from non-admin account."""
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
            patch.object(EventsAdapter, "get_event") as mock_get_event,
            patch.object(
                BookingsAdapter, "get_event_participants"
            ) as mock_get_participants,
            pytest.raises(user_errors.AdminRoleRequiredError),
        ):
            self.admin_service.get_event_participants(5, "user@inno.ru")

        mock_get_user.assert_called_once_with("user@inno.ru")
        mock_assert_admin.assert_called_once_with(mock_user)
        mock_get_event.assert_not_called()
        mock_get_participants.assert_not_called()

    def test__get_event_participants__event_not_found(self) -> None:
        """Attempt to get participants for non-existent event."""
        app.dependency_overrides[get_current_user] = lambda: "admin@inno.ru"

        mock_admin = create_mock_user()

        with (
            patch.object(
                UsersAdapter, "get_user", return_value=mock_admin
            ) as mock_get_user,
            patch.object(UsersAdapter, "assert_user_is_admin") as mock_assert_admin,
            patch.object(
                EventsAdapter,
                "get_event",
                side_effect=event_errors.EventNotFoundError(5),
            ) as mock_get_event,
            patch.object(
                BookingsAdapter, "get_event_participants"
            ) as mock_get_participants,
            pytest.raises(event_errors.EventNotFoundError),
        ):
            self.admin_service.get_event_participants(5, "admin@inno.ru")

        mock_get_user.assert_called_once_with("admin@inno.ru")
        mock_assert_admin.assert_called_once_with(mock_admin)
        mock_get_event.assert_called_once_with(5)
        mock_get_participants.assert_not_called()

    def test__get_bookings__success(self) -> None:
        """Test to get all bookings from admin account."""
        app.dependency_overrides[get_current_user] = lambda: "admin@inno.ru"

        mock_admin = create_mock_user()
        mock_bookings = [
            create_mock_booking(event_id=1, user_email="user1@inno.ru"),
            create_mock_booking(event_id=2, user_email="user2@inno.ru"),
            create_mock_booking(event_id=1, user_email="user3@inno.ru"),
        ]

        with (
            patch.object(
                UsersAdapter, "get_user", return_value=mock_admin
            ) as mock_get_user,
            patch.object(UsersAdapter, "assert_user_is_admin") as mock_assert_admin,
            patch.object(
                BookingsAdapter,
                "get_all_bookings",
                return_value=mock_bookings,
            ) as mock_get_all_bookings,
        ):
            result = self.admin_service.get_bookings("admin@inno.ru")

        mock_get_user.assert_called_once_with("admin@inno.ru")
        mock_assert_admin.assert_called_once_with(mock_admin)
        mock_get_all_bookings.assert_called_once_with()
        assert isinstance(result, list)
        assert all(isinstance(event, Booking) for event in result)
        assert len(result) == len(mock_bookings)
        assert result[0].event_id == 1
        assert result[1].event_id == 1 + 1
        assert result[2].event_id == 1
        assert result[0].user_email == "user1@inno.ru"
        assert result[1].user_email == "user2@inno.ru"
        assert result[2].user_email == "user3@inno.ru"

    def test__get_bookings__random_user(self) -> None:
        """Attempt to get all bookings from random email."""
        app.dependency_overrides[get_current_user] = lambda: "admin@inno.ru"

        with (
            patch.object(
                UsersAdapter,
                "get_user",
                side_effect=user_errors.UserNotFoundError("admin@inno.ru"),
            ) as mock_get_user,
            patch.object(UsersAdapter, "assert_user_is_admin") as mock_assert_admin,
            patch.object(BookingsAdapter, "get_all_bookings") as mock_get_all_bookings,
            pytest.raises(user_errors.UserNotFoundError),
        ):
            self.admin_service.get_bookings("admin@inno.ru")

        mock_get_user.assert_called_once_with("admin@inno.ru")
        mock_assert_admin.assert_not_called()
        mock_get_all_bookings.assert_not_called()

    def test__get_bookings__non_admin(self) -> None:
        """Attempt to get all bookings from non-admin account."""
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
            patch.object(BookingsAdapter, "get_all_bookings") as mock_get_all_bookings,
            pytest.raises(user_errors.AdminRoleRequiredError),
        ):
            self.admin_service.get_bookings("user@inno.ru")

        mock_get_user.assert_called_once_with("user@inno.ru")
        mock_assert_admin.assert_called_once_with(mock_user)
        mock_get_all_bookings.assert_not_called()
