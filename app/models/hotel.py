from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from database.database import Base

class Hotel(Base):
    __tablename__ = "hotels"

    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    name = Column(String)
    address = Column(String)
    city = Column(String)
    state = Column(String)
    country = Column(String)

    rating = Column(Float)

    owner = relationship("User", back_populates="hotels")
    rooms = relationship("Room", back_populates="hotel")
    bookings = relationship("Booking", back_populates="hotel")
