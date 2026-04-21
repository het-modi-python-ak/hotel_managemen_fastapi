from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from datetime import date
from typing import Annotated

from app.database.database import get_db
from app.models.booking import Booking
from app.models.booking_item import BookingItem
from app.models.room import Room
from app.models.user import User
from app.schemas.booking import BookingCreate
from app.core.dependencies import get_current_user
from app.core.redis_client import redis_client
from app.tasks.reminder_tasks import send_booking_reminder
from fastapi import BackgroundTasks
from sqlalchemy.exc import SQLAlchemyError
from app.services.email_service import send_booking_confirmation_email,send_cancellation_email
from app.core.rate_limiter import fixed_window_rate_limit
from app.tasks.reminder_tasks import send_booking_reminder
from app.models.user import User
from sqlalchemy.orm import selectinload

SessionDep = Annotated[AsyncSession, Depends(get_db)]
CurretUser = Annotated[User, Depends(get_current_user)]

router = APIRouter()
LOCK_TIME = 600 

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking_data: BookingCreate,
    db: SessionDep,
    current_user: CurretUser
):
    #  Validation Logic
    if booking_data.check_in < date.today():
        raise HTTPException(status_code=400, detail="Check-in cannot be in the past")

    nights = (booking_data.check_out - booking_data.check_in).days
    if nights <= 0:
        raise HTTPException(status_code=400, detail="Check-out must be after check-in")

    total_price = 0
    room_items = []
    locked_keys_info = [] # Store tuple of (key, quantity) for rollback

    try:
        for room_request in booking_data.rooms:
            #  Fetch Room (Async)
            room_stmt = select(Room).filter(
                Room.hotel_id == booking_data.hotel_id,
                Room.room_type == room_request.room_type
            )
            room_result = await db.execute(room_stmt)
            room = room_result.scalars().first()

            if not room:
                raise HTTPException(status_code=404, detail=f"{room_request.room_type} room not found")

            #  Redis Lock Check
            lock_key = f"lock:{booking_data.hotel_id}:{room.room_id}:{booking_data.check_in}:{booking_data.check_out}"
            raw_locked = redis_client.get(lock_key)
            locked_rooms = int(raw_locked) if raw_locked else 0

            #  Check DB Confirmed Bookings (Async Aggregate)
            booked_stmt = (
                select(func.sum(BookingItem.quantity))
                .join(Booking)
                .filter(
                    BookingItem.room_id == room.room_id,
                    Booking.status == "confirmed",
                    Booking.check_in < booking_data.check_out,
                    Booking.check_out > booking_data.check_in
                )
            )
            booked_result = await db.execute(booked_stmt)
            booked = booked_result.scalar() or 0

            available = room.total_rooms - booked - locked_rooms
            
            if available < room_request.quantity:
                raise HTTPException(
                    status_code=409,
                    detail=f"Only {available} {room.room_type} rooms available"
                )

            #  Apply Redis Lock
            redis_client.incrby(lock_key, room_request.quantity)
            redis_client.expire(lock_key, LOCK_TIME)
            locked_keys_info.append((lock_key, room_request.quantity))

            total_price += room.price * room_request.quantity * nights
            room_items.append({"room_id": room.room_id, "quantity": room_request.quantity})

        #  Create Booking Record
        booking = Booking(
            user_id=current_user.id,
            hotel_id=booking_data.hotel_id,
            check_in=booking_data.check_in,
            check_out=booking_data.check_out,
            no_of_people=booking_data.no_of_people,
            status="pending"
        )
        db.add(booking)
        await db.flush() # Generate booking_id

        #  Add Booking Items
        for item in room_items:
            db.add(
                BookingItem(
                    booking_id=booking.booking_id,
                    room_id=item["room_id"],
                    quantity=item["quantity"]
                )
            )
        
        await db.commit()
        await db.refresh(booking)

        #  
        send_booking_reminder.apply_async(
            args=[current_user.email, booking.booking_id], 
            countdown=10
        )

        return {
            "booking_id": booking.booking_id,
            "status": booking.status,
            "total_price": total_price,
            "message": "Rooms locked. Please confirm booking."
        }

    except Exception as e:
        await db.rollback()
        #  Cleanup Redis locks if DB transaction fails
        for key, qty in locked_keys_info:
            redis_client.decrby(key, qty)
            
       
        raise HTTPException(status_code=500, detail="Internal server error during booking")



