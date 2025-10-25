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
    organizator_email: str
    max_number_of_participants: int
    participants_registered: int


class EventFullInfo(EventMainInfo):
    """Full information about an event, including participants' emails."""

    participants_emails: list[str]
