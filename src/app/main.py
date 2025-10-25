import presentation.admins
import presentation.events
import presentation.users
from fastapi import FastAPI

app = FastAPI(
    title="Event Booking System",
    version="1.0",
)
app.include_router(presentation.users.router)
app.include_router(presentation.events.router)
app.include_router(presentation.admins.router)
