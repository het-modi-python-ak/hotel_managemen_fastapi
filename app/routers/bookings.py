from fastapi import APIRouter, Depends, HTTPException, status,BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
from app.database.database import get_db
from app.models.booking import Booking
from app.models.booking_item import BookingItem
from app.models.room import Room
from app.models.user import User
from app.schemas.booking import BookingCreate
from app.core.dependencies import get_current_user
from app.core.redis_client import redis_client
from app.core.hotel_enums import StateEnum, CountryEnum
from sqlalchemy.orm import Session
from sqlalchemy import func
import logging
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
from sqlalchemy.exc import SQLAlchemyError
from app.services.email_service import send_booking_confirmation_email,send_cancellation_email
from app.core.rate_limiter import fixed_window_rate_limit
from app.tasks.reminder_tasks import send_booking_reminder
from app.models.user_email import User2

router = APIRouter()

LOCK_TIME = 10  # time for booking


logger = logging.getLogger(__name__)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_booking(
    booking_data: BookingCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    
    # fixed_window_rate_limit(current_user.id,"create_booking")
    #  Validation Checks (Client Errors - 400)
    if booking_data.check_in < date.today():
        raise HTTPException(status_code=400, detail="Check-in cannot be in the past")

    nights = (booking_data.check_out - booking_data.check_in).days
    if nights <= 0:
        raise HTTPException(status_code=400, detail="Check-out must be after check-in")

    if booking_data.no_of_people < 1:
        raise HTTPException(status_code=400, detail="Number of people should be at least 1")

    total_price = 0
    room_items = []
    
    # Track locked keys for potential rollback if db fails
    locked_keys_in_this_req = []

    try:
        for room_request in booking_data.rooms:
            if room_request.quantity < 1:
                raise HTTPException(status_code=400, detail="Booking quantity should be minimum 1")
            
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
            
            
            locked_rooms = redis_client.get(lock_key)
            try:
                locked_rooms = int(locked_rooms) if locked_rooms else 0
            except:
                locked_rooms = 0

            booked = db.query(func.sum(BookingItem.quantity)).join(Booking).filter(
                BookingItem.room_id == room.room_id,
                Booking.status == "confirmed",
                Booking.check_in < booking_data.check_out,
                Booking.check_out > booking_data.check_in
            ).scalar() or 0

            available = room.total_rooms - booked - locked_rooms
            
            if available <1:
                raise HTTPException(status_code=409,detail="sorry, no rooms available")

            if available < room_request.quantity:
                raise HTTPException(
                    status_code=409,
                    detail=f"Only {available} {room.room_type} rooms available"
                )

            #  Apply Locks 
            redis_client.incrby(lock_key, room_request.quantity)
            redis_client.expire(lock_key, LOCK_TIME)
            locked_keys_in_this_req.append(lock_key)

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
        db.flush()  # Generate booking_id
        
        
        #send booking email 
        user = db.query(User2).filter(User2.id==current_user.id).first()
        
        send_booking_reminder.apply_async(args=[user.email,booking.booking_id],countdown=10)

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

    except HTTPException:
        
        db.rollback()
      
        raise
    except SQLAlchemyError as e:
      
        db.rollback()
        
        for key in locked_keys_in_this_req:
            redis_client.decrby(key, room_request.quantity) 
        
        print(f"Database error: {e}") # Log the error
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your booking"
        )
    except Exception as e:
       
        db.rollback()
        print(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )



@router.patch("/{booking_id}", status_code=status.HTTP_200_OK)
def confirm_booking(
    booking_id: int,
    background_tasks : BackgroundTasks,
    db: Session = Depends(get_db), 
    current_user=Depends(get_current_user)
):
    try:
        #  Fetch Booking
        booking = db.query(Booking).filter(Booking.booking_id == booking_id).first()
        
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        #  Authorization Check
        if booking.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
            
        #  Status Validation
        if booking.status == "confirmed":
            return {"message": "Booking already confirmed"}
        
        if booking.status != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot confirm booking with status: {booking.status}. Only pending bookings can be confirmed."
            )
            
       #
        items = db.query(BookingItem).filter(BookingItem.booking_id == booking_id).all()
        
        
        for item in items:
            lock_key = f"lock:{booking.hotel_id}:{item.room_id}:{booking.check_in}:{booking.check_out}"
            if not redis_client.exists(lock_key):
              
                booking.status = "cancelled"
                db.commit()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Booking window expired. Booking automatically cancelled. Please create a new booking."
                )
                
        
        for item in items:
            lock_key = f"lock:{booking.hotel_id}:{item.room_id}:{booking.check_in}:{booking.check_out}"
        
            new_value = redis_client.decrby(lock_key, item.quantity)
            if new_value <= 0:
                redis_client.delete(lock_key)
                
       
        booking.status = "confirmed"
        db.commit()
        db.refresh(booking)
        #email sending 
        user = db.query(User).filter(User.id==booking.user_id).first()
        
        background_tasks.add_task(send_booking_confirmation_email,user.email,booking.booking_id)
        
        return {"message": "Booking confirmed", "booking_id": booking.booking_id}

    
    except SQLAlchemyError as e:
        
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred during confirmation."
        )
    except Exception as e:
      
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred."
        )