@router.patch("/{booking_id}", status_code=status.HTTP_200_OK)
async def confirm_booking(
    booking_id: int,
    background_tasks: BackgroundTasks,
    db: SessionDep, 
    current_user: CurretUser
):
    try:
        # 1. Fetch Booking with items using selectinload
        stmt = (
            select(Booking)
            .filter(Booking.booking_id == booking_id)
            .options(selectinload(Booking.booking_items))
        )
        result = await db.execute(stmt)
        booking = result.scalars().first()
        
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        if booking.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
            
        if booking.status == "confirmed":
            return {"message": "Booking already confirmed"}
        
        if booking.status != "pending":
            raise HTTPException(status_code=400, detail=f"Cannot confirm {booking.status} booking")
            
        # 2. Redis Validation and Lock Release
        for item in booking.booking_items:
            lock_key = f"lock:{booking.hotel_id}:{item.room_id}:{booking.check_in}:{booking.check_out}"
            
            if not redis_client.exists(lock_key):
                booking.status = "cancelled"
                await db.commit()
                raise HTTPException(status_code=400, detail="Booking window expired")
            
            # Decrement and cleanup Redis
            new_val = redis_client.decrby(lock_key, item.quantity)
            if new_val <= 0:
                redis_client.delete(lock_key)
                
        # 3. Finalize
        booking.status = "confirmed"
        await db.commit()
        await db.refresh(booking)
        
        background_tasks.add_task(send_booking_confirmation_email, current_user.email, booking.booking_id)
        return {"message": "Booking confirmed", "booking_id": booking.booking_id}

    except Exception as e:
        await db.rollback()
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{booking_id}")
async def cancel_booking(
    booking_id: int,
    background_tasks: BackgroundTasks,
    db: SessionDep,
    current_user: CurretUser
):
    try:
        # Fetch Booking with items
        stmt = (
            select(Booking)
            .filter(Booking.booking_id == booking_id)
            .options(selectinload(Booking.booking_items))
        )
        result = await db.execute(stmt)
        booking = result.scalars().first()

        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        if booking.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
            
        if booking.status == "cancelled":
            return {"message": "Booking is already cancelled"}

        # Release Redis locks if it was still pending
        if booking.status == "pending":
            for item in booking.booking_items:
                lock_key = f"lock:{booking.hotel_id}:{item.room_id}:{booking.check_in}:{booking.check_out}"
                if redis_client.exists(lock_key):
                    new_val = redis_client.decrby(lock_key, item.quantity)
                    if new_val <= 0:
                        redis_client.delete(lock_key)

        booking.status = "cancelled"
        await db.commit()
        
        background_tasks.add_task(send_cancellation_email, current_user.email, booking.booking_id)
        return {"message": "Booking cancelled successfully"}

    except Exception as e:
        await db.rollback()
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/")
async def get_my_bookings(
    db: SessionDep,
    current_user: CurretUser
):
    try:
        
        fixed_window_rate_limit(current_user.id, "get_my_bookings")
        
        result = await db.execute(
            select(Booking).filter(Booking.user_id == current_user.id)
        )
        return result.scalars().all()
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail="Error fetching your bookings")

# 2. Get specific booking details
@router.get("/{booking_id}") 
async def get_booking_details(
    booking_id: int,
    db: SessionDep,
    current_user: CurretUser
):
    try:
        # Verify Booking existence and ownership
        booking_result = await db.execute(
            select(Booking).filter(
                Booking.booking_id == booking_id,
                Booking.user_id == current_user.id
            )
        )
        booking = booking_result.scalars().first()

        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found or unauthorized")

        # Fetch items and room types in a single joined query
        details_stmt = (
            select(BookingItem, Room.room_type)
            .join(Room, BookingItem.room_id == Room.room_id)
            .filter(BookingItem.booking_id == booking_id)
        )
        details_result = await db.execute(details_stmt)
        # This returns a list of rows, each containing (BookingItem, str)
        details_rows = details_result.all()

        room_details = [
            {
                "room_type": row.room_type,
                "quantity": row.BookingItem.quantity,
                "room_id": row.BookingItem.room_id
            }
            for row in details_rows
        ]

        return {
            "booking_id": booking.booking_id,
            "hotel_id": booking.hotel_id,
            "check_in": booking.check_in,
            "check_out": booking.check_out,
            "status": booking.status,
            "rooms_booked": room_details
        }

    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail="Error retrieving booking details")


@router.post("/test/cancel_all_pending")
async def cancel_all_pending_bookings(
    db: SessionDep,
    current_user: CurretUser
):
    # Fetch bookings and their items in one async operation
    stmt = (
        select(Booking)
        .filter(Booking.user_id == current_user.id, Booking.status == "pending")
        .options(selectinload(Booking.booking_items))
    )
    result = await db.execute(stmt)
    pending_bookings = result.scalars().all()

    if not pending_bookings:
        return {"message": "No pending bookings to cancel"}

    for booking in pending_bookings:
        # Release Redis locks for each item
        for item in booking.booking_items:
            lock_key = f"lock:{booking.hotel_id}:{item.room_id}:{booking.check_in}:{booking.check_out}"
            
            if redis_client.exists(lock_key):
                new_value = redis_client.decrby(lock_key, item.quantity)
                if new_value <= 0:
                    redis_client.delete(lock_key)
        
        booking.status = "cancelled"

    await db.commit()
    return {"message": f"Successfully cancelled {len(pending_bookings)} pending bookings."}


# 
@router.post("/test/cancel_all_confirm")
async def cancel_all_confirmed_bookings(
    db: SessionDep,
    current_user: CurretUser
):
    # Fetch confirmed bookings with items
    stmt = (
        select(Booking)
        .filter(Booking.user_id == current_user.id, Booking.status == "confirmed")
        .options(selectinload(Booking.booking_items))
    )
    result = await db.execute(stmt)
    confirmed_bookings = result.scalars().all()

    if not confirmed_bookings:
        return {"message": "No confirmed bookings to cancel"}

    for booking in confirmed_bookings:
    
        for item in booking.booking_items:
            lock_key = f"lock:{booking.hotel_id}:{item.room_id}:{booking.check_in}:{booking.check_out}"
            if redis_client.exists(lock_key):
                new_value = redis_client.decrby(lock_key, item.quantity)
                if new_value <= 0:
                    redis_client.delete(lock_key)
        
        booking.status = "cancelled"

    await db.commit()
    return {"message": f"Successfully cancelled {len(confirmed_bookings)} confirmed bookings."}
