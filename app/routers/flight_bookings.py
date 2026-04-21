from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from app.database.database import get_db
from app.models.flight_models import Flight, FlightBooking, FlightSeat
from app.core.dependencies import get_current_user
from datetime import datetime
from typing import Annotated
from app.models.user import User
from app.schemas.schemas import Bookseats
from pydantic import BaseModel


SessionDep = Annotated[AsyncSession, Depends(get_db)]
CurretUser = Annotated[User, Depends(get_current_user)]

router = APIRouter()

@router.get("/time")
async def get_current_time():
    return datetime.now()

@router.post("/")
async def book_multiple_seats(
    data: Bookseats, 
    db: SessionDep,
    current_user: CurretUser
):
    try:
        #  Verify Flight Existence
        flight_result = await db.execute(
            select(Flight).filter(Flight.flight_id == data.flight_id)
        )
        flight = flight_result.scalars().first()
        if not flight:
            raise HTTPException(status_code=404, detail="Flight not found")

        seats_to_book = []
        total_price = 0

        #  Verify and Collect Seats
        for seat_num in data.seat_numbers:
            seat_stmt = select(FlightSeat).filter(
                FlightSeat.flight_id == data.flight_id,
                FlightSeat.seat_number == seat_num
            )
            seat_result = await db.execute(seat_stmt)
            seat = seat_result.scalars().first()

            if not seat:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Seat {seat_num} not found on this flight"
                )
            
            if seat.is_booked:
                raise HTTPException(
                    status_code=400,  
                    detail=f"Seat {seat_num} is already booked"
                )
            
            seats_to_book.append(seat)
            total_price += seat.price

        #  Create Booking Record
        booking = FlightBooking(
            flight_id=data.flight_id,
            user_id=current_user.id,
            seat_number=",".join(data.seat_numbers), 
            total_price=total_price,
            created_by=current_user.id
        )
        db.add(booking)
        
        #  Update Seat Status
        for seat in seats_to_book:
            seat.is_booked = True

        #  Commit Transaction
        await db.commit()
        await db.refresh(booking)

        return {
            "message": "Seats booked successfully",
            "booking_id": booking.booking_id,
            "flight_id": booking.flight_id,
            "seats": data.seat_numbers,
            "total_price": total_price
        }

    except Exception as e:
        await db.rollback()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500, 
            detail=f"Database error: {str(e)}"
        )


@router.get("/{flight_id}/seat")
async def get_available_seats(flight_id: int, db: SessionDep):
    try:
        result = await db.execute(select(FlightSeat).filter(FlightSeat.flight_id == flight_id))
        seats = result.scalars().all()
        
        if not seats:
            raise HTTPException(status_code=404, detail="No seats found for flight")
        return seats
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail="Database error")

#  Get User Bookings
@router.get("/bookings")
async def get_all_bookings(db: SessionDep, current_user: CurretUser):
    try:
        result = await db.execute(
            select(FlightBooking).filter(FlightBooking.created_by == current_user.id)
        )
        return result.scalars().all()
    except Exception:
        raise HTTPException(status_code=500, detail="Database error fetching bookings")

#  Delete Booking (Release Seats)
@router.delete("/bookings/{booking_id}")
async def delete_booking(booking_id: int, db: SessionDep, current_user: CurretUser):
    try:
        # Find the booking
        result = await db.execute(
            select(FlightBooking).filter(
                FlightBooking.booking_id == booking_id,
                FlightBooking.created_by == current_user.id
            )
        )
        booking = result.scalars().first()
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        # Split seat numbers
        seats_to_release = booking.seat_number.split(',') if isinstance(booking.seat_number, str) else []
        
        # Batch update seats (More efficient than a loop)
        for s in seats_to_release:
            seat_result = await db.execute(
                select(FlightSeat).filter(
                    FlightSeat.flight_id == booking.flight_id,
                    FlightSeat.seat_number == s.strip()
                )
            )
            seat = seat_result.scalars().first()
            if seat:
                seat.is_booked = False

        await db.delete(booking)
        await db.commit()
        return {"message": "Booking deleted and seats released successfully"}
    except Exception as e:
        await db.rollback()
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

#  Swap Seat
class UpdateSeat(BaseModel):
    booking_id: int 
    old_seat_number: str 
    new_seat_number: str

@router.put("/bookings/{booking_id}/swap-seat")
async def swap_single_seat(
    data: UpdateSeat,
    db: SessionDep, 
    current_user: CurretUser
):
    try:
        # Fetch the booking
        booking_result = await db.execute(
            select(FlightBooking).filter(
                FlightBooking.booking_id == data.booking_id,
                FlightBooking.user_id == current_user.id
            )
        )
        booking = booking_result.scalars().first()

        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        current_seats = [s.strip() for s in booking.seat_number.split(",")]
        if data.old_seat_number not in current_seats:
            raise HTTPException(status_code=400, detail=f"Seat {data.old_seat_number} not in booking")

        # Fetch New and Old seats simultaneously
        new_seat_res = await db.execute(
            select(FlightSeat).filter(
                FlightSeat.flight_id == booking.flight_id, 
                FlightSeat.seat_number == data.new_seat_number
            )
        )
        new_seat = new_seat_res.scalars().first()

        old_seat_res = await db.execute(
            select(FlightSeat).filter(
                FlightSeat.flight_id == booking.flight_id, 
                FlightSeat.seat_number == data.old_seat_number
            )
        )
        old_seat = old_seat_res.scalars().first()

        if not new_seat or new_seat.is_booked:
            raise HTTPException(status_code=400, detail="New seat unavailable")

        # Update Statuses
        if old_seat:
            old_seat.is_booked = False
        new_seat.is_booked = True

        # Update Booking Info
        updated_seats = [data.new_seat_number if s == data.old_seat_number else s for s in current_seats]
        booking.total_price += (new_seat.price - old_seat.price)
        booking.seat_number = ",".join(updated_seats)

        await db.commit()
        await db.refresh(booking)

        return {
            "message": "Seat swapped successfully",
            "current_seats": booking.seat_number,
            "new_total_price": booking.total_price
        }

    except Exception as e:
        await db.rollback()
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=str(e))