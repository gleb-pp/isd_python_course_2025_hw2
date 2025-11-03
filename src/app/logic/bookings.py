from uuid import UUID
from src.app.repo.events import Event
from src.app.repo.bookings import Booking
from sqlalchemy.orm import Session
import src.app.exceptions.events as event_errors
import src.app.exceptions.bookings as booking_errors

def create_booking(event_id: UUID, user_email: str, db: Session) -> None:
    """Register the user with provided email to the event with provided event_id."""

    # check if event exists
    event = db.query(Event).filter_by(id=event_id).first()
    if event is None:
        raise event_errors.EventNotFoundError(event_id)
    
    # check if there are available seats
    if event.max_participants is not None:
        current_participants = db.query(Booking).filter_by(event_id=event_id).count()
        if current_participants >= event.max_participants:
            raise booking_errors.EventFullError(event_id)
    
    # check if user is already registered
    existing_booking = db.query(Booking).filter_by(event_id=event_id, user_email=user_email).first()
    if existing_booking is not None:
        return
    
    # create booking
    new_booking = Booking(event_id=event_id, user_email=user_email)
    db.add(new_booking)


def delete_booking(event_id: UUID, user_email: str, db: Session) -> None:
    """Unregister the user with provided email from the event with provided event_id."""

    # check if event exists
    event = db.query(Event).filter_by(id=event_id).first()
    if event is None:
        raise event_errors.EventNotFoundError(event_id)

    # check if booking exists
    booking = db.query(Booking).filter_by(event_id=event_id, user_email=user_email).first()
    if booking is None:
        return
    
    # delete booking
    db.delete(booking)


def get_event_participants(event_id: UUID, user_email: str, db: Session) -> list[str]:
    """Get the list of user emails registered for the event with provided event_id"""

    # check if event exists
    event = db.query(Event).filter_by(id=event_id).first()
    if event is None:
        raise event_errors.EventNotFoundError(event_id)
    
    # check if user is the organizer
    if event.organizator_email != user_email:
        raise event_errors.OrginizatorRoleRequiredError(event_id, user_email)
    
    # get list of participants
    bookings = db.query(Booking).filter_by(event_id=event_id).all()
    participant_emails = [booking.user_email for booking in bookings]
    return participant_emails