# delete booking
@router.delete("/{booking_id}")
def cancel_booking(
    booking_id: int,
    background_tasks:BackgroundTasks,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
        booking = db.query(Booking).filter(Booking.booking_id == booking_id).first()

        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        if booking.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to cancel this booking")
            
        if booking.status == "cancelled":
            return {"message": "Booking is already cancelled"}

        #  release Redis locks if the booking was still 'pending'
        if booking.status == "pending":
            items = db.query(BookingItem).filter(BookingItem.booking_id == booking_id).all()
            for item in items:
                lock_key = f"lock:{booking.hotel_id}:{item.room_id}:{booking.check_in}:{booking.check_out}"
                if redis_client.exists(lock_key):
                    new_value = redis_client.decrby(lock_key, item.quantity)
                    if new_value <= 0:
                        redis_client.delete(lock_key)

        booking.status = "cancelled"
        db.commit()
        
        #booking cancellation email 
        user = db.query(User).filter(User.id==booking.user_id).first()
        
        background_tasks.add_task(send_cancellation_email,user.email,booking.booking_id)
        
        return {"message": "Booking cancelled successfully"}

    except HTTPException as he:
        db.rollback()
        raise he
    except Exception as e:
        db.rollback()
       
        raise HTTPException(status_code=500, detail="Internal server error while cancelling booking")

# Get all bookings for current user
@router.get("/")
def get_my_bookings(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
        fixed_window_rate_limit(current_user.id,"get_my_bookings")
        bookings = db.query(Booking).filter(
            Booking.user_id == current_user.id
        ).all()
        return bookings
    except Exception as e:
        # Log the error internally here
        raise HTTPException(
            status_code=500, 
            detail="An error occurred while fetching your bookings"
        )

# Get specific booking details

@router.get("/{booking_id}") 
def get_booking_details(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
        booking = db.query(Booking).filter(
            Booking.booking_id == booking_id,
            Booking.user_id == current_user.id
        ).first()

        if not booking:
            raise HTTPException(
                status_code=404, 
                detail="Booking not found or not authorized"
            )

        # booking items and join with the Room model to get room types
        details = db.query(BookingItem, Room.room_type).join(Room).filter(
            BookingItem.booking_id == booking_id
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

    except HTTPException as he:
       
        raise he
    except Exception as e:
        # Catch unexpected database or server errors
        raise HTTPException(
            status_code=500, 
            detail="An error occurred while retrieving booking details"
        )




#for cancelling all pending bookings for tetsting propese 
@router.post("/test/cancel_all_pending")
def cancel_all_pending_bookings(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    
  
    pending_bookings = db.query(Booking).filter(
        Booking.user_id == current_user.id,
        Booking.status == "pending" 
    ).all()

    if not pending_bookings:
        return {"message": "No pending bookings to cancel"}

    total_cancelled = 0
    for booking in pending_bookings:
       
        items = db.query(BookingItem).filter(
            BookingItem.booking_id == booking.booking_id
        ).all()

        for item in items:
            lock_key = f"lock:{booking.hotel_id}:{item.room_id}:{booking.check_in}:{booking.check_out}"
            
         
            if redis_client.exists(lock_key):
                new_value = redis_client.decrby(lock_key, item.quantity)
                if new_value <= 0:
                    redis_client.delete(lock_key)
        
       
        booking.status = "cancelled"
        total_cancelled += 1

    db.commit()
    return {"message": f"Successfully cancelled {total_cancelled} pending bookings."}







#for cancelling all pending bookings for tetsting propese 
@router.post("/test/cancel_all_confirm")
def cancel_all_pending_bookings(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    
    #Find all pending bookings for the user
    pending_bookings = db.query(Booking).filter(
        Booking.user_id == current_user.id,
        Booking.status == "confirmed" 
    ).all()

    if not pending_bookings:
        return {"message": "No confirmed bookings to cancel"}

    total_cancelled = 0
    for booking in pending_bookings:
       
        items = db.query(BookingItem).filter(
            BookingItem.booking_id == booking.booking_id
        ).all()

        for item in items:
            lock_key = f"lock:{booking.hotel_id}:{item.room_id}:{booking.check_in}:{booking.check_out}"
            
           
            if redis_client.exists(lock_key):
                new_value = redis_client.decrby(lock_key, item.quantity)
                if new_value <= 0:
                    redis_client.delete(lock_key)
        
        booking.status = "cancelled"
        total_cancelled += 1

    db.commit()
    return {"message": f"Successfully cancelled {total_cancelled} confirmed bookings."}



