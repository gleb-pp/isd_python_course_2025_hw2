class EventException(Exception):
    """Base exception for event-related errors."""
    pass


class EventNotFoundError(EventException):
    """Exception raised when an event is not found."""

    def __init__(self, event_id: int) -> None:
        super().__init__(f"Event {event_id} not found.")


class OrginizatorRoleRequiredError(EventException):
    """Exception raised when the user does not have the organizer role for the event."""

    def __init__(self, event_id: int, user_email: str) -> None:
        super().__init__(f"User {user_email} is not the organizer for event {event_id}.")
