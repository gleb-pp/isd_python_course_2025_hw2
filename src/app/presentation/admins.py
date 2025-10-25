from typing import Annotated

from auth import get_current_user
from classes.common import Success
from classes.users import User
from fastapi import APIRouter, Depends

router = APIRouter()


@router.get("/admin/users", tags=["Admins"])
async def get_all_users(
    user_email: Annotated[str, Depends(get_current_user)],
) -> list[User]:
    """Get the list of all users in the system.

    Return the email and name of each user.

    Admin role required.
    """


@router.delete("/admin/users/{user_email}", tags=["Admins"])
async def delete_user(
    deleted_user_email: str, user_email: Annotated[str, Depends(get_current_user)]
) -> Success:
    """Delete user account from the system.

    The user will be removed from all events for which they are registered.

    All events organized by the deleted user will also be deleted.

    A user cannot delete themselves.

    Admin role required.
    """


@router.delete("/admin/events/{event_id}", tags=["Admins"])
async def delete_event(
    deleted_user_email: str, user_email: Annotated[str, Depends(get_current_user)]
) -> Success:
    """Remove the event with provided event_id.

    Admin role required.
    """
