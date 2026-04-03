from sqlalchemy import Column, Integer, ForeignKey, DateTime, String,Date
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.database import Base


class Booking(Base):

    __tablename__ = "bookings"

    booking_id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    hotel_id = Column(Integer, ForeignKey("hotels.hotel_id"))
    no_of_people =Column(Integer)
    check_in = Column(Date)
    check_out = Column(Date)


    status = Column(String(30), default="pending")

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="bookings")
   
    hotel = relationship("Hotel", back_populates="bookings")

    items = relationship("BookingItem", back_populates="booking")
