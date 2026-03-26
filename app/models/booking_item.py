from sqlalchemy import Column, Integer, ForeignKey, Date
from sqlalchemy.orm import relationship
from database.database import Base


class BookingItem(Base):
    __tablename__ = "booking_items"

    booking_item_id = Column(Integer, primary_key=True)

    booking_id = Column(Integer, ForeignKey("bookings.booking_id"))
    room_id = Column(Integer, ForeignKey("rooms.room_id"))

    quantity = Column(Integer)

    check_in = Column(Date)
    check_out = Column(Date)

    booking = relationship("Booking", back_populates="items")
    room = relationship("Room", back_populates="booking_items")