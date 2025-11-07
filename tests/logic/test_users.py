from datetime import datetime
from secrets import token_hex
from unittest.mock import MagicMock, patch

import pytest

import src.app.exceptions.users as user_errors
from src.app.settings.user import user_settings
from src.app.auth import get_current_user
from src.app.logic.users import (
    assert_user_is_admin,
    create_user,
    delete_user,
    get_access_token,
    get_all_users,
    get_user,
    validate_password_lenght,
    validate_user_email,
    validate_user_name,
    verify_password,
)
from src.app.repo.users import User


def create_mock_user(**kwargs: object) -> MagicMock:
    """Create a mock User object for testing."""
    mock_user = MagicMock(spec=User)
    for key, value in kwargs.items():
        setattr(mock_user, key, value)
    return mock_user


def test__create_user__valid() -> None:
    """Check the valid user creation."""
    mock_db = MagicMock()
    mock_db.query().filter().first.return_value = None
    hashed_password = token_hex(16)
    mock_user = create_mock_user(
        email="g.popov@inno.ru", name="Gleb", password_hash=hashed_password
    )

    with (
        patch(
            "src.app.logic.users.pwd_hasher.hash", return_value=hashed_password
        ) as mock_hash,
        patch("src.app.logic.users.User", return_value=mock_user),
    ):
        user = create_user("g.popov@inno.ru", "Gleb", "12345678", mock_db)

    mock_hash.assert_called_once_with("12345678")
    mock_db.add.assert_called_once_with(mock_user)
    mock_db.flush.assert_called_once()
    assert user == mock_user


def test__create_user__alread_exists() -> None:
    """Attempt to create a user that already exists."""
    mock_db = MagicMock()
    mock_db.query().filter().first.return_value = create_mock_user()
    with pytest.raises(user_errors.UserExistsError):
        create_user("g.popov@inno.ru", "Gleb", "123456", mock_db)


@pytest.mark.parametrize(
    ("email", "expected_exception"),
    [
        ("g.popov@inno.ru", None),
        ("glebpopov.ru", user_errors.EmailFormatError),
        ("glebpopov", user_errors.EmailFormatError),
        ("g..popov@inno.ru", user_errors.EmailFormatError),
        (
            "gv" * user_settings.max_email_local_part + "@inno.ru",
            user_errors.EmailFormatError,
        ),
        (
            "g.popov@" + "i" * user_settings.max_email_lenght + ".ru",
            user_errors.EmailFormatError,
        ),
    ],
)
def test__validate_user_email(
    email: str, expected_exception: type[Exception] | None
) -> None:
    """Check the email validation."""
    if expected_exception:
        with pytest.raises(expected_exception):
            validate_user_email(email)
    else:
        validate_user_email(email)


@pytest.mark.parametrize(
    ("name", "expected_exception"),
    [
        ("Gleb123", None),
        ("GlebPopov", None),
        ("Gleb&?#34", user_errors.NameFormatError),
        ("G" * (user_settings.min_user_name_lenght - 1), user_errors.NameFormatError),
        ("G" * (user_settings.max_user_name_lenght + 1), user_errors.NameFormatError),
    ],
)
def test__validate_user_name(
    name: str, expected_exception: type[Exception] | None
) -> None:
    """Check the name validation."""
    if expected_exception:
        with pytest.raises(expected_exception):
            validate_user_name(name)
    else:
        validate_user_name(name)


@pytest.mark.parametrize(
    ("password", "expected_exception"),
    [
        ("", user_errors.WeakPasswordError),
        ("G" * (user_settings.pwd_min_lenght - 1), user_errors.WeakPasswordError),
        ("G" * user_settings.pwd_min_lenght, None),
    ],
)
def test__validate_password_lenght(
    password: str, expected_exception: type[Exception] | None
) -> None:
    """Check the password validation."""
    if expected_exception:
        with pytest.raises(expected_exception):
            validate_password_lenght(password)
    else:
        validate_password_lenght(password)


def test__get_access_token() -> None:
    """Check that get_access_token encodes correct data."""
    user = create_mock_user(email="g.popov@inno.ru")
    random_token = token_hex(16)
    with patch("jose.jwt.encode", return_value=random_token) as mock_jwt:
        token = get_access_token(user)

    mock_jwt.assert_called_once()
    args, _kwargs = mock_jwt.call_args
    payload = args[0]

    assert payload["email"] == user.email
    assert "exp" in payload
    assert isinstance(payload["exp"], datetime)
    assert token == random_token


def test__get_all_users() -> None:
    """Check all users are returned."""
    mock_db = MagicMock()
    mock_db.query().all.return_value = [create_mock_user()]
    users = get_all_users(mock_db)
    mock_db.query().all.assert_called_once()
    assert len(users) == 1


def test__get_user__exists() -> None:
    """Check existing user is returned."""
    mock_db = MagicMock()
    u = create_mock_user(email="g.popov@inno.ru")
    mock_db.query().filter().first.return_value = u

    user = get_user("g.popov@inno.ru", mock_db)
    assert user == u


def test__get_user__not_found() -> None:
    """Check that UserNotFoundError is raised if user missing."""
    mock_db = MagicMock()
    mock_db.query().filter().first.return_value = None

    with pytest.raises(user_errors.UserNotFoundError):
        get_user("g.popov@inno.ru", mock_db)


def test__assert_user_is_admin__success() -> None:
    """Check admin user passes."""
    user = create_mock_user(email="g.popov@inno.ru", is_admin=True)
    assert_user_is_admin(user)


def test__assert_user_is_admin__fail() -> None:
    """Check non-admin user raises AdminRoleRequiredError."""
    user = create_mock_user(email="g.popov@inno.ru", is_admin=False)
    with pytest.raises(user_errors.AdminRoleRequiredError):
        assert_user_is_admin(user)


def test__verify_password__correct() -> None:
    """Password verification succeeds."""
    hashed_password = token_hex(16)
    user = create_mock_user(password_hash=hashed_password)
    with patch(
        "src.app.logic.users.pwd_hasher.verify", return_value=True
    ) as mock_verify:
        verify_password(user, "password")
    mock_verify.assert_called_once_with("password", hashed_password)


def test__verify_password__wrong() -> None:
    """Invalid password raises InvalidPasswordError."""
    user = create_mock_user(password_hash=token_hex(16))
    with (
        patch("src.app.logic.users.pwd_hasher.verify", return_value=False),
        pytest.raises(user_errors.InvalidPasswordError),
    ):
        verify_password(user, "wrong")


def test_delete_user_called() -> None:
    """Check delete_user calls db.delete."""
    mock_db = MagicMock()
    user = create_mock_user(email="g.popov@inno.ru")
    delete_user(user, mock_db)
    mock_db.delete.assert_called_once_with(user)
