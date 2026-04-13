# from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, UniqueConstraint
# from sqlalchemy.orm import relationship
# from datetime import datetime
# from app.database.database import Base 

# class Airport(Base):
#     __tablename__ = "airports"
#     id= Column(Integer, primary_key=True, index=True)
#     code = Column(String(100), unique=True, index=True)
#     name = Column(String(100))
#     location = Column(String(100))
#     country = Column(String(100))
    
    
#     departures = relationship("Flight", foreign_keys="Flight.source_id", back_populates="source")
#     arrivals = relationship("Flight", foreign_keys="Flight.destination_id", back_populates="destination")


# class Flight(Base):
#     __tablename__ = "flights" 
#     flight_id = Column(Integer, primary_key=True, index=True)
#     created_by = Column(Integer, ForeignKey("users2.id"))
#     flight_number = Column(String(100), unique=True, index=True)
#     source_id = Column(Integer, ForeignKey("airports.id"))
#     destination_id = Column(Integer, ForeignKey("airports.id"))
#     depart_time = Column(DateTime)
#     arrival_time = Column(DateTime)
    
    
#     source = relationship("Airport", foreign_keys=[source_id], back_populates="departures")
#     destination = relationship("Airport", foreign_keys=[destination_id], back_populates="arrivals")
#     seats = relationship("Seat", back_populates="flight")
#     bookings = relationship("FlightBooking", back_populates="flight")


# class Seat(Base):
#     __tablename__ = "seats"
#     seat_id = Column(Integer, primary_key=True, index=True) 
#     flight_id = Column(Integer, ForeignKey("flights.flight_id"))  
#     seat_number = Column(String(50))
#     seat_class = Column(String(50))
#     is_booked = Column(Boolean, default=False)
#     price = Column(Integer)

#     __table_args__ = (UniqueConstraint("flight_id", "seat_number", name="unique_seat_per_flight"),)

#     flight = relationship("Flight", back_populates="seats") # 
#     allocations = relationship("SeatAllocation", back_populates="seat",cascade="all, delete")


# class FlightBooking(Base):
#     __tablename__ = "flight_bookings"
#     booking_id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey("users2.id"))
#     seat_id = Column(Integer, ForeignKey("seats.seat_id"))
#     flight_id = Column(Integer, ForeignKey("flights.flight_id"))
#     status = Column(String(50), default="pending")
#     total_price = Column(Integer)
#     created_at = Column(DateTime, default=datetime.now()) 

#     passengers = relationship("Passenger", back_populates="booking")
#     flight = relationship("Flight", back_populates="bookings")



# class Passenger(Base):
#     __tablename__ = "passengers"
#     passenger_id = Column(Integer, primary_key=True, index=True)
#     booking_id = Column(Integer, ForeignKey("flight_bookings.booking_id"))
#     name = Column(String(50))
#     age = Column(Integer)

#     booking = relationship("FlightBooking", back_populates="passengers")
#     seat_allocation = relationship("SeatAllocation", back_populates="passenger", uselist=False)



# class SeatAllocation(Base):
#     __tablename__ = "seat_allocations"
#     id = Column(Integer, primary_key=True) #
#     seat_id = Column(Integer, ForeignKey("seats.seat_id") )
#     passenger_id = Column(Integer, ForeignKey("passengers.passenger_id")) # 

#     passenger = relationship("Passenger", back_populates="seat_allocation")
#     seat = relationship("Seat", back_populates="allocations")








from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.database import Base


class Airline(Base):
    __tablename__ = "airlines"

    airline_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True)
    country = Column(String(100))
    created_by = Column(Integer, ForeignKey("users2.id"))
    created_at = Column(DateTime,default=datetime.now())
    updated_at = Column(DateTime,default=datetime.now())


    airplanes = relationship("Airplane", back_populates="airline")


class Airport(Base):
    __tablename__ = "airports"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(100), unique=True, index=True)
    name = Column(String(100))
    location = Column(String(100))
    country = Column(String(100))
    created_by = Column(Integer, ForeignKey("users2.id"))
    created_at = Column(DateTime,default=datetime.now())
    updated_at = Column(DateTime,default=datetime.now())



    departures = relationship("Flight", foreign_keys="Flight.source_id", back_populates="source")
    arrivals = relationship("Flight", foreign_keys="Flight.destination_id", back_populates="destination")


