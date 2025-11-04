from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import src.app.exceptions.users as user_errors
import src.app.logic.events as events_logic
import src.app.logic.metrics as metrics_logic
import src.app.logic.users as user_logic
from src.app.auth import get_current_user
from src.app.db import get_db
from src.app.models.metrics import (
    AverageBookingsPerUser,
    AverageRegistrations,
    EventRegistrations,
    OfflineEventsRatio,
    TopRegistrationsMetric,
)

router = APIRouter(
    prefix="/admin/metrics",
    tags=["Metrics"],
)


@router.get("/top_registrations")
async def get_top_registrations_events(
    admin_email: Annotated[str, Depends(get_current_user)],
    events_number: int,
    db: Annotated[Session, Depends(get_db)],
) -> TopRegistrationsMetric:
    """Get the list of N most popular events with the biggest number of bookings.

    Admin role required.
    """
    try:
        user = user_logic.get_user(admin_email, db)
        user_logic.assert_user_is_admin(user)
        events = events_logic.get_events_list(db)
        events_registrations = [
            EventRegistrations(
                event_id=event.id,
                registrations=metrics_logic.get_event_registrations(event, db),
            )
            for event in events
        ]
        return TopRegistrationsMetric(
            events=sorted(
                events_registrations, key=lambda e: e.registrations, reverse=True
            )[:events_number]
        )
    except user_errors.UserNotFoundError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e
    except user_errors.AdminRoleRequiredError as e:
        raise HTTPException(status_code=403, detail=str(e)) from e


@router.get("/average_registrations")
async def get_average_registrations(
    admin_email: Annotated[str, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> AverageRegistrations:
    """Get the average number of bookings per event.

    Admin role required.
    """
    try:
        user = user_logic.get_user(admin_email, db)
        user_logic.assert_user_is_admin(user)
        events = events_logic.get_events_list(db)
        if not events:
            return AverageRegistrations(average_registrations=0.0)
        events_registrations = [
            metrics_logic.get_event_registrations(event, db) for event in events
        ]
        return AverageRegistrations(
            average_registrations=sum(events_registrations) / len(events_registrations)
        )
    except user_errors.UserNotFoundError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e
    except user_errors.AdminRoleRequiredError as e:
        raise HTTPException(status_code=403, detail=str(e)) from e


@router.get("/average_bookings_per_user")
async def get_average_bookings_per_user(
    admin_email: Annotated[str, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> AverageBookingsPerUser:
    """Get the average number of bookings per user.

    Admin role required.
    """
    try:
        admin = user_logic.get_user(admin_email, db)
        user_logic.assert_user_is_admin(admin)
        users = user_logic.get_all_users(db)
        if not users:
            return AverageBookingsPerUser(average_bookings_per_user=0.0)
        users_bookings = [metrics_logic.get_user_bookings(user, db) for user in users]
        return AverageBookingsPerUser(
            average_bookings_per_user=sum(users_bookings) / len(users_bookings)
        )
    except user_errors.UserNotFoundError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e
    except user_errors.AdminRoleRequiredError as e:
        raise HTTPException(status_code=403, detail=str(e)) from e


@router.get("/offline_ratio")
async def get_offline_events_ratio(
    admin_email: Annotated[str, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> OfflineEventsRatio:
    """Get the percentage of offline events among all events.

    Admin role required.
    """
    try:
        admin = user_logic.get_user(admin_email, db)
        user_logic.assert_user_is_admin(admin)
        events = events_logic.get_events_list(db)
        if not events:
            return OfflineEventsRatio(offline_events_ratio=0.0)
        offline_events = [event for event in events if event.is_offline]
        return OfflineEventsRatio(
            offline_events_ratio=len(offline_events) / len(events)
        )
    except user_errors.UserNotFoundError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e
    except user_errors.AdminRoleRequiredError as e:
        raise HTTPException(status_code=403, detail=str(e)) from e
