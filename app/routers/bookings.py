from fastapi import APIRouter, Depends, HTTPException,Header
from sqlalchemy.orm import Session
from database.database import get_db
from models.booking import Booking
from models.hotel import Hotel
from core.dependencies import get_current_user
from datetime import date,datetime,timedelta
from typing import Annotated
from enum import Enum
from models.room import Room
from sqlalchemy import func



router = APIRouter()


#count booking overlaping dates 



@router.post("/") # Endpoint changed to '/' as prefix is set
def create_booking(
    hotel_id: int,
    total_room: int,
    no_of_people: int,
    check_in: date,
    check_out: date,
    # total_price: float,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
    room = db.query(Room).filter(Room.hotel_id==hotel_id).first()
    

    if not hotel:
        
        raise HTTPException(status_code=404, detail="Hotel not found")

    booking = Booking(
        user_id=current_user.id,
        hotel_id=hotel_id,
        total_room=total_room,
        no_of_people=no_of_people,
        check_in=check_in,
        check_out=check_out,
        total_price=no_of_people*total_room*room.price
    )

    db.add(booking)
    db.commit()
    db.refresh(booking)

    return booking




#update booking 
class BookingStatus(str, Enum):
    confirm = "confirmed"
    cancell = "cancelled"
    


@router.patch("/{booking_id}")
def update_booking_status(
    booking_id: int, 
    
    status: Annotated[BookingStatus, Header()], 
    db: Session = Depends(get_db),
    current_user= Depends(get_current_user)
):
    
   
    booking = db.query(Booking).filter(Booking.booking_id == booking_id,Booking.user_id ==current_user.id).first()

   
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    booking.status = status.value
    db.commit()
    db.refresh(booking)
    
    return booking


# #get booking 


@router.get("/")
def get_my_bookings(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    bookings = db.query(Booking).filter(
        Booking.user_id == current_user.id
    ).all()

    return bookings




@router.delete("/{booking_id}")
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    booking = db.query(Booking).filter(
        Booking.booking_id == booking_id
    ).first()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    db.delete(booking)
    db.commit()

    return {"message": "Booking cancelled"}