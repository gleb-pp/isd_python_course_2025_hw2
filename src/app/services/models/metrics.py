from pydantic import BaseModel


class EventRegistrations(BaseModel):
    """The metric calculated as number of bookings."""

    event_id: int
    registrations: int


class TopRegistrationsMetric(BaseModel):
    """The metric of N most popular events."""

    events: list[EventRegistrations]


class AverageRegistrations(BaseModel):
    """The metric of the average number of bookings per event."""

    average_registrations: float


class AverageBookingsPerUser(BaseModel):
    """The metric of the average number of bookings per user."""

    average_bookings_per_user: float


class OfflineEventsRatio(BaseModel):
    """The percentage of offline events among all events."""

    offline_events_ratio: float
