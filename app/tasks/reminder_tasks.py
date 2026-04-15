# from app.core.celery_app import celery_app
# from app.services.email_service import send_reminder_email
# from app.database.database import SessionLocal
# from app.models.booking import Booking

# @celery_app.task
# def send_booking_reminder(email:str,booking_id:int):
    
#     db = SessionLocal()
    
#     booking = db.query(Booking).filter(Booking.booking_id==booking_id).first()
    
#     if booking :
#         send_reminder_email(email,booking_id)
#     db.close()



from app.core.celery_app import celery
from app.services.email_service import send_reminder_email
from sqlalchemy.orm import Session
from app.core.celery_app import celery
from app.database.database import SessionLocal
from app.models.flight_models import FlightBooking
from app.models.flight_models import Flight
from app.services.notification_service import send_notification
from datetime import datetime,timedelta
from app.models.user_email import User2
from app.models.user import User

from app.models.room import Room
from app.models.booking_item import BookingItem
from app.models.room_type import RoomType
from app.models.role import Role
from app.models.permission import Permission
from app.models.hotel import Hotel
from app.models.flight_models import Flight,FlightBooking,FlightSeat,SeatAllocation,Airline,Airplane,AirplaneSeat,Airport
from app.services.email_service import send_reminder_email_flight

@celery.task
def send_booking_reminder(email:str,booking_id:int):
    send_reminder_email(email,booking_id)
    
# @celery.task   
# def check_flight_reminders():
#     print("checking flight reminders ... ")
#     db:Session = SessionLocal()
#     now = datetime.now()
#     target  = not + timedelta(minutes=10)
#     bookings = (db.query(FlightBooking)).join(Flight).filter(Flight.depart_time>=now,Flight.depart_time<=target,FlightBooking.reminder_sent.is_(False)).all()
#     user = db.query(User).filter(User.id==booking.created_by).first()
    
    
#     for booking in bookings:
#         send_notification(user.email,booking.flight.flight_number) 
#         booking.reminder_sent=True
#         db.commit()
#         db.close()
    
    
@celery.task
def check_flight_reminders():
    print("checking flight reminders ... ")
    db:Session = SessionLocal()
    try:
        now = datetime.now()
        target = now + timedelta(minutes=10)
        
        # 1. Fixed syntax: 'not' changed to 'now'
        # 2. Used .is_(False) or == False
        bookings = (db.query(FlightBooking)
                    .join(Flight)
                    .filter(
                        Flight.depart_time >= now,
                        Flight.depart_time <= target,
                        FlightBooking.reminder_sent.is_(False) # Corrected
                    ).all())

        for booking in bookings:
            # 3. Fixed: Use 'booking' from loop, not 'booking' (undefined)
            user = db.query(User).filter(User.id == booking.created_by).first()
            if user:
                send_notification(user.email, booking.flight.flight_number)
                print("user id is " , user.id)
                send_reminder_email_flight(user.email,booking.flight.flight_number)
                print("outside the email sending ")
                booking.reminder_sent = True
                db.commit()
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        # 4. Ensure session closes
        db.close()

    