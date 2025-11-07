from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import src.app.domain.exceptions.users as user_errors
from src.app.auth import get_current_user
from src.app.db import get_db
from src.app.services.metrics import MetricsService
from src.app.services.models.metrics import (
    AverageBookingsPerUser,
    AverageRegistrations,
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
    service = MetricsService(db)
    try:
        return service.get_top_registrations_events(admin_email, events_number)
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
    service = MetricsService(db)
    try:
        return service.get_average_registrations(admin_email)
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
    service = MetricsService(db)
    try:
        return service.get_average_bookings_per_user(admin_email)
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
    service = MetricsService(db)
    try:
        return service.get_offline_events_ratio(admin_email)
    except user_errors.UserNotFoundError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e
    except user_errors.AdminRoleRequiredError as e:
        raise HTTPException(status_code=403, detail=str(e)) from e
