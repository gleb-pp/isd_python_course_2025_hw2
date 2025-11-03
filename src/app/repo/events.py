from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from src.app.repo.base import Base

class Event(Base):
    __tablename__ = 'events'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(80), nullable=False)
    description = Column(Text, nullable=True)
    date = Column(DateTime, nullable=False)
    is_offline = Column(Boolean, default=True, nullable=False)
    location = Column(String(200), nullable=False)
    organizer_email = Column(String(254), ForeignKey('users.email'), nullable=False)
    max_participants = Column(Integer, nullable=True)

    organizer = relationship("User", back_populates="organized_events")
