from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship
from database.database import Base
from models.booked_room import BookedRoom

class Room(Base):
    __tablename__ = "rooms"

    room_id = Column(Integer, primary_key=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id"))

    room_number = Column(String(30))
    room_type = Column(String(30))
    price = Column(Float)

    is_available = Column(Boolean, default=True)

    hotel = relationship("Hotel", back_populates="rooms")
    booked_rooms = relationship("BookedRoom", back_populates="room")
