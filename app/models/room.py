
from sqlalchemy import Column, Integer, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from database.database import Base
from models.room_type import RoomType


class Room(Base):
    __tablename__ = "rooms"

    room_id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.hotel_id"))

    room_type = Column(Enum(RoomType))
    price = Column(Float)

    total_rooms = Column(Integer)

    hotel = relationship("Hotel", back_populates="rooms")
    booking_items = relationship("BookingItem", back_populates="room")
