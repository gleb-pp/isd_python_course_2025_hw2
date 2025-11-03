from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class EventID(BaseModel):
    """Unique identifier for an event."""

    event_id: UUID


class EventMainInfo(EventID):
    """Main information about an event."""

    title: str
    description: str | None
    date: datetime
    is_offline: bool
    location: str
    organizator_email: str
    max_participants: int | None
    participants_registered: int = 0


class EventFullInfo(EventMainInfo):
    """Full information about an event, including participants' emails."""

    participants_emails: list[str]
