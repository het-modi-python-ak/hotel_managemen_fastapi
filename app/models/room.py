from sqlalchemy import Column, Integer, Float, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database.database import Base
from app.models.room_type import RoomType


class Room(Base):

    __tablename__ = "rooms"

    room_id = Column(Integer, primary_key=True, index=True)

    hotel_id = Column(Integer, ForeignKey("hotels.hotel_id"))

    room_type = Column(Enum(RoomType))

    price = Column(Float)

    total_rooms = Column(Integer)

    __table_args__ = (
        UniqueConstraint("hotel_id", "room_type"),
    )

    hotel = relationship("Hotel", back_populates="rooms")

    booking_items = relationship("BookingItem", back_populates="room")