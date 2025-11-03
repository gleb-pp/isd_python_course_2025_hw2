from fastapi import FastAPI

import src.app.presentation.admins
import src.app.presentation.events
import src.app.presentation.users
import src.app.presentation.bookings
from src.app.db import create_tables

app = FastAPI(
    title="Event Booking System",
    version="1.0",
)
app.include_router(src.app.presentation.users.router)
app.include_router(src.app.presentation.events.router)
app.include_router(src.app.presentation.admins.router)
app.include_router(src.app.presentation.bookings.router)

@app.on_event("startup")
def startup_event():
    create_tables()
