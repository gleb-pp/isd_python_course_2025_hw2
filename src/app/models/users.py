from pydantic import BaseModel, ConfigDict


class AccessToken(BaseModel):
    """Access token for authenticated user."""

    access_token: str


class User(BaseModel):
    """Basic user information."""

    email: str
    name: str
    model_config = ConfigDict(from_attributes=True)


class UserCreate(User):
    """User creation information."""

    password: str


class UserLogin(BaseModel):
    """User login information."""

    email: str
    password: str
