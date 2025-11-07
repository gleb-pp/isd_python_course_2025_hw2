from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import src.app.domain.exceptions.users as user_errors
from src.app.db import get_db
from src.app.services.models.users import AccessToken, UserCreate, UserLogin
from src.app.services.users import UserService

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
    service = UserService(db)
    try:
        return service.register(user)
    except (
        user_errors.EmailFormatError,
        user_errors.NameFormatError,
        user_errors.WeakPasswordError,
    ) as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except user_errors.UserExistsError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e


@router.post("/login")
async def login(
    user: UserLogin, db: Annotated[Session, Depends(get_db)]
) -> AccessToken:
    """Log into user account with provided email and password.

    Returns email and JWT access token for 30 minutes.
    """
    service = UserService(db)
    try:
        return service.login(user)
    except user_errors.UserError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e
