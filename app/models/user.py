from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database.database import Base
from models.rbac import user_roles

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True)
    phone = Column(String)
    password = Column(String)
    created_at = Column(DateTime, default=datetime.now)

    roles = relationship("Role", secondary=user_roles, back_populates="users")

    hotels = relationship("Hotel", back_populates="owner")
    bookings = relationship("Booking", back_populates="user")