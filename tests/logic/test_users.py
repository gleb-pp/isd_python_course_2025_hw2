from datetime import datetime
from secrets import token_hex
from unittest.mock import MagicMock, patch

import pytest

import src.app.domain.exceptions.users as user_errors
from src.app.infrastructure.db_models.users import UserDB
from src.app.infrastructure.adapters.users_adapter import UsersAdapter
from src.app.settings.user import user_settings


def create_mock_user(**kwargs: object) -> MagicMock:
    """Create a mock UserDB object for testing."""
    mock_user = MagicMock(spec=UserDB)
    for key, value in kwargs.items():
        setattr(mock_user, key, value)
    return mock_user


class TestUsersAdapter:
    """Test class for UsersAdapter."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.mock_db = MagicMock()
        self.users_adapter = UsersAdapter(self.mock_db)

    def test__create_user__valid(self) -> None:
        """Check the valid user creation."""
        self.mock_db.query().filter().first.return_value = None
        hashed_password = token_hex(16)
        mock_user = create_mock_user(
            email="g.popov@inno.ru", name="Gleb", password_hash=hashed_password
        )

        with (
            patch(
                "src.app.infrastructure.adapters.users_adapter.pwd_hasher.hash", return_value=hashed_password
            ) as mock_hash,
            patch("src.app.infrastructure.adapters.users_adapter.UserDB", return_value=mock_user),
        ):
            user = self.users_adapter.create_user("g.popov@inno.ru", "Gleb", "12345678")

        mock_hash.assert_called_once_with("12345678")
        self.mock_db.add.assert_called_once_with(mock_user)
        self.mock_db.flush.assert_called_once()
        assert user == mock_user


    def test__create_user__alread_exists(self) -> None:
        """Attempt to create a user that already exists."""
        self.mock_db.query().filter().first.return_value = create_mock_user()
        with pytest.raises(user_errors.UserExistsError):
            self.users_adapter.create_user("g.popov@inno.ru", "Gleb", "123456")


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
        self, email: str, expected_exception: type[Exception] | None
    ) -> None:
        """Check the email validation."""
        if expected_exception:
            with pytest.raises(expected_exception):
                self.users_adapter.validate_user_email(email)
        else:
            self.users_adapter.validate_user_email(email)


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
        self, name: str, expected_exception: type[Exception] | None
    ) -> None:
        """Check the name validation."""
        if expected_exception:
            with pytest.raises(expected_exception):
                self.users_adapter.validate_user_name(name)
        else:
            self.users_adapter.validate_user_name(name)


    @pytest.mark.parametrize(
        ("password", "expected_exception"),
        [
            ("", user_errors.WeakPasswordError),
            ("G" * (user_settings.pwd_min_lenght - 1), user_errors.WeakPasswordError),
            ("G" * user_settings.pwd_min_lenght, None),
        ],
    )
    def test__validate_password_lenght(
        self, password: str, expected_exception: type[Exception] | None
    ) -> None:
        """Check the password validation."""
        if expected_exception:
            with pytest.raises(expected_exception):
                self.users_adapter.validate_password_lenght(password)
        else:
            self.users_adapter.validate_password_lenght(password)


    def test__get_access_token(self) -> None:
        """Check that get_access_token encodes correct data."""
        user = create_mock_user(email="g.popov@inno.ru")
        random_token = token_hex(16)
        with patch("jose.jwt.encode", return_value=random_token) as mock_jwt:
            token = self.users_adapter.get_access_token(user)

        mock_jwt.assert_called_once()
        args, _kwargs = mock_jwt.call_args
        payload = args[0]

        assert payload["email"] == user.email
        assert "exp" in payload
        assert isinstance(payload["exp"], datetime)
        assert token == random_token


    def test__get_all_users(self) -> None:
        """Check all users are returned."""
        self.mock_db.query().all.return_value = [create_mock_user()]
        users = self.users_adapter.get_all_users()
        self.mock_db.query().all.assert_called_once()
        assert len(users) == 1


    def test__get_user__exists(self) -> None:
        """Check existing user is returned."""
        u = create_mock_user(email="g.popov@inno.ru")
        self.mock_db.query().filter().first.return_value = u

        user = self.users_adapter.get_user("g.popov@inno.ru")
        assert user == u


    def test__get_user__not_found(self) -> None:
        """Check that UserNotFoundError is raised if user missing."""
        self.mock_db.query().filter().first.return_value = None

        with pytest.raises(user_errors.UserNotFoundError):
            self.users_adapter.get_user("g.popov@inno.ru")


    def test__assert_user_is_admin__success(self) -> None:
        """Check admin user passes."""
        user = create_mock_user(email="g.popov@inno.ru", is_admin=True)
        self.users_adapter.assert_user_is_admin(user)


    def test__assert_user_is_admin__fail(self) -> None:
        """Check non-admin user raises AdminRoleRequiredError."""
        user = create_mock_user(email="g.popov@inno.ru", is_admin=False)
        with pytest.raises(user_errors.AdminRoleRequiredError):
            self.users_adapter.assert_user_is_admin(user)


    def test__verify_password__correct(self) -> None:
        """Password verification succeeds."""
        hashed_password = token_hex(16)
        user = create_mock_user(password_hash=hashed_password)
        with patch(
            "src.app.infrastructure.adapters.users_adapter.pwd_hasher.verify", return_value=True
        ) as mock_verify:
            self.users_adapter.verify_password(user, "password")
        mock_verify.assert_called_once_with("password", hashed_password)


    def test__verify_password__wrong(self) -> None:
        """Invalid password raises InvalidPasswordError."""
        user = create_mock_user(password_hash=token_hex(16))
        with (
            patch("src.app.infrastructure.adapters.users_adapter.pwd_hasher.verify", return_value=False),
            pytest.raises(user_errors.InvalidPasswordError),
        ):
            self.users_adapter.verify_password(user, "wrong")


    def test_delete_user_called(self) -> None:
        """Check delete_user calls db.delete."""
        user = create_mock_user(email="g.popov@inno.ru")
        self.users_adapter.delete_user(user)
        self.mock_db.delete.assert_called_once_with(user)
