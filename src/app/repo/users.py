from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    email = Column(String(254), primary_key=True, unique=True, nullable=False)
    name = Column(String(80), nullable=False)
    password_hash = Column(String(128), nullable=False)
