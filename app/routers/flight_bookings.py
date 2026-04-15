from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.database.database import get_db
from app.models.flight_models import Flight,Airport,FlightBooking,AirplaneSeat,FlightSeat
from app.core.dependencies import get_current_user
from datetime import datetime,timezone
from typing import List
from app.schemas.schemas import FlightBookingreposnse
from app.services.email_service import send_reminder_email
from app.tasks.reminder_tasks import send_booking_reminder
from app.models.user_email import User2
from app.core.redis_client import redis_client
import json
from typing import Annotated
from app.models.user import User

SessionDep = Annotated[Session, Depends(get_db)]
CurretUser = Annotated[User,Depends(get_current_user)]


router = APIRouter()

@router.get("/time")
def get_current_time():
    return datetime.now()



from pydantic import BaseModel
from app.schemas.schemas import Bookseats
    
    
@router.post("/")
def book_multiple_seats(
    # flight_id: int,
    # seat_numbers: List[str], 
    data : Bookseats, 
    db: SessionDep,
    current_user:CurretUser
):
    try:
        flight_id = data.flight_id
        seat_numbers = data.seat_numbers
    
        
       
        flight = db.query(Flight).filter(Flight.flight_id == flight_id).first()
        if not flight:
            raise HTTPException(status_code=404, detail="Flight not found")

        
        seats_to_book = []
        total_price = 0

        # 
        for seat_num in seat_numbers:
            seat = db.query(FlightSeat).filter(
                FlightSeat.flight_id == flight_id,
                FlightSeat.seat_number == seat_num
            ).first()

            if not seat:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Seat {seat_num} not found on this flight"
                )
            
            if seat.is_booked != 0:
                raise HTTPException(
                    status_code=400,  
                    detail=f"Seat {seat_num} is already booked"
                )
            
            seats_to_book.append(seat)
            total_price += seat.price

        booking = FlightBooking(
            flight_id=flight_id,
            user_id=current_user.id,
            seat_number=",".join(seat_numbers), # 
            total_price=total_price,
            created_by=current_user.id
        )
        db.add(booking)
        
       
        for seat in seats_to_book:
            seat.is_booked = True

        db.commit()

        return {
            "message": "Seats booked successfully",
            "booking_id": booking.booking_id,
            "flight_id":booking.flight_id,
            "seats": seat_numbers,
            "total_price": total_price
        }

    except SQLAlchemyError as e:
        db.rollback()  
        raise HTTPException(
            status_code=500, 
            detail=f"Database error: {str(e)}"
        )




@router.get("/{flight_id}/seat")
def get_available_seat(flight_id:int,db:Session=Depends(get_db)):
    try:
        seats = db.query(FlightSeat).filter(FlightSeat.flight_id==flight_id).all()
    
    
        if not seats :
            raise HTTPException(status_code=404,detail="No seats found for flight")

        return seats
   
   
    except SQLAlchemyError:
        raise HTTPException(status_code=404, detail="Database error ")
    
    
    
    
#get my booking
@router.get("/bookings")
def get_all_bookings(db: SessionDep, current_user:CurretUser):
  
    try:
        bookings = db.query(FlightBooking).filter(FlightBooking.created_by == current_user.id).all()
        return bookings
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")



#delete booking 
@router.delete("/bookings/{booking_id}")
def delete_booking(booking_id: int, db: SessionDep, current_user:CurretUser):
    
    try:
        #find the flight 
        booking = db.query(FlightBooking).filter(
            FlightBooking.booking_id == booking_id,
            FlightBooking.created_by == current_user.id
        ).first()

        seats_to_release = booking.seat_number if isinstance(booking.seat_number, list) else booking.seat_number.split(',')
        
        for s in seats_to_release:
            seat = db.query(FlightSeat).filter(
                FlightSeat.flight_id == booking.flight_id,
                FlightSeat.seat_number == s.strip()
            ).first()
            if seat:
                seat.is_booked = False
        

        # if not booking:
        #     raise HTTPException(status_code=404, detail="Booking not found or unauthorized")

        # #unbooked the all seat 
        
        # # seat_number = [B1,B2,B3]
        
        # for book in booking:
        #     seat = db.query(FlightSeat).filter(FlightSeat.flight_id == book.flight_id,FlightSeat.seat_number== book.seat_number).first()
        #     seat.is_booked = False

            
           
            
            
        # for book in booking:
        #     db.delete(book)


        
        
        
        
        # seat = db.query(FlightSeat).filter(
        #     FlightSeat.flight_id == booking.flight_id,
        #     FlightSeat.seat_number == booking.seat_number
        # ).all()
        
        
        # for s in seat:
        #     print(s)
        #     s.is_booked = False
        
        # db.delete(booking)
        db.delete(booking)
        db.commit()
        
        return {"message": "Booking deleted successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    
    
    
 
class UpdateSeat(BaseModel):
    booking_id: int 
    old_seat_number: str 
    new_seat_number: str
        

#update booking
@router.put("/bookings/{booking_id}/swap-seat")
def swap_single_seat(
    # booking_id: int, 
    # old_seat_number: str, 
    # new_seat_number: str, 
    data : UpdateSeat,
    db: SessionDep, 
    current_user = Depends(get_current_user)
):
    try:
        
        booking_id = data.booking_id
        old_seat_number = data.old_seat_number
        new_seat_number = data.new_seat_number
        
        # Fetch the booking
        booking = db.query(FlightBooking).filter(
            FlightBooking.booking_id == booking_id,
            FlightBooking.user_id == current_user.id
        ).first()

        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        #  Parse existing seats
        # Assuming seat_number is stored as "A1,A2,A3"
        current_seats = [s.strip() for s in booking.seat_number.split(",")]

        if old_seat_number not in current_seats:
            raise HTTPException(status_code=400, detail=f"Seat {old_seat_number} is not part of this booking")

        #  Check if the new seat is available
        new_seat = db.query(FlightSeat).filter(
            FlightSeat.flight_id == booking.flight_id,
            FlightSeat.seat_number == new_seat_number
        ).first()

        if not new_seat:
            raise HTTPException(status_code=404, detail="New seat not found")
        
        if new_seat.is_booked:
            raise HTTPException(status_code=400, detail="New seat is already occupied")

        #  Release the OLD seat
        old_seat = db.query(FlightSeat).filter(
            FlightSeat.flight_id == booking.flight_id,
            FlightSeat.seat_number == old_seat_number
        ).first()
        if old_seat:
            old_seat.is_booked = False

        #  Occupy the NEW seat
        new_seat.is_booked = True

        # Update the booking string 

        updated_seats = [new_seat_number if s == old_seat_number else s for s in current_seats]
        
        # Calculate price difference
        price_diff = new_seat.price - old_seat.price
        booking.total_price += price_diff
        booking.seat_number = ",".join(updated_seats)

        db.commit()
        db.refresh(booking)

        return {
            "message": f"Swapped {old_seat_number} for {new_seat_number}",
            "updated_booking_id": booking.booking_id,
            "current_seats": booking.seat_number,
            "new_total_price": booking.total_price
        }

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
