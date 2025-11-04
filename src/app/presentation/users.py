from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import src.app.exceptions.users as user_errors
import src.app.logic.users as user_logic
from src.app.db import get_db
from src.app.models.users import AccessToken, UserCreate, UserLogin

router = APIRouter(tags=["Users"])


@router.post("/register")
async def register(
    user: UserCreate, db: Annotated[Session, Depends(get_db)]
) -> AccessToken:
    """Register a user account with provided email, name, and password.

    User email should be in the correct format.

    User name can contain only letters, digits, spaces, and underscores.

    User name must contains from 1 to 80 symbols.

    User password should have at least 8 symbols.

    Returns email and JWT access token for 30 minutes.
    """

    try:
        user_logic.validate_user_email(user.email)
        user_logic.validate_user_name(user.name)
        user_logic.validate_password_lenght(user.password)
        user = user_logic.create_user(user.email, user.name, user.password, db)
        token = user_logic.get_access_token(user)
        db.commit()
        return AccessToken(access_token=token)
    except (
        user_errors.EmailFormatError,
        user_errors.NameFormatError,
        user_errors.WeakPasswordError,
    ) as e:
        db.rollback()
        raise HTTPException(status_code=422, detail=str(e)) from e
    except user_errors.UserExistsError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail=str(e)) from e


@router.post("/login")
async def login(
    user: UserLogin, db: Annotated[Session, Depends(get_db)]
) -> AccessToken:
    """Log into user account with provided email and password.

    Returns email and JWT access token for 30 minutes.
    """

    try:
        user = user_logic.get_user(user.email, db)
        user_logic.verify_password(user, user.password)
        token = user_logic.get_access_token(user)
        return AccessToken(access_token=token)
    except user_errors.UserError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e
