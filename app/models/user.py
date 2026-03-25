
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database.database import Base
from models.association import user_roles


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(30))
    email = Column(String(30), unique=True)
    phone = Column(String(10))
    password = Column(String(30))
    created_at = Column(DateTime, default=datetime.now)

    roles = relationship("Role", secondary=user_roles, back_populates="users") #many to many

 
    hotels = relationship("Hotel", back_populates="owner") #one to many
    bookings = relationship("Booking", back_populates="user") #one t many
    
