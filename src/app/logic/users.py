from regex import match
import src.app.exceptions.users as user_errors
from src.app.repo.users import User
from datetime import datetime, timezone, timedelta
from jose import jwt
from src.app.auth import pwd_hasher, ACCESS_TOKEN_EXPIRE_MINUTES, JWT_SECRET_KEY, ALGORITHM


def create_user(email, name, password, db) -> None:
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
    pattern=r"^[\p{L}0-9_ ]+$"
    name = name.strip()
    if not (
        match(pattern, name)
        and 1 <= len(name) <= 80
    ):
        raise user_errors.NameFormatError

    # validation of password length
    if len(password) < 8:
        raise user_errors.WeakPasswordError

    # checking whether such user exists
    if db.query(User).filter(User.email == email).first() is not None:
        raise user_errors.UserExistsError(email)

    # hashing password
    hashed_password = pwd_hasher.hash(password)
    user = User(email=email, name=name, password_hash=hashed_password)
    db.add(user)


def get_access_token(email, password, db) -> str:
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
        "exp": datetime.now(tz=timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    access_token = jwt.encode(data, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return access_token
