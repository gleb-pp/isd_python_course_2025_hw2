from classes.users import AccessToken, UserCreate, UserLogin
from fastapi import APIRouter

router = APIRouter()


@router.post("/create_user", tags=["Users"])
async def create_user(user: UserCreate) -> AccessToken:
    """Create a user account with provided email, name, and password.

    Returns email and JWT access token for 30 minutes.
    """


@router.post("/login", tags=["Users"])
async def login(user: UserLogin) -> AccessToken:
    """Log into user account with provided email and password.

    Returns email and JWT access token for 30 minutes.
    """
