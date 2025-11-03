from sqlalchemy import Column, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.repo.base import Base


class User(Base):
    """Database model for the users."""

    __tablename__ = "users"

    email = Column(String(254), primary_key=True, unique=True, nullable=False)
    name = Column(String(80), nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)

    organized_events = relationship("Event", back_populates="organizer")
    bookings = relationship("Booking", back_populates="user")
