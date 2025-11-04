from secrets import token_hex
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

import src.app.exceptions.users as user_errors
from src.app.db import get_db
from src.app.main import app
from src.app.repo.users import User

client = TestClient(app)

HTTP_200_OK = 200
HTTP_422_UNPROCESSABLE_ENTITY = 422
HTTP_409_CONFLICT = 409
HTTP_401_UNAUTHORIZED = 401


def create_mock_user(**kwargs: object) -> MagicMock:
    """Create a mock User object for testing."""
    mock_user = MagicMock(spec=User)
    for key, value in kwargs.items():
        setattr(mock_user, key, value)
    return mock_user


def test__register__success() -> None:
    """Test successful user registration."""
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    user_data = {"email": "g.popov@inno.ru", "name": "Gleb", "password": "12345678"}

    mock_user = create_mock_user()
    mock_token = token_hex(32)

    with (
        patch(
            "src.app.presentation.users.user_logic.validate_user_email"
        ) as mock_validate_email,
        patch(
            "src.app.presentation.users.user_logic.validate_user_name"
        ) as mock_validate_name,
        patch(
            "src.app.presentation.users.user_logic.validate_password_lenght"
        ) as mock_validate_password,
        patch(
            "src.app.presentation.users.user_logic.create_user", return_value=mock_user
        ) as mock_create_user,
        patch(
            "src.app.presentation.users.user_logic.get_access_token",
            return_value=mock_token,
        ) as mock_get_access_token,
    ):
        response = client.post("/register", json=user_data)

    mock_validate_email.assert_called_once_with(user_data["email"])
    mock_validate_name.assert_called_once_with(user_data["name"])
    mock_validate_password.assert_called_once_with(user_data["password"])
    mock_create_user.assert_called_once_with(
        user_data["email"], user_data["name"], user_data["password"], mock_db
    )
    mock_get_access_token.assert_called_once_with(mock_user)
    mock_db.commit.assert_called_once()
    mock_db.rollback.assert_not_called()
    assert response.status_code == HTTP_200_OK
    assert response.json() == {"access_token": mock_token}


def test__register__invalid_email() -> None:
    """Attempt to register an account with an invalid email."""
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    user_data = {"email": "gpopov", "name": "Gleb", "password": "12345678"}

    mock_user = create_mock_user()
    mock_token = token_hex(32)

    with (
        patch(
            "src.app.presentation.users.user_logic.validate_user_email",
            side_effect=user_errors.EmailFormatError,
        ) as mock_validate_email,
        patch(
            "src.app.presentation.users.user_logic.validate_user_name"
        ) as mock_validate_name,
        patch(
            "src.app.presentation.users.user_logic.validate_password_lenght"
        ) as mock_validate_password,
        patch(
            "src.app.presentation.users.user_logic.create_user", return_value=mock_user
        ) as mock_create_user,
        patch(
            "src.app.presentation.users.user_logic.get_access_token",
            return_value=mock_token,
        ) as mock_get_access_token,
    ):
        response = client.post("/register", json=user_data)

    mock_validate_email.assert_called_once_with(user_data["email"])
    mock_validate_name.assert_not_called()
    mock_validate_password.assert_not_called()
    mock_create_user.assert_not_called()
    mock_get_access_token.assert_not_called()
    mock_db.commit.assert_not_called()
    mock_db.rollback.assert_called_once()
    assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY


def test__register__invalid_name() -> None:
    """Attempt to register an account with an invalid email."""
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    user_data = {
        "email": "g.popov@inno.ru",
        "name": "Gleb" * 21,
        "password": "12345678",
    }

    mock_user = create_mock_user()
    mock_token = token_hex(32)

    with (
        patch(
            "src.app.presentation.users.user_logic.validate_user_email"
        ) as mock_validate_email,
        patch(
            "src.app.presentation.users.user_logic.validate_user_name",
            side_effect=user_errors.NameFormatError,
        ) as mock_validate_name,
        patch(
            "src.app.presentation.users.user_logic.validate_password_lenght"
        ) as mock_validate_password,
        patch(
            "src.app.presentation.users.user_logic.create_user", return_value=mock_user
        ) as mock_create_user,
        patch(
            "src.app.presentation.users.user_logic.get_access_token",
            return_value=mock_token,
        ) as mock_get_access_token,
    ):
        response = client.post("/register", json=user_data)

    mock_validate_email.assert_called_once_with(user_data["email"])
    mock_validate_name.assert_called_once_with(user_data["name"])
    mock_validate_password.assert_not_called()
    mock_create_user.assert_not_called()
    mock_get_access_token.assert_not_called()
    mock_db.commit.assert_not_called()
    mock_db.rollback.assert_called_once()
    assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY


