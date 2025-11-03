from datetime import datetime

from pydantic import BaseModel


class EventID(BaseModel):
    """Unique identifier for an event."""

    event_id: int


class EventInfo(EventID):
    """Main information about an event."""

    title: str
    description: str | None
    date: datetime
    is_offline: bool
    location: str
    organizer_email: str
    max_participants: int | None

    class Config:
        """ORM mode configuration."""

        from_attributes = True
