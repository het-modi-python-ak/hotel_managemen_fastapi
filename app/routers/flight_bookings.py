from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.database.database import get_db
from app.models.flight_models import Flight,Airport,FlightBooking,AirplaneSeat,FlightSeat
from app.core.dependencies import get_current_user
from datetime import datetime,timezone
from typing import List
from app.schemas.schemas import FlightBookingreposnse


router = APIRouter()

@router.post("/",response_model=FlightBookingreposnse)
def book_seat(flight_id:int,seat_number:str,db:Session=Depends(get_db),current_user = Depends(get_current_user)):
    try:
        flight = db.query(Flight).filter(Flight.flight_id==flight_id).first()

        if not flight:
            raise HTTPException(status_code=404,detail="No flight found with this id")

        
        seat = db.query(FlightSeat).filter(FlightSeat.seat_number==seat_number).first()

        if not seat:
            raise HTTPException(status_code=404,detail="No seats found with this number")

        if seat.is_booked != 0 :
            raise HTTPException(status_code=404,detail="Seat not available for now")
        
        
        booking = FlightBooking( flight_id=flight_id,user_id = current_user.id , seat_number = seat_number,total_price =  seat.price,created_by=current_user.id)
        seat.is_booked=True
        
        db.add(booking)
        db.commit()
        
        return booking

        
    except SQLAlchemyError as e:

        raise HTTPException(status_code=404,detail=f"Database error : {e}" )




@router.post("/book-multiple")
def book_multiple_seats(
    flight_id: int,
    seat_numbers: List[str],  
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
       
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
def get_all_bookings(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
  
    try:
        bookings = db.query(FlightBooking).filter(FlightBooking.created_by == current_user.id).all()
        return bookings
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")



#delete booking 
@router.delete("/bookings/{booking_id}")
def delete_booking(booking_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    
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