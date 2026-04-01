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
from core.redis_client import redis_client
from core.hotel_enums import StateEnum, CountryEnum


router = APIRouter()

LOCK_TIME = 30  # for booking

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_booking(
    booking_data: BookingCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if booking_data.check_in < date.today():
        raise HTTPException(status_code=400, detail="Check-in cannot be in the past")

    nights = (booking_data.check_out - booking_data.check_in).days
    if nights <= 0:
        raise HTTPException(status_code=400, detail="Check-out must be after check-in")

    total_price = 0
    room_items = []

    for room_request in booking_data.rooms:

        room = db.query(Room).filter(
            Room.hotel_id == booking_data.hotel_id,
            Room.room_type == room_request.room_type
        ).first()

        if room_request.quantity < 1:
            raise HTTPException(status_code =400 , detail="booking quantity should be minimum 1")
        

        if not room:
            raise HTTPException(
                status_code=404,
                detail=f"{room_request.room_type} room not found"
            )

        lock_key = f"lock:{booking_data.hotel_id}:{room.room_id}:{booking_data.check_in}:{booking_data.check_out}"

        locked_rooms = redis_client.get(lock_key)
        try:
            locked_rooms = int(locked_rooms)
        except:
            locked_rooms =  0

        booked = db.query(func.sum(BookingItem.quantity)).join(Booking).filter(
            BookingItem.room_id == room.room_id,
            Booking.status == "confirmed" , 
            Booking.check_in < booking_data.check_out,
            Booking.check_out > booking_data.check_in
        ).scalar() or 0
        



          


        available = room.total_rooms - booked - locked_rooms # available rooms

        if available < 0:
            raise HTTPException(status_code = 404 , detail = "sorry , no rooms availabel in this hotel ")

        print("available rooms " , available)
        print("booked rooms " , booked)
        print("total rooms " , room.total_rooms)
        print("locked rooms ", locked_rooms)







        if room_request.quantity > available:
            raise HTTPException(
                status_code=400,
                detail=f"Only {available} {room.room_type} rooms available"
            )

        redis_client.incrby(lock_key, room_request.quantity)
        redis_client.expire(lock_key, LOCK_TIME)

        total_price += room.price * room_request.quantity * nights # total price

        room_items.append({
            "room_id": room.room_id,
            "quantity": room_request.quantity,
            "lock_key": lock_key
        })

    booking = Booking(
        user_id=current_user.id,
        hotel_id=booking_data.hotel_id,
        check_in=booking_data.check_in,
        check_out=booking_data.check_out,
        no_of_people=booking_data.no_of_people,
        status="pending"
    )

    db.add(booking)
    db.flush()

    for item in room_items:
        db.add(
            BookingItem(
                booking_id=booking.booking_id,
                room_id=item["room_id"],
                quantity=item["quantity"]
            )
        )

    db.commit()
    db.refresh(booking)
   
    return {
        "booking_id": booking.booking_id,
        "status": booking.status,
        "total_price": total_price,
        "message": "Rooms locked for 5 minutes. Confirm booking before timeout."
    }





# confirm
@router.put("/{booking_id}")
def confirm_booking(
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
        raise HTTPException(status_code=403, detail="Not authorized")

    if booking.status == "confirmed":
        return {"message": "Booking already confirmed"}

    if booking.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot confirm booking with status: {booking.status}. Only pending bookings can be confirmed."
        )

    items = db.query(BookingItem).filter(
        BookingItem.booking_id == booking_id
    ).all()

    # Verify all locks are still active
    for item in items:
        lock_key = f"lock:{booking.hotel_id}:{item.room_id}:{booking.check_in}:{booking.check_out}"
        if not redis_client.exists(lock_key):
            # If any lock key is missing/expired, cancel the booking and deny confirmation
            booking.status = "cancelled"
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Booking window expired. Booking automatically cancelled. Please create a new booking."
            )

    # If all locks are present, proceed with confirmation and release the locks
    for item in items:
        lock_key = f"lock:{booking.hotel_id}:{item.room_id}:{booking.check_in}:{booking.check_out}"
        new_value = redis_client.decrby(lock_key, item.quantity)
        if new_value <= 0:
            redis_client.delete(lock_key)

    booking.status = "confirmed"
    db.commit()

    return {"message": "Booking confirmed"}








