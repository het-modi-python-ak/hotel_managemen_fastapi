from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from models.booking import Booking
from models.booking_item import BookingItem
from models.room import Room
from core.dependencies import get_current_user
from datetime import date
from pydantic import BaseModel
from schemas.schemas import BookingRequest
from services.booking_service import get_available_rooms


router = APIRouter()





class RoomBooking(BaseModel): #pydnt
    room_type: int
    quantity: int

class BookingCreate(BaseModel): #pydnt
    hotel_id: int
    check_in: date
    check_out: date
    rooms: list[RoomBooking]




# @router.post("/")
# def create_booking(
#     booking_data: BookingCreate,
#     db: Session = Depends(get_db),
#     current_user=Depends(get_current_user)
# ):
#     booking = Booking(
#         user_id=current_user.id,
#         hotel_id=booking_data.ahotel_id
#     )

#     db.add(booking)
#     db.commit()
#     db.refresh(booking)

#     total_price = 0

#     for item in booking_data.rooms:
#         # --- FIX HERE: Changed item["room_id"] to item.room_id ---
#         room = db.query(Room).filter(Room.room_id == item.room_id).first()
        
#         if not room:
#             raise HTTPException(status_code=404, detail="Room not found")

#         # --- FIX HERE: Changed item["quantity"] to item.quantity ---
#         booking_item = BookingItem(
#             booking_id=booking.booking_id,
#             room_id=room.room_id,
#             quantity=item.quantity, 
#             check_in=booking_data.check_in,
#             check_out=booking_data.check_out,
#             price_per_room=room.price
#         )

#         total_price += room.price * item.quantity
#         db.add(booking_item)

#     db.commit()
# # here i can add book  multiple rooms like for room id 1 the number of total rooms are 2 , bur i can book like say 4 rooms for room id 1 
# # , other then this when i register same type of room for the same category , but i get the different room_id for the same types of room
# #  and there is no status seen if the room is available or  not 

#     return {
#         "booking_id": booking.booking_id,
#         "total_price": total_price
#     }

@router.post("/")
def create_booking(
    booking: BookingRequest, # Use the Pydantic model defined
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # 1. Create the base booking
    booking_db = Booking(
        user_id=current_user.id,
        hotel_id=booking.hotel_id,
        status="confirmed"
    )
    db.add(booking_db)
    db.commit()
    db.refresh(booking_db)

    # 2. Process room items
    for item in booking.rooms:
        # Check availability
        available = get_available_rooms(
            db,
            hotel_id=booking.hotel_id,
            room_type=item.room_type, # Ensure your Room model has room_type
            check_in=booking.check_in,
            check_out=booking.check_out
        )

        if item.quantity > available:
            raise HTTPException(
                400,
                f"Only {available} rooms of this type are available"
            )

        # Get specific room instances
        rooms = db.query(Room).filter(
            Room.hotel_id == booking.hotel_id,
            Room.room_type == item.room_type
        ).all()

        if not rooms:
            raise HTTPException(404, f"Room type {item.room_type} not found")

        # Properly assign quantities to rooms
        remaining_to_book = item.quantity
        for room in rooms:
            if remaining_to_book <= 0:
                break
            
            # Booking 1 unit of this specific room_id
            booking_item = BookingItem(
                booking_id=booking_db.booking_id,
                room_id=room.room_id,
                quantity=1, 
                check_in=booking.check_in,
                check_out=booking.check_out
            )
            db.add(booking_item)
            remaining_to_book -= 1

        db.commit()
    return {"message": "Booking successful", "booking_id": booking_db.booking_id}



@router.get("/my")
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
        Booking.booking_id == booking_id,
        Booking.user_id == current_user.id
    ).first()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    booking.status = "cancelled"
    db.commit()
    return {"message": "Booking cancelled"}

