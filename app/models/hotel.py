
from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from database.database import Base
from models.room import Room

class Hotel(Base):
    __tablename__ = "hotels"

    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    name = Column(String(30))
    address = Column(String(50))
    city = Column(String(30))
    state = Column(String(30))
    country = Column(String(30))

    rating = Column(Float)

    owner = relationship("User", back_populates="hotels")
    rooms = relationship("Room", back_populates="hotel")
    bookings = relationship("Booking", back_populates="hotel")

