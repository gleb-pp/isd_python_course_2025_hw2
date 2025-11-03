from typing import Annotated

from fastapi import APIRouter, Depends

from src.app.auth import get_current_user
from src.app.models.common import Success
from src.app.models.users import User, UserCreate

router = APIRouter(
    prefix="/admin",
    tags=["Admins"],
)


@router.get("/users")
async def get_all_users(
    user_email: Annotated[str, Depends(get_current_user)],
) -> list[User]:
    """Get the list of all users in the system.

    Return the email and name of each user.

    Admin role required.
    """


@router.post("/users/")
async def create_user(
    new_user: UserCreate, admin_email: Annotated[str, Depends(get_current_user)]
) -> Success:
    """Create a user account with provided email, name, and password.

    Admin role required.
    """


@router.delete("/users/{user_email}")
async def delete_user(
    deleted_user_email: str, user_email: Annotated[str, Depends(get_current_user)]
) -> Success:
    """Delete user account from the system.

    The user will be removed from all events for which they are registered.

    All events organized by the deleted user will also be deleted.

    A user cannot delete themselves.

    Admin role required.
    """


@router.delete("/events/{event_id}")
async def delete_event(
    event_id: str, user_email: Annotated[str, Depends(get_current_user)]
) -> Success:
    """Remove the event with provided event_id.

    Admin role required.
    """


# TODO: метрики
