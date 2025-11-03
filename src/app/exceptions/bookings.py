from uuid import UUID


class BookingError(Exception):
    """Base exception for booking-related errors."""


class EventFullError(BookingError):
    """Exception raised when trying to book an event that is already full."""

    def __init__(self, event_id: UUID) -> None:
        super().__init__(f"Event {event_id} is full. No available places left.")
