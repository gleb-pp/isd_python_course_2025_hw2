from sqlalchemy.orm import Session

from src.app.infrastructure.adapters.events_adapter import EventsAdapter
from src.app.infrastructure.adapters.metrics_adapter import MetricsAdapter
from src.app.infrastructure.adapters.users_adapter import UsersAdapter
from src.app.services.models.metrics import (
    AverageBookingsPerUser,
    AverageRegistrations,
    EventRegistrations,
    OfflineEventsRatio,
    TopRegistrationsMetric,
)


class MetricsService:
    """Service layer for the Metrics."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.events = EventsAdapter(db)
        self.users = UsersAdapter(db)
        self.metrics = MetricsAdapter(db)

    def get_top_registrations_events(
        self, admin_email: str, events_number: int
    ) -> TopRegistrationsMetric:
        """Get the list of N most popular events with the biggest number of bookings."""
        user = self.users.get_user(admin_email)
        self.users.assert_user_is_admin(user)
        events = self.events.get_events_list()
        events_registrations = [
            EventRegistrations(
                event_id=event.id,
                registrations=self.metrics.get_event_registrations(event),
            )
            for event in events
        ]
        return TopRegistrationsMetric(
            events=sorted(
                events_registrations, key=lambda e: e.registrations, reverse=True
            )[:events_number]
        )

    def get_average_registrations(self, admin_email: str) -> AverageRegistrations:
        """Get the average number of bookings per event."""
        user = self.users.get_user(admin_email)
        self.users.assert_user_is_admin(user)
        events = self.events.get_events_list()
        if not events:
            return AverageRegistrations(average_registrations=0.0)
        events_registrations = [
            self.metrics.get_event_registrations(event) for event in events
        ]
        return AverageRegistrations(
            average_registrations=sum(events_registrations) / len(events_registrations)
        )

    def get_average_bookings_per_user(self, admin_email: str) -> AverageBookingsPerUser:
        """Get the average number of bookings per user."""
        admin = self.users.get_user(admin_email)
        self.users.assert_user_is_admin(admin)
        users = self.users.get_all_users()
        if not users:
            return AverageBookingsPerUser(average_bookings_per_user=0.0)
        users_bookings = [self.metrics.get_user_bookings(user) for user in users]
        return AverageBookingsPerUser(
            average_bookings_per_user=sum(users_bookings) / len(users_bookings)
        )

    def get_offline_events_ratio(self, admin_email: str) -> OfflineEventsRatio:
        """Get the percentage of offline events among all events."""
        admin = self.users.get_user(admin_email)
        self.users.assert_user_is_admin(admin)
        events = self.events.get_events_list()
        if not events:
            return OfflineEventsRatio(offline_events_ratio=0.0)
        offline_events = [event for event in events if event.is_offline]
        return OfflineEventsRatio(
            offline_events_ratio=len(offline_events) / len(events)
        )
