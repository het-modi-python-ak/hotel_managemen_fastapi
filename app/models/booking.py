
from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from datetime import datetime
from database.database import Base


class Booking(Base):
    __tablename__ = "bookings"

    booking_id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    hotel_id = Column(Integer, ForeignKey("hotels.hotel_id"))

    status = Column(String(30), default="confirmed")

    created_at = Column(DateTime, default=datetime.now())

    user = relationship("User", back_populates="bookings")
    hotel = relationship("Hotel", back_populates="bookings")
    items = relationship("BookingItem", back_populates="booking")