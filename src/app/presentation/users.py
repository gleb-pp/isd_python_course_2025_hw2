from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import src.app.logic.users
import src.app.exceptions.users as user_errors
from src.app.db import get_db

from src.app.models.users import AccessToken, UserCreate, UserLogin

router = APIRouter(tags=["Users"])


@router.post("/register")
async def register(user: UserCreate, db: Session = Depends(get_db)) -> AccessToken:
    """Register a user account with provided email, name, and password.

    User email should be in the correct format.

    User name can contain only letters, digits, spaces, and underscores.

    User name must contains from 1 to 80 symbols.

    User password should have at least 8 symbols.

    Returns email and JWT access token for 30 minutes.
    """

    try:
        src.app.logic.users.create_user(user.email, user.name, user.password, db)
        db.flush()
        token = src.app.logic.users.get_access_token(user.email, user.password, db)
        db.commit()
        return AccessToken(access_token=token)
    except (
        user_errors.EmailFormatError,
        user_errors.NameFormatError,
        user_errors.WeakPasswordError
    ) as e:
        db.rollback()
        raise HTTPException(status_code=422, detail=str(e))
    except user_errors.UserExistsError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail=str(e))
    except (
        user_errors.UserNotFoundError,
        user_errors.InvalidPasswordError
    ) as e:
        db.rollback()
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/login")
async def login(user: UserLogin, db: Session = Depends(get_db)) -> AccessToken:
    """Log into user account with provided email and password.

    Returns email and JWT access token for 30 minutes.
    """

    try:
        token = src.app.logic.users.get_access_token(user.email, user.password, db)
        db.commit()
        return AccessToken(access_token=token)
    except user_errors.UserException as e:
        db.rollback()
        raise HTTPException(status_code=401, detail=str(e))
