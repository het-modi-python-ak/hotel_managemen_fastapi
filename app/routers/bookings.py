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

router = APIRouter()

LOCK_TIME = 300


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

        if not room:
            raise HTTPException(
                status_code=404,
                detail=f"{room_request.room_type} room not found"
            )

        lock_key = f"lock:{booking_data.hotel_id}:{room.room_id}:{booking_data.check_in}:{booking_data.check_out}"

        lock = redis_client.set(lock_key, current_user.id, nx=True, ex=LOCK_TIME)

        if not lock:
            raise HTTPException(
                status_code=400,
                detail=f"{room.room_type} rooms are temporarily locked by another user"
            )

        booked = db.query(func.sum(BookingItem.quantity)).join(Booking).filter(
            BookingItem.room_id == room.room_id,
            Booking.status != "cancelled",
            Booking.check_in < booking_data.check_out,
            Booking.check_out > booking_data.check_in
        ).scalar() or 0

        available = room.total_rooms - booked

        if room_request.quantity > available:
            raise HTTPException(
                status_code=400,
                detail=f"Only {available} {room.room_type} rooms available"
            )

        total_price += room.price * room_request.quantity * nights

        room_items.append({
            "room_id": room.room_id,
            "quantity": room_request.quantity
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

    items = db.query(BookingItem).filter(
        BookingItem.booking_id == booking_id
    ).all()

    for item in items:
        lock_key = f"lock:{booking.hotel_id}:{item.room_id}:{booking.check_in}:{booking.check_out}"
        redis_client.delete(lock_key)

    booking.status = "confirmed"

    db.commit()

    return {"message": "Booking confirmed"}


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

    items = db.query(BookingItem).filter(
        BookingItem.booking_id == booking_id
    ).all()

    for item in items:
        lock_key = f"lock:{booking.hotel_id}:{item.room_id}:{booking.check_in}:{booking.check_out}"
        redis_client.delete(lock_key)

    booking.status = "cancelled"

    db.commit()

    return {"message": "Booking cancelled successfully"}


@router.get("/my")
def get_my_bookings(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    bookings = db.query(Booking).filter(
        Booking.user_id == current_user.id
    ).all()

    return bookings