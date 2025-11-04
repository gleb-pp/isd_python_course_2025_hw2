from pydantic import BaseModel, ConfigDict


class EventParticipants(BaseModel):
    """The list of event's participants."""

    participants_emails: list[str]
    model_config = ConfigDict(from_attributes=True)


class Booking(BaseModel):
    """Booking model."""

    event_id: int
    user_email: str
    model_config = ConfigDict(from_attributes=True)
