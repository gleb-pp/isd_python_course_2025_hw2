class BookingException(Exception):
    """Base exception for booking-related errors."""
    pass


class EventFullError(BookingException):
    """Exception raised when trying to book an event that is already full."""

    def __init__(self, event_id: int) -> None:
        super().__init__(f"Event {event_id} is full. No available places left.")
