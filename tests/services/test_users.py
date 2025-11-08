from secrets import token_hex
from unittest.mock import MagicMock, patch

import pytest

import src.app.domain.exceptions.users as user_errors
from src.app.db import get_db
from src.app.infrastructure.adapters.users_adapter import UsersAdapter
from src.app.infrastructure.db_models.users import UserDB
from src.app.main import app
from src.app.services.models.users import AccessToken, UserCreate, UserLogin
from src.app.services.users import UserService


def create_mock_user(**kwargs: object) -> MagicMock:
    """Create a mock UserDB object for testing."""
    mock_user = MagicMock(spec=UserDB)
    for key, value in kwargs.items():
        setattr(mock_user, key, value)
    return mock_user


class TestUserService:
    """Test class for UserService."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.mock_db = MagicMock()
        app.dependency_overrides[get_db] = lambda: self.mock_db
        self.users_service = UserService(self.mock_db)

    def test__register__success(self) -> None:
        """Test successful user registration."""
        user_data = UserCreate(
            email="g.popov@inno.ru", name="Gleb", password=token_hex(16)
        )
        mock_user = create_mock_user()
        mock_token = token_hex(32)

        with (
            patch.object(UsersAdapter, "validate_user_email") as mock_validate_email,
            patch.object(UsersAdapter, "validate_user_name") as mock_validate_name,
            patch.object(
                UsersAdapter, "validate_password_lenght"
            ) as mock_validate_password,
            patch.object(
                UsersAdapter, "create_user", return_value=mock_user
            ) as mock_create_user,
            patch.object(
                UsersAdapter, "get_access_token", return_value=mock_token
            ) as mock_get_access_token,
        ):
            result = self.users_service.register(user_data)

        mock_validate_email.assert_called_once_with(user_data.email)
        mock_validate_name.assert_called_once_with(user_data.name)
        mock_validate_password.assert_called_once_with(user_data.password)
        mock_create_user.assert_called_once_with(
            user_data.email, user_data.name, user_data.password
        )
        mock_get_access_token.assert_called_once_with(mock_user)
        self.mock_db.commit.assert_called_once()

        assert isinstance(result, AccessToken)
        assert result.access_token == mock_token

    def test__register__invalid_email(self) -> None:
        """Attempt to register an account with an invalid email."""
        user_data = UserCreate(email="g.popov", name="Gleb", password=token_hex(16))

        with (
            patch.object(
                UsersAdapter,
                "validate_user_email",
                side_effect=user_errors.EmailFormatError,
            ) as mock_validate_email,
            patch.object(UsersAdapter, "validate_user_name") as mock_validate_name,
            patch.object(
                UsersAdapter, "validate_password_lenght"
            ) as mock_validate_password,
            patch.object(UsersAdapter, "create_user") as mock_create_user,
            patch.object(UsersAdapter, "get_access_token") as mock_get_access_token,
            pytest.raises(user_errors.EmailFormatError),
        ):
            self.users_service.register(user_data)

        mock_validate_email.assert_called_once_with(user_data.email)
        mock_validate_name.assert_not_called()
        mock_validate_password.assert_not_called()
        mock_create_user.assert_not_called()
        mock_get_access_token.assert_not_called()
        self.mock_db.commit.assert_not_called()

    def test__register__invalid_name(self) -> None:
        """Attempt to register an account with an invalid email."""
        user_data = UserCreate(
            email="g.popov@inno.ru", name=("Gleb" * 21), password=token_hex(16)
        )

        with (
            patch.object(UsersAdapter, "validate_user_email") as mock_validate_email,
            patch.object(
                UsersAdapter,
                "validate_user_name",
                side_effect=user_errors.NameFormatError,
            ) as mock_validate_name,
            patch.object(
                UsersAdapter, "validate_password_lenght"
            ) as mock_validate_password,
            patch.object(UsersAdapter, "create_user") as mock_create_user,
            patch.object(UsersAdapter, "get_access_token") as mock_get_access_token,
            pytest.raises(user_errors.NameFormatError),
        ):
            self.users_service.register(user_data)

        mock_validate_email.assert_called_once_with(user_data.email)
        mock_validate_name.assert_called_once_with(user_data.name)
        mock_validate_password.assert_not_called()
        mock_create_user.assert_not_called()
        mock_get_access_token.assert_not_called()
        self.mock_db.commit.assert_not_called()

    def test__register__invalid_password(self) -> None:
        """Attempt to register an account with an invalid password."""
        user_data = UserCreate(email="g.popov@inno.ru", name="Gleb", password="")

        with (
            patch.object(UsersAdapter, "validate_user_email") as mock_validate_email,
            patch.object(UsersAdapter, "validate_user_name") as mock_validate_name,
            patch.object(
                UsersAdapter,
                "validate_password_lenght",
                side_effect=user_errors.WeakPasswordError,
            ) as mock_validate_password,
            patch.object(UsersAdapter, "create_user") as mock_create_user,
            patch.object(UsersAdapter, "get_access_token") as mock_get_access_token,
            pytest.raises(user_errors.WeakPasswordError),
        ):
            self.users_service.register(user_data)

        mock_validate_email.assert_called_once_with(user_data.email)
        mock_validate_name.assert_called_once_with(user_data.name)
        mock_validate_password.assert_called_once_with(user_data.password)
        mock_create_user.assert_not_called()
        mock_get_access_token.assert_not_called()
        self.mock_db.commit.assert_not_called()

    def test__register__user_exists(self) -> None:
        """Attempt to register an account that already exists."""
        user_data = UserCreate(
            email="g.popov@inno.ru", name="Gleb", password=token_hex(16)
        )

        with (
            patch.object(UsersAdapter, "validate_user_email") as mock_validate_email,
            patch.object(UsersAdapter, "validate_user_name") as mock_validate_name,
            patch.object(
                UsersAdapter, "validate_password_lenght"
            ) as mock_validate_password,
            patch.object(
                UsersAdapter,
                "create_user",
                side_effect=user_errors.UserExistsError(user_data.email),
            ) as mock_create_user,
            patch.object(UsersAdapter, "get_access_token") as mock_get_access_token,
            pytest.raises(user_errors.UserExistsError),
        ):
            self.users_service.register(user_data)

        mock_validate_email.assert_called_once_with(user_data.email)
        mock_validate_name.assert_called_once_with(user_data.name)
        mock_validate_password.assert_called_once_with(user_data.password)
        mock_create_user.assert_called_once_with(
            user_data.email,
            user_data.name,
            user_data.password,
        )
        mock_get_access_token.assert_not_called()
        self.mock_db.commit.assert_not_called()

    def test__login__success(self) -> None:
        """Test successful user login."""
        user_data = UserLogin(email="g.popov@inno.ru", password=token_hex(16))

        mock_user = create_mock_user()
        mock_token = token_hex(32)

        with (
            patch.object(
                UsersAdapter, "get_user", return_value=mock_user
            ) as mock_get_user,
            patch.object(UsersAdapter, "verify_password") as mock_verify_password,
            patch.object(
                UsersAdapter,
                "get_access_token",
                return_value=mock_token,
            ) as mock_get_token,
        ):
            result = self.users_service.login(user_data)

        mock_get_user.assert_called_once_with(user_data.email)
        mock_verify_password.assert_called_once_with(mock_user, user_data.password)
        mock_get_token.assert_called_once_with(mock_user)
        assert isinstance(result, AccessToken)
        assert mock_token == result.access_token

    def test__login__random_email(self) -> None:
        """Attempt to login with incorrect email."""
        user_data = UserLogin(email="g.popov@inno.ru", password=token_hex(16))

        with (
            patch.object(
                UsersAdapter,
                "get_user",
                side_effect=user_errors.UserNotFoundError(user_data.email),
            ) as mock_get_user,
            patch.object(UsersAdapter, "verify_password") as mock_verify_password,
            patch.object(UsersAdapter, "get_access_token") as mock_get_token,
            pytest.raises(user_errors.UserNotFoundError),
        ):
            self.users_service.login(user_data)

        mock_get_user.assert_called_once_with(user_data.email)
        mock_verify_password.assert_not_called()
        mock_get_token.assert_not_called()

    def test__login__wrong_password(self) -> None:
        """Attempt to login with the wrong password."""
        user_data = UserLogin(email="g.popov@inno.ru", password=token_hex(16))

        mock_user = create_mock_user()

        with (
            patch.object(
                UsersAdapter, "get_user", return_value=mock_user
            ) as mock_get_user,
            patch.object(
                UsersAdapter,
                "verify_password",
                side_effect=user_errors.InvalidPasswordError,
            ) as mock_verify_password,
            patch.object(UsersAdapter, "get_access_token") as mock_get_token,
            pytest.raises(user_errors.InvalidPasswordError),
        ):
            self.users_service.login(user_data)

        mock_get_user.assert_called_once_with(user_data.email)
        mock_verify_password.assert_called_once_with(mock_user, user_data.password)
        mock_get_token.assert_not_called()
