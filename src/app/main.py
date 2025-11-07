from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

import src.app.presentation.admins
import src.app.presentation.bookings
import src.app.presentation.events
import src.app.presentation.metrics
import src.app.presentation.users
from src.app.db import create_tables

app = FastAPI(
    title="Event Booking System",
    version="1.0",
)
app.include_router(src.app.presentation.users.router)
app.include_router(src.app.presentation.events.router)
app.include_router(src.app.presentation.admins.router)
app.include_router(src.app.presentation.bookings.router)
app.include_router(src.app.presentation.metrics.router)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Create database tables on application startup."""
    create_tables()
    yield
