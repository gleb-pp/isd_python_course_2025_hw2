from pydantic import BaseModel


class EventParticipants(BaseModel):
    """The list of event's participants."""

    participants_emails: list[str]


class Booking(BaseModel):
    """Booking model."""

    event_id: int
    user_email: str
