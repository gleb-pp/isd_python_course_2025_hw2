from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class EventID(BaseModel):
    """Unique identifier for an event."""

    id: int
    model_config = ConfigDict(from_attributes=True)


class EventBase(BaseModel):
    """Base event information."""

    title: Annotated[str, Field(min_length=3, max_length=80)]
    description: Annotated[
        str | None, Field(default=None, min_length=3, max_length=1000)
    ]
    date: datetime
    is_offline: bool
    location: Annotated[str, Field(min_length=3, max_length=200)]
    max_participants: Annotated[int | None, Field(default=None, gt=0)] = None


class EventInfo(EventBase, EventID):
    """Main information about an event."""

    organizer_email: str
    model_config = ConfigDict(from_attributes=True)