def test__register__invalid_password() -> None:
    """Attempt to register an account with an invalid password."""
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    user_data = {"email": "g.popov@inno.ru", "name": "Gleb", "password": "123"}

    mock_user = create_mock_user()
    mock_token = token_hex(32)

    with (
        patch(
            "src.app.presentation.users.user_logic.validate_user_email"
        ) as mock_validate_email,
        patch(
            "src.app.presentation.users.user_logic.validate_user_name"
        ) as mock_validate_name,
        patch(
            "src.app.presentation.users.user_logic.validate_password_lenght",
            side_effect=user_errors.WeakPasswordError,
        ) as mock_validate_password,
        patch(
            "src.app.presentation.users.user_logic.create_user", return_value=mock_user
        ) as mock_create_user,
        patch(
            "src.app.presentation.users.user_logic.get_access_token",
            return_value=mock_token,
        ) as mock_get_access_token,
    ):
        response = client.post("/register", json=user_data)

    mock_validate_email.assert_called_once_with(user_data["email"])
    mock_validate_name.assert_called_once_with(user_data["name"])
    mock_validate_password.assert_called_once_with(user_data["password"])
    mock_create_user.assert_not_called()
    mock_get_access_token.assert_not_called()
    mock_db.commit.assert_not_called()
    mock_db.rollback.assert_called_once()
    assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY


def test__register__user_exists() -> None:
    """Attempt to register an account that already exists."""
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    user_data = {"email": "g.popov@inno.ru", "name": "Gleb", "password": "12345678"}

    mock_token = token_hex(32)

    with (
        patch(
            "src.app.presentation.users.user_logic.validate_user_email"
        ) as mock_validate_email,
        patch(
            "src.app.presentation.users.user_logic.validate_user_name"
        ) as mock_validate_name,
        patch(
            "src.app.presentation.users.user_logic.validate_password_lenght"
        ) as mock_validate_password,
        patch(
            "src.app.presentation.users.user_logic.create_user",
            side_effect=user_errors.UserExistsError(user_data["email"]),
        ) as mock_create_user,
        patch(
            "src.app.presentation.users.user_logic.get_access_token",
            return_value=mock_token,
        ) as mock_get_access_token,
    ):
        response = client.post("/register", json=user_data)

    mock_validate_email.assert_called_once_with(user_data["email"])
    mock_validate_name.assert_called_once_with(user_data["name"])
    mock_validate_password.assert_called_once_with(user_data["password"])
    mock_create_user.assert_called_once_with(
        user_data["email"], user_data["name"], user_data["password"], mock_db
    )
    mock_get_access_token.assert_not_called()
    mock_db.commit.assert_not_called()
    mock_db.rollback.assert_called_once()
    assert response.status_code == HTTP_409_CONFLICT


def test__login__success() -> None:
    """Test successful user login."""
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    user_data = {"email": "g.popov@inno.ru", "password": "12345678"}

    mock_user = create_mock_user()
    mock_token = token_hex(32)

    with (
        patch(
            "src.app.presentation.users.user_logic.get_user", return_value=mock_user
        ) as mock_get_user,
        patch(
            "src.app.presentation.users.user_logic.verify_password"
        ) as mock_verify_password,
        patch(
            "src.app.presentation.users.user_logic.get_access_token",
            return_value=mock_token,
        ) as mock_get_token,
    ):
        response = client.post("/login", json=user_data)

    mock_get_user.assert_called_once_with(user_data["email"], mock_db)
    mock_verify_password.assert_called_once_with(mock_user, user_data["password"])
    mock_get_token.assert_called_once_with(mock_user)
    assert response.status_code == HTTP_200_OK
    assert response.json() == {"access_token": mock_token}


def test__login__random_email() -> None:
    """Attempt to login with incorrect email."""
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    user_data = {"email": "g.popov@inno.ru", "password": "12345678"}

    mock_token = token_hex(32)

    with (
        patch(
            "src.app.presentation.users.user_logic.get_user",
            side_effect=user_errors.UserNotFoundError(user_data["email"]),
        ) as mock_get_user,
        patch(
            "src.app.presentation.users.user_logic.verify_password"
        ) as mock_verify_password,
        patch(
            "src.app.presentation.users.user_logic.get_access_token",
            return_value=mock_token,
        ) as mock_get_token,
    ):
        response = client.post("/login", json=user_data)

    mock_get_user.assert_called_once_with(user_data["email"], mock_db)
    mock_verify_password.assert_not_called()
    mock_get_token.assert_not_called()
    assert response.status_code == HTTP_401_UNAUTHORIZED


def test__login__wrong_password() -> None:
    """Attempt to login with the wrong password."""
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    user_data = {"email": "g.popov@inno.ru", "password": "wrongpass"}

    mock_user = create_mock_user()
    mock_token = token_hex(32)

    with (
        patch(
            "src.app.presentation.users.user_logic.get_user", return_value=mock_user
        ) as mock_get_user,
        patch(
            "src.app.presentation.users.user_logic.verify_password",
            side_effect=user_errors.InvalidPasswordError,
        ) as mock_verify_password,
        patch(
            "src.app.presentation.users.user_logic.get_access_token",
            return_value=mock_token,
        ) as mock_get_token,
    ):
        response = client.post("/login", json=user_data)

    mock_get_user.assert_called_once_with(user_data["email"], mock_db)
    mock_verify_password.assert_called_once_with(mock_user, user_data["password"])
    mock_get_token.assert_not_called()
    assert response.status_code == HTTP_401_UNAUTHORIZED
