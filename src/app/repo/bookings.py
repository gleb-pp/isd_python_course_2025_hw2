from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from src.app.repo.base import Base

class Booking(Base):
    __tablename__ = 'bookings'

    event_id = Column(Integer, ForeignKey('events.id'), primary_key=True)
    user_email = Column(String(254), ForeignKey('users.email'), primary_key=True)

    event = relationship("Event", back_populates="bookings")
    user = relationship("User", back_populates="bookings")
