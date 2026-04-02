from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base


class Hotel(Base):

    __tablename__ = "hotels"

    hotel_id = Column(Integer, primary_key=True)

    name = Column(String(100))
    address = Column(String(255))
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100))

    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="hotels")

    rooms = relationship("Room", back_populates="hotel")

    bookings = relationship("Booking", back_populates="hotel")