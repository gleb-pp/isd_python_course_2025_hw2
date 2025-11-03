from fastapi import APIRouter

from src.app.models.users import AccessToken, UserCreate, UserLogin

router = APIRouter(tags=["Users"])


@router.post("/register")
async def register(user: UserCreate) -> AccessToken:
    """Register a user account with provided email, name, and password.

    Returns email and JWT access token for 30 minutes.
    """


@router.post("/login")
async def login(user: UserLogin) -> AccessToken:
    """Log into user account with provided email and password.

    Returns email and JWT access token for 30 minutes.
    """
