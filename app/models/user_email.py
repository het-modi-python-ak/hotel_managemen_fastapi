
from sqlalchemy import Column, Integer, String, DateTime,ForeignKey,Float,Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.database import Base
from app.models.association import user_roles
from app.models.hotel import Hotel
from app.models.booking import Booking

class User2(Base):
    __tablename__ = "users2"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(30))
    email = Column(String(30), unique=True)
    phone = Column(String(10))
    password = Column(String(255))
    created_at = Column(DateTime, default=datetime.now)
    is_verified = Column(Boolean,default=False)

    # roles = relationship("Role", secondary=user_roles, back_populates="users") #many to many

 
    # hotels = relationship("Hotel", back_populates="owner") #one to many
    # bookings = relationship("Booking", back_populates="user") #one t many

    # showing error in this erro 


