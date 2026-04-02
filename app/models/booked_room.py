from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base


class BookedRoom(Base):
    __tablename__ = "booked_rooms"

    id = Column(Integer, primary_key=True)

    booking_id = Column(Integer, ForeignKey("bookings.booking_id"))
    room_id = Column(Integer, ForeignKey("rooms.room_id"))

    no_room = Column(Integer)

    booking = relationship("Booking", back_populates="booked_rooms")
    room = relationship("Room", back_populates="booked_rooms")