from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from src.app.repo.base import Base


class User(Base):
    __tablename__ = 'users'
    
    email = Column(String(254), primary_key=True, unique=True, nullable=False)
    name = Column(String(80), nullable=False)
    password_hash = Column(String(128), nullable=False)

    organized_events = relationship("Event", back_populates="organizer")
    bookings = relationship("Booking", back_populates="user")
