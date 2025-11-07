from pydantic import BaseModel


class Success(BaseModel):
    """Indicates whether an operation was successful."""

    success: bool