class Airplane(Base):
    __tablename__ = "airplanes"

    airplane_id = Column(Integer, primary_key=True, index=True)
    model = Column(String(100))
    total_seats = Column(Integer)
    airline_id = Column(Integer, ForeignKey("airlines.airline_id"))
    created_by = Column(Integer, ForeignKey("users2.id"))
    created_at = Column(DateTime,default=datetime.now())
    updated_at = Column(DateTime,default=datetime.now())


    airline = relationship("Airline", back_populates="airplanes")
    seat_templates = relationship("AirplaneSeat", back_populates="airplane")
    flights = relationship("Flight", back_populates="airplane")


class AirplaneSeat(Base):
    __tablename__ = "airplane_seats"

    id = Column(Integer, primary_key=True)
    airplane_id = Column(Integer, ForeignKey("airplanes.airplane_id"))
    seat_number = Column(String(10))
    seat_class = Column(String(50))
    created_by = Column(Integer, ForeignKey("users2.id"))
    created_at = Column(DateTime,default=datetime.now())
    updated_at = Column(DateTime,default=datetime.now())

    airplane = relationship("Airplane", back_populates="seat_templates")
    


class Flight(Base):
    __tablename__ = "flights"

    flight_id = Column(Integer, primary_key=True, index=True)
    created_by = Column(Integer, ForeignKey("users2.id"))

    airplane_id = Column(Integer, ForeignKey("airplanes.airplane_id"))

    flight_number = Column(String(100), unique=True, index=True)

    source_id = Column(Integer, ForeignKey("airports.id"))
    destination_id = Column(Integer, ForeignKey("airports.id"))

    depart_time = Column(DateTime)
    arrival_time = Column(DateTime)
    created_by = Column(Integer, ForeignKey("users2.id"))
    created_at = Column(DateTime,default=datetime.now())
    updated_at = Column(DateTime,default=datetime.now())
    

    airplane = relationship("Airplane", back_populates="flights")

    source = relationship("Airport", foreign_keys=[source_id], back_populates="departures")
    destination = relationship("Airport", foreign_keys=[destination_id], back_populates="arrivals")

    seats = relationship("FlightSeat", back_populates="flight")
    bookings = relationship("FlightBooking", back_populates="flight")


class FlightSeat(Base):
    __tablename__ = "flight_seats"

    seat_id = Column(Integer, primary_key=True, index=True)
    flight_id = Column(Integer, ForeignKey("flights.flight_id"))

    seat_number = Column(String(100))
    seat_class = Column(String(50))
    price = Column(Integer)

    is_booked = Column(Boolean, default=False)
    created_by = Column(Integer, ForeignKey("users2.id"))
    created_at = Column(DateTime,default=datetime.now())
    updated_at = Column(DateTime,default=datetime.now())

    flight = relationship("Flight", back_populates="seats")
    allocations = relationship("SeatAllocation", back_populates="seat")


class FlightBooking(Base):
    __tablename__ = "flight_bookings"

    booking_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users2.id"))
    flight_id = Column(Integer, ForeignKey("flights.flight_id"))
    seat_number = Column(String(10))
    status = Column(String(50), default="pending")
    total_price = Column(Integer)
    reminder_sent = Column(Boolean,default=False)

    created_by = Column(Integer, ForeignKey("users2.id"))
    created_at = Column(DateTime,default=datetime.now())
    updated_at = Column(DateTime,default=datetime.now())
    
    
    passengers = relationship("Passenger", back_populates="booking")
    flight = relationship("Flight", back_populates="bookings")
























class Passenger(Base):
    __tablename__ = "passengers"

    passenger_id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("flight_bookings.booking_id"))

    name = Column(String(50))
    age = Column(Integer)

    booking = relationship("FlightBooking", back_populates="passengers")
    seat_allocation = relationship("SeatAllocation", back_populates="passenger", uselist=False)


class SeatAllocation(Base):
    __tablename__ = "seat_allocations"

    id = Column(Integer, primary_key=True)

    seat_id = Column(Integer, ForeignKey("flight_seats.seat_id"))
    passenger_id = Column(Integer, ForeignKey("passengers.passenger_id"))

    passenger = relationship("Passenger", back_populates="seat_allocation")
    seat = relationship("FlightSeat", back_populates="allocations")