# delete booking
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
        raise HTTPException(status_code=403, detail="Not authorized")
        
    if booking.status == "cancelled":
        return {"message": "Booking already cancelled"}

    items = db.query(BookingItem).filter(
        BookingItem.booking_id == booking_id
    ).all()

    for item in items:
        lock_key = f"lock:{booking.hotel_id}:{item.room_id}:{booking.check_in}:{booking.check_out}"
        
        # Check if the lock key exists before attempting to modify it
        if redis_client.exists(lock_key):
            new_value = redis_client.decrby(lock_key, item.quantity)
            
            if new_value <= 0:
                redis_client.delete(lock_key)

    booking.status = "cancelled"

    db.commit()

    return {"message": "Booking cancelled successfully"}






#get my bookins 

@router.get("/")
def get_my_bookings(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    bookings = db.query(Booking).filter(
        Booking.user_id == current_user.id
    ).all()

    return bookings

@router.get("{booking_id}")
def get_booking_details(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    booking = db.query(Booking).filter(
        Booking.booking_id == booking_id,
        Booking.user_id == current_user.id
    ).first()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found or not authorized")

    # booking items and join with the Room model to get room types
    details = db.query(BookingItem, Room.room_type).join(Room).filter(
        BookingItem.booking_id == booking_id,
        BookingItem.room_id == Room.room_id
    ).all()

    room_details = [
        {
            "room_type": room_type,
            "quantity": item.quantity,
            "room_id": item.room_id
        }
        for item, room_type in details
    ]

    return {
        "booking_id": booking.booking_id,
        "hotel_id": booking.hotel_id,
        "check_in": booking.check_in,
        "check_out": booking.check_out,
        "status": booking.status,
        "rooms_booked": room_details
    }






#for cancelling all pending bookings for tetsting propese 
@router.post("/test/cancel_all_pending")
def cancel_all_pending_bookings(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    
  
    # 1. Find all pending bookings for the user
    pending_bookings = db.query(Booking).filter(
        Booking.user_id == current_user.id,
        Booking.status == "pending" 
    ).all()

    if not pending_bookings:
        return {"message": "No pending bookings to cancel"}

    total_cancelled = 0
    for booking in pending_bookings:
        # 2. Get associated booking items to unlock rooms
        items = db.query(BookingItem).filter(
            BookingItem.booking_id == booking.booking_id
        ).all()

        for item in items:
            lock_key = f"lock:{booking.hotel_id}:{item.room_id}:{booking.check_in}:{booking.check_out}"
            
            # 3. Decrement redis lock
            if redis_client.exists(lock_key):
                new_value = redis_client.decrby(lock_key, item.quantity)
                if new_value <= 0:
                    redis_client.delete(lock_key)
        
        # 4. Update status
        booking.status = "cancelled"
        total_cancelled += 1

    db.commit()
    return {"message": f"Successfully cancelled {total_cancelled} pending bookings."}





#cancelle all confirmed booking 



#for cancelling all pending bookings for tetsting propese 
@router.post("/test/cancel_all_confirm")
def cancel_all_pending_bookings(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    
    # 1. Find all pending bookings for the user
    pending_bookings = db.query(Booking).filter(
        Booking.user_id == current_user.id,
        Booking.status == "confirmed" 
    ).all()

    if not pending_bookings:
        return {"message": "No confirmed bookings to cancel"}

    total_cancelled = 0
    for booking in pending_bookings:
        # 2. Get associated booking items to unlock rooms
        items = db.query(BookingItem).filter(
            BookingItem.booking_id == booking.booking_id
        ).all()

        for item in items:
            lock_key = f"lock:{booking.hotel_id}:{item.room_id}:{booking.check_in}:{booking.check_out}"
            
            # 3. Decrement redis lock
            if redis_client.exists(lock_key):
                new_value = redis_client.decrby(lock_key, item.quantity)
                if new_value <= 0:
                    redis_client.delete(lock_key)
        
        # 4. Update status
        booking.status = "cancelled"
        total_cancelled += 1

    db.commit()
    return {"message": f"Successfully cancelled {total_cancelled} confirmed bookings."}



