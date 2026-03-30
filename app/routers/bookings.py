
# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from sqlalchemy import func
# from database.database import get_db
# from models.booking import Booking
# from models.booking_item import BookingItem
# from models.room import Room
# from models.hotel import Hotel
# from core.dependencies import get_current_user
# from datetime import datetime
# from schemas.booking_schema import BookingCreate


# router = APIRouter( tags=["Bookings"])



# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from sqlalchemy import func
# from database.database import get_db
# from models.booking import Booking
# from models.booking_item import BookingItem
# from models.room import Room
# from schemas.booking import BookingCreate
# from core.dependencies import get_current_user


# router = APIRouter(prefix="/bookings", tags=["Bookings"])


# @router.post("/")
# def create_booking(
#     booking_data: BookingCreate,
#     db: Session = Depends(get_db),
#     current_user=Depends(get_current_user)
# ):

#     booking = Booking(
#         user_id=current_user.id,
#         hotel_id=booking_data.hotel_id,
#         check_in=booking_data.check_in,
#         check_out=booking_data.check_out,
#         no_of_people=booking_data.no_of_people,
#         status="pending"
#     )

#     db.add(booking)
#     db.commit()
#     db.refresh(booking)

#     total_price = 0

#     for room_request in booking_data.rooms:

#         room = db.query(Room).filter(
#             Room.hotel_id == booking_data.hotel_id,
#             Room.room_type == room_request.room_type
#         ).first()

#         if not room:
#             raise HTTPException(status_code=404, detail="Room type not found")

#         booked = db.query(func.sum(BookingItem.quantity)).join(Booking).filter(
#             BookingItem.room_id == room.room_id,
#             Booking.status != "cancelled",
#             Booking.check_in < booking_data.check_out,
#             Booking.check_out > booking_data.check_in
#         ).scalar()

#         booked = booked or 0

#         available = room.total_rooms - booked

#         if room_request.quantity > available:
#             raise HTTPException(
#                 status_code=400,
#                 detail=f"{room.room_type} rooms not available"
#             )

#         booking_item = BookingItem(
#             booking_id=booking.booking_id,
#             room_id=room.room_id,
#             quantity=room_request.quantity
#         )

#         db.add(booking_item)

#         nights = (booking_data.check_out - booking_data.check_in).days

#         total_price += room.price * room_request.quantity * nights

#     db.commit()

#     return {
#         "booking_id": booking.booking_id,
#         "status": "pending",
#         "total_price": total_price
#     }

# #confirm booking

# @router.put("/confirm/{booking_id}")
# def confirm_booking(booking_id:int , db :Session= Depends(get_db), current_user=Depends(get_current_user)):
#     booking = db.query(Booking).filter(Booking.booking_id == booking_id).first()

#     if booking.user_id != current_user.id:
#         raise HTTPException(status_code=404, detail="Invalid user")


#     if not booking:
#         raise HTTPException(status_code=404, detail="Booking not found")
#     booking.status = "confirmed"
#     db.commit()
#     return {"message":"Booking confirmed"}


# #cancell booking 


# @router.put("/cancel/{booking_id}")
# def cancel_booking(booking_id:int,db:Session=Depends(get_db),current_user=Depends(get_current_user)):
#       booking = db.query(Booking).filter(Booking.booking_id == booking_id).first()

#       if booking.user_id != current_user.id:
#         raise HTTPException(status_code=404, detail="Invalid user")
      
#       if not booking :
#           raise HTTPException(status_code=404, detail="Booking not found")
#       booking.status = "cancelled"
#       db.commit()
#       return {"messgae":"Booking cnacelled"}


# @router.get("/my")
# def get_my_bookings(
#     db: Session = Depends(get_db),
#     current_user=Depends(get_current_user)
# ):

#     bookings = db.query(Booking).filter(
#         Booking.user_id == current_user.id
#     ).all()

#     return bookings


# @router.delete("/{booking_id}")
# def cancel_booking(
#     booking_id: int,
#     db: Session = Depends(get_db),
#     current_user=Depends(get_current_user)
# ):

#     booking = db.query(Booking).filter(
#         Booking.booking_id == booking_id
#     ).first()

#     if not booking:
#         raise HTTPException(status_code=404, detail="Booking not found")

#     if booking.user_id != current_user.id:
#         raise HTTPException(status_code=403, detail="Not allowed")

#     booking.status = "cancelled"

#     db.commit()

#     return {"message": "Booking cancelled"}


# # herer the delete route is not working properly and also the checkin and checnk_out date is not validated properly and also correct some other errors if you found



from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
from database.database import get_db
from models.booking import Booking
from models.booking_item import BookingItem
from models.room import Room
from schemas.booking import BookingCreate
from core.dependencies import get_current_user

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_booking(
    booking_data: BookingCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # 1. Date Validation
    if booking_data.check_in < date.today():
        raise HTTPException(status_code=400, detail="Check-in date cannot be in the past")
    
    nights = (booking_data.check_out - booking_data.check_in).days
    if nights <= 0:
        raise HTTPException(status_code=400, detail="Check-out must be after check-in")

    total_price = 0
    room_items = []

    # 2. Availability Check (Before saving the booking)
    for room_request in booking_data.rooms:
        room = db.query(Room).filter(
            Room.hotel_id == booking_data.hotel_id,
            Room.room_type == room_request.room_type
        ).first()

        if not room:
            raise HTTPException(status_code=404, detail=f"Room type '{room_request.room_type}' not found")

        # Calculate booked rooms for these dates
        booked = db.query(func.sum(BookingItem.quantity)).join(Booking).filter(
            BookingItem.room_id == room.room_id,
            Booking.status != "cancelled",
            Booking.check_in < booking_data.check_out,
            Booking.check_out > booking_data.check_in
        ).scalar() or 0

        if room_request.quantity > (room.total_rooms - booked):
            raise HTTPException(
                status_code=400,
                detail=f"Not enough {room.room_type} rooms available for these dates"
            )
        
        total_price += room.price * room_request.quantity * nights
        room_items.append({"room_id": room.room_id, "quantity": room_request.quantity})

    # 3. Create Booking
    new_booking = Booking(
        user_id=current_user.id,
        hotel_id=booking_data.hotel_id,
        check_in=booking_data.check_in,
        check_out=booking_data.check_out,
        no_of_people=booking_data.no_of_people,
        status="pending"
    )
    db.add(new_booking)
    db.flush() # Flush to get new_booking.booking_id without committing yet

    # 4. Create Booking Items
    for item in room_items:
        db.add(BookingItem(
            booking_id=new_booking.booking_id,
            room_id=item["room_id"],
            quantity=item["quantity"]
        ))

    db.commit()
    db.refresh(new_booking)

    return {
        "booking_id": new_booking.booking_id,
        "status": new_booking.status,
        "total_price": total_price
    }

@router.put("{booking_id}")
def confirm_booking(booking_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    booking = db.query(Booking).filter(Booking.booking_id == booking_id).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to confirm this booking")

    booking.status = "confirmed"
    db.commit()
    return {"message": "Booking confirmed"}

@router.delete("/{booking_id}")
def delete_or_cancel_booking(booking_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    booking = db.query(Booking).filter(Booking.booking_id == booking_id).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # If it's already "pending", you might want to delete it. 
    # If it's "confirmed", you just change status to "cancelled".
    if booking.status=="cancelled":
        raise HTTPException(status_code=404,detail=" Booking already cancelled ")
    booking.status = "cancelled"

    
    db.commit()
    return {"message": "Booking successfully cancelled"}

@router.get("/my")
def get_my_bookings(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(Booking).filter(Booking.user_id == current_user.id).all()
