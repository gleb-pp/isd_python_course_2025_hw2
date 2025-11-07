from datetime import UTC, datetime, timedelta

from jose import jwt
from regex import match
from sqlalchemy.orm import Session

import src.app.exceptions.users as user_errors
from src.app.auth import pwd_hasher
from src.app.repo.users import User
from src.app.settings.auth import auth_settings
from src.app.settings.user import user_settings


def create_user(email: str, name: str, password: str, db: Session) -> User:
    """Create a new user with provided email, name, and password."""
    # checking whether such user exists
    if db.query(User).filter(User.email == email).first() is not None:
        raise user_errors.UserExistsError(email)

    # hashing password
    hashed_password = pwd_hasher.hash(password)
    user = User(email=email, name=name, password_hash=hashed_password)
    db.add(user)
    db.flush()
    return user


def validate_user_email(email: str) -> None:
    """Validate the format of the provided user email."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not (
        match(pattern, email)
        and len(email) <= user_settings.max_email_lenght
        and ".." not in email
        and len(email.split("@")[0]) <= user_settings.max_email_local_part
    ):
        raise user_errors.EmailFormatError


def validate_user_name(name: str) -> None:
    """Validate the format of the provided user name."""
    pattern = r"^[\p{L}0-9_ ]+$"
    name = name.strip()
    if not (
        match(pattern, name)
        and user_settings.min_user_name_lenght
        <= len(name)
        <= user_settings.max_user_name_lenght
    ):
        raise user_errors.NameFormatError


def validate_password_lenght(password: str) -> None:
    """Validate the length of the provided user password."""
    if len(password) < user_settings.pwd_min_lenght:
        raise user_errors.WeakPasswordError


def get_access_token(user: User) -> str:
    """Get JWT access token for user with provided email and password."""
    # giving access token
    data = {
        "email": user.email,
        "exp": datetime.now(tz=UTC)
        + timedelta(minutes=auth_settings.access_token_expire_minutes),
    }
    return jwt.encode(
        data, auth_settings.jwt_secret_key, algorithm=auth_settings.algorithm
    )


def get_all_users(db: Session) -> list[User]:
    """Get the list of all users in the system."""
    return db.query(User).all()


def get_user(email: str, db: Session) -> User:
    """Check whether a user with provided email exists in the system."""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise user_errors.UserNotFoundError(email)
    return user


def assert_user_is_admin(user: User) -> None:
    """Check whether the user with provided email has admin role."""
    if not user.is_admin:
        raise user_errors.AdminRoleRequiredError(user.email)


def verify_password(user: User, password: str) -> None:
    """Verify that the provided password is correct for the user with provided email."""
    if not pwd_hasher.verify(password, user.password_hash):
        raise user_errors.InvalidPasswordError


def delete_user(user: User, db: Session) -> None:
    """Delete the user from the database."""
    db.delete(user)
