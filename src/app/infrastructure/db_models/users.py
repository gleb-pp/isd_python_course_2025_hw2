from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.infrastructure.db_models.base import Base


class UserDB(Base):
    """Database model for the users."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(254), primary_key=True, unique=True, nullable=False
    )
    name = Column(String(80), nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)

    organized_events = relationship("Event", back_populates="organizer")
    bookings = relationship("Booking", back_populates="user")
