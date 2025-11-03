from pydantic import BaseModel


class AccessToken(BaseModel):
    """Access token for authenticated user."""

    access_token: str


class User(BaseModel):
    """Basic user information."""

    email: str
    name: str


class UserCreate(User):
    """User creation information."""

    password: str


class UserLogin(BaseModel):
    """User login information."""

    email: str
    password: str
