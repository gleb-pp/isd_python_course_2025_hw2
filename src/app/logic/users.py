from datetime import UTC, datetime, timedelta

from jose import jwt
from regex import match
from sqlalchemy.orm import Session

import src.app.exceptions.users as user_errors
from src.app.auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    JWT_SECRET_KEY,
    PWD_MIN_LENGTH,
    pwd_hasher,
)
from src.app.repo.users import User


def create_user(email: str, name: str, password: str, db: Session) -> None:
    """Create a new user with provided email, name, and password."""
    # validation of email format
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not (
        match(pattern, email)
        and len(email) <= 254
        and ".." not in email
        and len(email.split("@")[0]) <= 64
    ):
        raise user_errors.EmailFormatError

    # validation of username format
    pattern = r"^[\p{L}0-9_ ]+$"
    name = name.strip()
    if not (match(pattern, name) and 1 <= len(name) <= 80):
        raise user_errors.NameFormatError

    # validation of password length
    if len(password) < PWD_MIN_LENGTH:
        raise user_errors.WeakPasswordError

    # checking whether such user exists
    if db.query(User).filter(User.email == email).first() is not None:
        raise user_errors.UserExistsError(email)

    # hashing password
    hashed_password = pwd_hasher.hash(password)
    user = User(email=email, name=name, password_hash=hashed_password)
    db.add(user)


def get_access_token(email: str, password: str, db: Session) -> str:
    """Get JWT access token for user with provided email and password."""
    # checking whether such user exists
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise user_errors.UserNotFoundError(email)

    # checking password
    if not pwd_hasher.verify(password, user.password_hash):
        raise user_errors.InvalidPasswordError

    # giving access token
    data = {
        "email": email,
        "exp": datetime.now(tz=UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(data, JWT_SECRET_KEY, algorithm=ALGORITHM)
