from sqlalchemy import Column, Integer, ForeignKey, Date, String, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database.database import Base

class Booking(Base):
    __tablename__ = "bookings"

    booking_id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    hotel_id = Column(Integer, ForeignKey("hotels.id"))

    total_room = Column(Integer)
    no_of_people = Column(Integer)

    check_in = Column(Date)
    check_out = Column(Date)

    total_price = Column(Float)

    status = Column(String, default="pending")

    created_at = Column(DateTime, default=datetime.now)

    user = relationship("User", back_populates="bookings")
    hotel = relationship("Hotel", back_populates="bookings")

    booked_rooms = relationship("BookedRoom", back_populates="booking")