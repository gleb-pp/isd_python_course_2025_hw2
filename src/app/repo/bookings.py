from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.repo.base import Base


class Booking(Base):
    """Database model for the bookings."""

    __tablename__ = "bookings"

    event_id = Column(Integer, ForeignKey("events.id"), primary_key=True)
    user_email: Mapped[str] = mapped_column(
        String(254), ForeignKey("users.email"), primary_key=True
    )

    event = relationship("Event", back_populates="bookings")
    user = relationship("User", back_populates="bookings")
