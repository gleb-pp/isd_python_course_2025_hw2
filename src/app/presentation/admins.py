from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import src.app.domain.exceptions.bookings as booking_errors
import src.app.domain.exceptions.events as event_errors
import src.app.domain.exceptions.users as user_errors
import src.app.logic.bookings as bookings_logic
import src.app.logic.events as events_logic
import src.app.logic.users as user_logic
from src.app.auth import get_current_user
from src.app.db import get_db
from src.app.services.models.bookings import Booking, EventParticipants
from src.app.services.models.common import Success
from src.app.services.models.users import User, UserCreate

router = APIRouter(
    prefix="/admin",
    tags=["Admins"],
)


@router.get("/users")
async def get_all_users(
    admin_email: Annotated[str, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[User]:
    """Get the list of all users in the system.

    Return the email and name of each user.

    Admin role required.
    """
    try:
        user = user_logic.get_user(admin_email, db)
        user_logic.assert_user_is_admin(user)
        users = user_logic.get_all_users(db)
        return [User.model_validate(user) for user in users]
    except user_errors.UserNotFoundError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e
    except user_errors.AdminRoleRequiredError as e:
        raise HTTPException(status_code=403, detail=str(e)) from e


@router.post("/users")
async def create_user(
    new_user: UserCreate,
    admin_email: Annotated[str, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Success:
    """Create a user account with provided email, name, and password.

    User email should be in the correct format.

    User name can contain only letters, digits, spaces, and underscores.

    User name must contains from 1 to 80 symbols.

    User password should have at least 8 symbols.

    Admin role required.
    """
    try:
        user = user_logic.get_user(admin_email, db)
        user_logic.assert_user_is_admin(user)
        user_logic.validate_user_email(new_user.email)
        user_logic.validate_user_name(new_user.name)
        user_logic.validate_password_lenght(new_user.password)
        user_logic.create_user(new_user.email, new_user.name, new_user.password, db)
        db.commit()
        return Success(success=True)
    except user_errors.UserNotFoundError as e:
        db.rollback()
        raise HTTPException(status_code=401, detail=str(e)) from e
    except user_errors.AdminRoleRequiredError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail=str(e)) from e
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


@router.delete("/users/{deleted_user_email}")
async def delete_user(
    deleted_user_email: str,
    admin_email: Annotated[str, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Success:
    """Delete user account from the system.

    The user will be removed from all events for which they are registered.

    All events organized by the deleted user will also be deleted.

    A user cannot delete themselves.

    Admin role required.
    """
    try:
        user = user_logic.get_user(admin_email, db)
        user_logic.assert_user_is_admin(user)
    except user_errors.UserNotFoundError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e
    except user_errors.AdminRoleRequiredError as e:
        raise HTTPException(status_code=403, detail=str(e)) from e

    try:
        deleted_user = user_logic.get_user(deleted_user_email, db)
        user_logic.delete_user(deleted_user, db)
        db.commit()
        return Success(success=True)
    except user_errors.UserNotFoundError as e:
        db.rollback()
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.delete("/events/{event_id}")
async def delete_event(
    event_id: int,
    admin_email: Annotated[str, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Success:
    """Remove the event with provided event_id.

    Admin role required.
    """
    try:
        user = user_logic.get_user(admin_email, db)
        user_logic.assert_user_is_admin(user)
        event = events_logic.get_event(event_id, db)
        events_logic.delete_event(event, db)
        db.commit()
        return Success(success=True)
    except user_errors.UserNotFoundError as e:
        db.rollback()
        raise HTTPException(status_code=401, detail=str(e)) from e
    except user_errors.AdminRoleRequiredError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail=str(e)) from e
    except event_errors.EventNotFoundError as e:
        db.rollback()
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post("/bookings/{event_id}/{guest_email}")
async def create_user_booking(
    event_id: int,
    guest_email: str,
    admin_email: Annotated[str, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Success:
    """Create a booking for the user with guest_email to the event with event_id.

    Admin role required.
    """
    try:
        user = user_logic.get_user(admin_email, db)
        user_logic.assert_user_is_admin(user)
    except user_errors.UserNotFoundError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e
    except user_errors.AdminRoleRequiredError as e:
        raise HTTPException(status_code=403, detail=str(e)) from e

    try:
        guest = user_logic.get_user(guest_email, db)
        event = events_logic.get_event(event_id, db)
        bookings_logic.assert_seats_available(event, db)
        bookings_logic.create_booking(event, guest, db)
        db.commit()
        return Success(success=True)
    except user_errors.UserNotFoundError as e:
        db.rollback()
        raise HTTPException(status_code=404, detail=str(e)) from e
    except event_errors.EventNotFoundError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e)) from e
    except booking_errors.EventFullError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail=str(e)) from e


@router.delete("/bookings/{event_id}/{guest_email}")
async def delete_user_booking(
    event_id: int,
    guest_email: str,
    admin_email: Annotated[str, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Success:
    """Delete a booking for the user with guest_email from the event with event_id.

    Admin role required.
    """
    try:
        user = user_logic.get_user(admin_email, db)
        user_logic.assert_user_is_admin(user)
    except user_errors.UserNotFoundError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e
    except user_errors.AdminRoleRequiredError as e:
        raise HTTPException(status_code=403, detail=str(e)) from e

    try:
        guest = user_logic.get_user(guest_email, db)
        event = events_logic.get_event(event_id, db)
        bookings_logic.delete_booking(event, guest, db)
        db.commit()
        return Success(success=True)
    except user_errors.UserNotFoundError as e:
        db.rollback()
        raise HTTPException(status_code=404, detail=str(e)) from e
    except event_errors.EventNotFoundError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/bookings/{event_id}")
async def get_event_participants(
    event_id: int,
    admin_email: Annotated[str, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> EventParticipants:
    """Get the list of bookings for the event with event_id.

    Admin role required.
    """
    try:
        user = user_logic.get_user(admin_email, db)
        user_logic.assert_user_is_admin(user)
        event = events_logic.get_event(event_id, db)
        participants_emails = bookings_logic.get_event_participants(event, db)
        return EventParticipants(participants_emails=participants_emails)
    except user_errors.UserNotFoundError as e:
        db.rollback()
        raise HTTPException(status_code=401, detail=str(e)) from e
    except user_errors.AdminRoleRequiredError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail=str(e)) from e
    except event_errors.EventNotFoundError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/bookings")
async def get_bookings(
    admin_email: Annotated[str, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[Booking]:
    """Get the list of all bookings in the system.

    Admin role required.
    """
    try:
        user = user_logic.get_user(admin_email, db)
        user_logic.assert_user_is_admin(user)
        bookings = bookings_logic.get_all_bookings(db)
        return [Booking.model_validate(booking) for booking in bookings]
    except user_errors.UserNotFoundError as e:
        db.rollback()
        raise HTTPException(status_code=401, detail=str(e)) from e
    except user_errors.AdminRoleRequiredError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail=str(e)) from e
